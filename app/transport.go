package main

import (
	"bytes"
	"context"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"crypto/tls"
	"crypto/x509"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"math/big"
	"net"
	"net/http"
	"os"
	"strings"
	"time"
)

func certificate() (tls.Certificate, string, error) {
	key, e := ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	if e != nil {
		return tls.Certificate{}, "", e
	}
	now := time.Now()
	t := &x509.Certificate{SerialNumber: big.NewInt(now.UnixNano()), NotBefore: now.Add(-time.Minute), NotAfter: now.AddDate(1, 0, 0), KeyUsage: x509.KeyUsageDigitalSignature}
	der, e := x509.CreateCertificate(rand.Reader, t, t, &key.PublicKey, key)
	sum := sha256.Sum256(der)
	return tls.Certificate{Certificate: [][]byte{der}, PrivateKey: key}, hex.EncodeToString(sum[:]), e
}

// Authenticate the peer during the handshake, before sending credentials or application data.
func call(r record, i instance, path string, body []byte, timeout time.Duration) ([]byte, error) {
	if r.ID != i.ID || !validAddress(r.Address) || len(r.Fingerprint) != 64 || len(i.Token) != 64 {
		return nil, errors.New("invalid Classify endpoint record")
	}
	cfg := &tls.Config{MinVersion: tls.VersionTLS13, InsecureSkipVerify: true, VerifyConnection: func(c tls.ConnectionState) error {
		if len(c.PeerCertificates) == 1 {
			sum := sha256.Sum256(c.PeerCertificates[0].Raw)
			if subtle.ConstantTimeCompare([]byte(hex.EncodeToString(sum[:])), []byte(r.Fingerprint)) == 1 {
				return nil
			}
		}
		return errors.New("Classify service identity changed")
	}}
	transport := &http.Transport{TLSClientConfig: cfg, DisableKeepAlives: true, DialContext: (&net.Dialer{Timeout: time.Second}).DialContext}
	client := http.Client{Transport: transport, Timeout: timeout, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
	method := http.MethodGet
	if body != nil {
		method = http.MethodPost
	}
	req, e := http.NewRequest(method, "https://"+r.Address+path, bytes.NewReader(body))
	if e != nil {
		return nil, e
	}
	req.Header.Set("Authorization", "Bearer "+i.Token)
	req.Header.Set("Content-Type", "application/json")
	resp, e := client.Do(req)
	if e != nil {
		return nil, e
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 && !(path == "/v1/classify" && resp.StatusCode == 400) {
		return nil, fmt.Errorf("Classify returned HTTP %d", resp.StatusCode)
	}
	return io.ReadAll(io.LimitReader(resp.Body, maxRequest+1))
}
func probe(r record, i instance) (status, error) {
	var st status
	b, e := call(r, i, "/health", nil, 2*time.Second)
	if e == nil {
		e = json.Unmarshal(b, &st)
	}
	return st, e
}
func failure(msg string) []byte {
	b, _ := json.Marshal(map[string]any{"error": map[string]string{"code": "unavailable", "message": msg}})
	return b
}

func (s service) bridge() error {
	r, i, e := s.ensure(nil)
	if errors.Is(e, errManager) {
		reason := "OS manager unavailable; using the per-process runtime: " + e.Error()
		s.log(reason)
		if err := save(s.path("fallback.json"), reason); err != nil {
			return err
		}
		return s.direct()
	}
	if e != nil {
		return e
	}
	scanner := scanLines(os.Stdin)
	for scanner.Scan() {
		reply, err := call(r, i, "/v1/classify", scanner.Bytes(), stallLimit+15*time.Second)
		if err != nil {
			// Classification has no side effects. Retry once after coordinating recovery.
			old := r
			r, i, err = s.ensure(&old)
			if err == nil {
				reply, err = call(r, i, "/v1/classify", scanner.Bytes(), stallLimit+15*time.Second)
			}
			if err != nil {
				reply = failure(err.Error())
			}
		}
		if _, err := fmt.Fprintln(os.Stdout, string(reply)); err != nil {
			return err
		}
	}
	return scanner.Err()
}
func authenticated(token string, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if subtle.ConstantTimeCompare([]byte(r.Header.Get("Authorization")), []byte("Bearer "+token)) != 1 {
			http.Error(w, "unauthorized", 401)
			return
		}
		next.ServeHTTP(w, r)
	})
}
func (s service) serve(id string) error {
	var i instance
	if e := s.read("instance.json", &i); e != nil {
		return e
	}
	if !validID(id) || i.ID != id {
		return errors.New("obsolete service registration")
	}
	started, e := processStart(os.Getpid())
	if e != nil {
		return e
	}
	listen, e := net.Listen("tcp4", fmt.Sprintf("127.0.0.1:%d", i.Port))
	if e != nil {
		return fmt.Errorf("cannot bind port %d: %w. Unset NATIVELANG_CLASSIFY_PORT to choose an available port", i.Port, e)
	}
	defer listen.Close()
	cert, pin, e := certificate()
	if e != nil {
		return e
	}
	r := record{id, listen.Addr().String(), os.Getpid(), started, pin}
	if e = save(s.path("endpoint.json"), r); e != nil {
		return e
	}
	os.Remove(s.path("fallback.json"))
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	model := newModel(s)
	go model.load(ctx)
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(model.snapshot())
	})
	mux.HandleFunc("POST /v1/classify", model.classify)
	server := http.Server{Handler: authenticated(i.Token, mux), ReadTimeout: 15 * time.Second, WriteTimeout: stallLimit + 10*time.Second, IdleTimeout: 10 * time.Second, MaxHeaderBytes: 8192}
	go func() {
		ticker := time.NewTicker(time.Second)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				if model.idle() {
					s.log("idle shutdown")
					server.Close()
					return
				}
			}
		}
	}()
	s.log("listening on " + r.Address)
	e = server.Serve(tls.NewListener(listen, &tls.Config{MinVersion: tls.VersionTLS13, Certificates: []tls.Certificate{cert}}))
	if errors.Is(e, http.ErrServerClosed) {
		return nil
	}
	return e
}
func validID(id string) bool      { _, err := hex.DecodeString(id); return len(id) == 32 && err == nil }
func cleanOutput(b []byte) string { return strings.TrimSpace(string(b)) }
