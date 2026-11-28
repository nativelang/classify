package main

import (
	"context"
	"errors"
	"fmt"

	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

var errManager = errors.New("user service manager unavailable")

func managerCommand(extra []string, name string, args ...string) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	cmd := exec.CommandContext(ctx, name, args...)
	cmd.Env = append(os.Environ(), extra...)
	b, e := cmd.CombinedOutput()
	if e != nil {
		return "", fmt.Errorf("%s: %w: %s", filepath.Base(name), e, cleanOutput(b))
	}
	return cleanOutput(b), nil
}
func (s service) stop() error {
	var i instance
	e := s.read("instance.json", &i)
	if os.IsNotExist(e) {
		return nil
	}
	if e != nil {
		return e
	}
	if !validID(i.ID) {
		return errors.New("invalid Classify service registration")
	}
	var r record
	if s.read("endpoint.json", &r) == nil && r.ID == i.ID && !owned(s, i, r) {
		// A dead process is an ordinary stale endpoint. A live matching process without
		// manager ownership is ambiguous; never signal it or start a duplicate.
		if t, e := processStart(r.PID); e == nil && t == r.Started {
			return errors.New("cannot verify OS ownership of the recorded Classify process")
		}
	}
	if e = unregister(s, i); e != nil {
		return e
	}
	for _, p := range []string{"endpoint.json", "instance.json", "startup-error.json"} {
		if e = os.Remove(s.path(p)); e != nil && !os.IsNotExist(e) {
			return e
		}
	}
	return nil
}
func owned(s service, i instance, r record) bool {
	if r.ID != i.ID || r.PID <= 0 {
		return false
	}
	t, e := processStart(r.PID)
	return e == nil && t == r.Started && managerOwns(s, i, r.PID)
}
func (s service) ensure(previous *record) (record, instance, error) {
	var r record
	var i instance
	port, e := requestedPort()
	if e != nil {
		return r, i, e
	}
	unlock, e := lock(s.path("control.lock"))
	if e != nil {
		return r, i, e
	}
	defer unlock()
	e = s.read("instance.json", &i)
	if e == nil {
		if !validID(i.ID) {
			return r, i, errors.New("invalid Classify service registration")
		}
		if s.read("endpoint.json", &r) == nil && r.ID == i.ID {
			st, err := probe(r, i)
			if err == nil && st.Phase == "ready" {
				if port != 0 && !strings.HasSuffix(r.Address, ":"+strconv.Itoa(port)) {
					return r, i, fmt.Errorf("Classify already runs at %s; unset NATIVELANG_CLASSIFY_PORT or stop the service before changing ports", r.Address)
				}
				return r, i, nil
			}
			if err == nil && (st.Phase == "loading" || st.Phase == "downloading") {
				return s.waitReady(i)
			}
			if previous != nil && previous.ID != i.ID {
				return r, i, errors.New("replacement service did not respond; see classify service logs")
			}
		}
		if e = s.stop(); e != nil {
			return r, i, e
		}
	} else if !os.IsNotExist(e) {
		return r, i, e
	}
	i = instance{secret(16), port, secret(32)}
	exe, e := os.Executable()
	if e != nil {
		return r, i, e
	}
	if e = save(s.path("instance.json"), i); e != nil {
		return r, i, e
	}
	if e = register(s, i, exe); e != nil {
		// A supervisor can report a command error after creating the job. Clean up
		// our unique registration before allowing per-process fallback.
		if cleanup := unregister(s, i); cleanup != nil {
			s.log("registration cleanup: " + cleanup.Error())
		}
		os.Remove(s.path("instance.json"))
		return r, i, fmt.Errorf("%w: %v", errManager, e)
	}
	return s.waitReady(i)
}

type startFailure struct{ ID, Message string }

func (s service) waitReady(i instance) (record, instance, error) {
	var r record
	var progress string
	last := time.Now()
	for time.Since(last) < stallLimit+10*time.Second {
		var f startFailure
		if s.read("startup-error.json", &f) == nil && f.ID == i.ID {
			return r, i, errors.New(f.Message)
		}
		if s.read("endpoint.json", &r) == nil && r.ID == i.ID {
			st, e := probe(r, i)
			if e == nil {
				if st.Phase == "ready" {
					return r, i, nil
				}
				if st.Phase == "failed" {
					return r, i, errors.New(st.Message + "; see classify service logs")
				}
				p := fmt.Sprintf("%s/%d", st.Phase, st.Bytes)
				if p != progress {
					last = time.Now()
					progress = p
				}
			}
		}
		time.Sleep(200 * time.Millisecond)
	}
	return r, i, errors.New("Classify startup stopped making progress; see classify service logs")
}
func processStart(pid int) (string, error) {
	if pid <= 0 {
		return "", errors.New("invalid PID")
	}
	if runtime.GOOS == "windows" {
		return windowsStart(pid)
	}
	return managerCommand([]string{"LC_ALL=C", "TZ=UTC"}, "/bin/ps", "-p", strconv.Itoa(pid), "-o", "lstart=")
}
