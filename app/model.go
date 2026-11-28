package main

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

type model struct {
	s      service
	id     string
	mu     sync.Mutex
	st     status
	active int
	last   time.Time
	lane   chan struct{}
	cmd    *exec.Cmd
	in     io.WriteCloser
	out    *bufio.Scanner
}

func newModel(s service, id string) *model {
	return &model{s: s, id: id, st: status{Phase: "downloading"}, last: time.Now(), lane: make(chan struct{}, 1)}
}
func (m *model) snapshot() status {
	m.mu.Lock()
	st := m.st
	m.mu.Unlock()
	if st.Phase == "downloading" {
		for _, name := range []string{"package.tar.gz", "server.zip"} {
			paths, _ := filepath.Glob(filepath.Join(filepath.Dir(m.s.dir), "v*", ".*.partial", name))
			for _, p := range paths {
				if f, e := os.Stat(p); e == nil {
					st.Bytes += f.Size()
				}
			}
		}
	}
	return st
}
func (m *model) idle() bool {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.active == 0 && m.st.Phase == "ready" && time.Since(m.last) > idleLimit
}
func (m *model) phase(name, msg string) {
	m.mu.Lock()
	m.st.Phase = name
	m.st.Message = msg
	m.last = time.Now()
	m.mu.Unlock()
	m.s.log(name + " " + msg)
}
func (m *model) exchange(data []byte) ([]byte, error) {
	if _, e := fmt.Fprintln(m.in, string(data)); e != nil {
		return nil, e
	}
	if !m.out.Scan() {
		return nil, errors.New("native worker stopped")
	}
	b := append([]byte(nil), m.out.Bytes()...)
	if !json.Valid(b) {
		return nil, errors.New("invalid native worker result")
	}
	return b, nil
}
func (m *model) load(ctx context.Context) {
	exe, e := m.s.native(ctx)
	if e != nil {
		m.phase("failed", "native runtime installation failed: "+e.Error())
		return
	}
	m.phase("loading", "")
	begin := time.Now()
	cmd := workerCommand(ctx, exe)
	in, e := cmd.StdinPipe()
	if e != nil {
		m.phase("failed", e.Error())
		return
	}
	out, e := cmd.StdoutPipe()
	if e != nil {
		m.phase("failed", e.Error())
		return
	}
	// The runtime writes hardware selection at startup. Log only those known diagnostic lines.
	stderr, e := cmd.StderrPipe()
	if e != nil {
		m.phase("failed", e.Error())
		return
	}
	if e = cmd.Start(); e != nil {
		m.phase("failed", e.Error())
		return
	}
	defer cmd.Wait()
	defer cmd.Process.Kill()
	go func() {
		lines := bufio.NewScanner(stderr)
		for lines.Scan() {
			line := lines.Text()
			if len(line) < 150 && (strings.HasPrefix(line, "Classify CPU backend:") || strings.HasPrefix(line, "Classify inference device:")) {
				m.s.log(line)
			}
		}
	}()
	m.cmd = cmd
	m.in = in
	m.out = scanLines(out)
	// The runtime opens the model before reading stdin. A validation error witnesses readiness.
	timer := time.AfterFunc(stallLimit, func() { cmd.Process.Kill() })
	reply, e := m.exchange([]byte("{}"))
	timer.Stop()
	var ready struct{ Error struct{ Code string } }
	if e != nil || json.Unmarshal(reply, &ready) != nil || ready.Error.Code != "invalid_argument" {
		m.phase("failed", "model did not become ready")
		return
	}
	m.mu.Lock()
	m.st.LoadMS = time.Since(begin).Milliseconds()
	m.mu.Unlock()
	if err := save(m.s.path("ready.json"), m.id); err != nil {
		m.phase("failed", err.Error())
		return
	}
	m.phase("ready", "")
	m.lane <- struct{}{}
	<-ctx.Done()
}
func (m *model) classify(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	if m.snapshot().Phase != "ready" {
		http.Error(w, "service is not ready", 503)
		return
	}
	data, e := io.ReadAll(http.MaxBytesReader(w, r.Body, maxRequest))
	if e != nil {
		http.Error(w, "request too large", 413)
		return
	}
	// Compact a JSON document to preserve the native worker's one-line request framing.
	var raw json.RawMessage = data
	line, e := json.Marshal(raw)
	if e != nil {
		w.WriteHeader(400)
		io.WriteString(w, `{"error":{"code":"invalid_argument","message":"Invalid JSON"}}`)
		return
	}
	m.mu.Lock()
	m.active++
	m.mu.Unlock()
	defer func() { m.mu.Lock(); m.active--; m.last = time.Now(); m.mu.Unlock() }()
	select {
	case <-r.Context().Done():
		return
	case <-m.lane:
	}
	defer func() { m.lane <- struct{}{} }()
	if m.snapshot().Phase != "ready" {
		http.Error(w, "worker is unavailable", 503)
		return
	}
	start := time.Now()
	timer := time.AfterFunc(stallLimit, func() { m.cmd.Process.Kill() })
	reply, e := m.exchange(line)
	timer.Stop()
	var result map[string]json.RawMessage
	if e == nil {
		e = json.Unmarshal(reply, &result)
	}
	m.mu.Lock()
	m.st.Requests++
	m.st.InferenceMS += time.Since(start).Milliseconds()
	if e != nil || result["error"] != nil {
		m.st.Errors++
	}
	m.mu.Unlock()
	if e != nil {
		m.phase("failed", "native worker did not reply")
		http.Error(w, "native worker did not reply", 503)
		return
	}
	if result["error"] != nil {
		var detail struct{ Code string }
		json.Unmarshal(result["error"], &detail)
		if detail.Code == "invalid_argument" {
			w.WriteHeader(http.StatusBadRequest)
		} else {
			w.WriteHeader(http.StatusServiceUnavailable)
		}
		w.Write(reply)
		return
	}
	result["source"] = json.RawMessage(`"self_hosted"`)
	json.NewEncoder(w).Encode(result)
}
