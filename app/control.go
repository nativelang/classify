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

var errStalled = errors.New("Classify startup stopped making progress")

// Hold the control lock only for registration changes. Status and stop stay
// usable during a first download, and every waiting client observes the same job.
func (s service) ensure(previous *record) (record, instance, error) {
	port, err := requestedPort()
	if err != nil {
		return record{}, instance{}, err
	}
	var stalled string
	for attempt := 0; attempt < 2; attempt++ {
		i, err := s.selectInstance(port, previous, stalled)
		if err != nil {
			return record{}, i, err
		}
		r, _, err := s.waitReady(i)
		if err == nil && port != 0 && !strings.HasSuffix(r.Address, ":"+strconv.Itoa(port)) {
			return r, i, fmt.Errorf("Classify already runs at %s; unset NATIVELANG_CLASSIFY_PORT or stop the service before changing ports", r.Address)
		}
		if !errors.Is(err, errStalled) || attempt == 1 {
			return r, i, err
		}
		stalled = i.ID
	}
	return record{}, instance{}, errStalled
}

func (s service) selectInstance(port int, previous *record, stalled string) (instance, error) {
	var i instance
	unlock, err := lock(s.path("control.lock"))
	if err != nil {
		return i, err
	}
	defer unlock()
	err = s.read("instance.json", &i)
	if err == nil {
		if !validID(i.ID) {
			return i, errors.New("invalid Classify service registration")
		}
		var r record
		if s.read("endpoint.json", &r) == nil && r.ID == i.ID {
			st, err := probe(r, i)
			if err == nil && (st.Phase == "ready" || (i.ID != stalled && (st.Phase == "loading" || st.Phase == "downloading"))) {
				return i, nil
			}
			if previous != nil && previous.ID != i.ID {
				return i, errors.New("replacement service did not respond; see classify service logs")
			}
		} else if i.ID != stalled {
			var f startFailure
			if s.read("startup-error.json", &f) != nil || f.ID != i.ID {
				// Registration was committed before starting the OS job.
				if info, e := os.Stat(s.path("instance.json")); e == nil && time.Since(info.ModTime()) < 30*time.Second {
					return i, nil
				}
			}
		}
		if err = s.stop(); err != nil {
			return i, err
		}
	} else if !os.IsNotExist(err) {
		return i, err
	}
	i = instance{secret(16), port, secret(32)}
	exe, err := os.Executable()
	if err != nil {
		return i, err
	}
	if err = save(s.path("instance.json"), i); err != nil {
		return i, err
	}
	if err = register(s, i, exe); err != nil {
		if cleanup := unregister(s, i); cleanup != nil {
			s.log("registration cleanup: " + cleanup.Error())
		}
		os.Remove(s.path("instance.json"))
		return i, fmt.Errorf("%w: %v", errManager, err)
	}
	return i, nil
}

type startFailure struct{ ID, Message string }

func (s service) waitReady(i instance) (record, instance, error) {
	var r record
	var progress string
	last := time.Now()
	for time.Since(last) < stallLimit+10*time.Second {
		var current instance
		if e := s.read("instance.json", &current); e != nil || current.ID != i.ID {
			return r, i, errors.New("service stopped or replaced during startup")
		}
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
	return r, i, fmt.Errorf("%w; see classify service logs", errStalled)
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
