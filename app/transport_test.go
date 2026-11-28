package main

import (
	"crypto/tls"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func TestAuthenticateBeforeSending(t *testing.T) {
	cert, pin, err := certificate()
	if err != nil {
		t.Fatal(err)
	}
	var received atomic.Int32
	i := instance{secret(16), 0, secret(32)}
	srv := httptest.NewUnstartedServer(authenticated(i.Token, http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { received.Add(1); io.WriteString(w, "ok") })))
	srv.TLS = &tls.Config{Certificates: []tls.Certificate{cert}, MinVersion: tls.VersionTLS13}
	srv.StartTLS()
	defer srv.Close()
	r := record{ID: i.ID, Address: srv.Listener.Addr().String(), Fingerprint: strings.Repeat("0", 64)}
	if _, err := call(r, i, "/v1/classify", []byte("{}"), time.Second); err == nil || received.Load() != 0 {
		t.Fatal("sent request to an unverified peer")
	}
	r.Fingerprint = pin
	wrong := i
	wrong.Token = secret(32)
	if _, err := call(r, wrong, "/health", nil, time.Second); err == nil || received.Load() != 0 {
		t.Fatal("accepted an unauthenticated caller")
	}
	if _, err := call(r, i, "/health", nil, time.Second); err != nil || received.Load() != 1 {
		t.Fatal(err)
	}
}
func TestPortAndIdle(t *testing.T) {
	t.Setenv("NATIVELANG_CLASSIFY_PORT", "65536")
	if _, e := requestedPort(); e == nil {
		t.Fatal("accepted invalid port")
	}
	m := newModel(service{t.TempDir()}, secret(16))
	m.last = time.Now().Add(-2 * idleLimit)
	if m.idle() {
		t.Fatal("stopped during startup")
	}
	m.st.Phase = "ready"
	m.active = 1
	if m.idle() {
		t.Fatal("stopped with pending work")
	}
	m.active = 0
	if !m.idle() {
		t.Fatal("stayed warm after idle deadline")
	}
}
func TestPortConflictPreservesOwner(t *testing.T) {
	s := service{t.TempDir()}
	foreign := httptest.NewServer(http.NotFoundHandler())
	defer foreign.Close()
	i := instance{secret(16), foreign.Listener.Addr().(*net.TCPAddr).Port, secret(32)}
	if e := save(s.path("instance.json"), i); e != nil {
		t.Fatal(e)
	}
	if e := s.serve(i.ID); e == nil || !strings.Contains(e.Error(), "Unset NATIVELANG_CLASSIFY_PORT") {
		t.Fatal(e)
	}
	if _, e := os.Stat(filepath.Join(s.dir, "endpoint.json")); !os.IsNotExist(e) {
		t.Fatal("claimed foreign endpoint")
	}
}

func TestColdRegistrationIsSharedBeforeTLSIsReady(t *testing.T) {
	s := service{t.TempDir()}
	i := instance{secret(16), 0, secret(32)}
	if err := save(s.path("instance.json"), i); err != nil {
		t.Fatal(err)
	}
	cold := time.Now().Add(-time.Minute)
	if err := os.Chtimes(s.path("instance.json"), cold, cold); err != nil {
		t.Fatal(err)
	}
	selected, err := s.selectInstance(0, nil, "")
	if err != nil || selected.ID != i.ID {
		t.Fatalf("replaced cold registration: %v", err)
	}
	r := record{ID: i.ID, Address: "127.0.0.1:1", PID: os.Getpid(), Fingerprint: secret(32)}
	if err := save(s.path("endpoint.json"), r); err != nil {
		t.Fatal(err)
	}
	selected, err = s.selectInstance(0, nil, "")
	if err != nil || selected.ID != i.ID {
		t.Fatalf("replaced starting listener: %v", err)
	}
}
