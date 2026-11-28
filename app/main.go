// Classify manages the per-user service and bridges the native JSON Lines protocol.
package main

import (
	"bufio"
	"context"
	"crypto/rand"
	_ "embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

//go:embed native-bootstrap.sh
var nativeSH string

//go:embed native-install.ps1
var nativePS []byte

const maxRequest = 10 << 20
const idleLimit = 15 * time.Minute
const stallLimit = 3 * time.Minute

type instance struct {
	ID    string `json:"instance"`
	Port  int    `json:"requested_port"`
	Token string `json:"token"`
}
type record struct {
	ID          string `json:"instance"`
	Address     string `json:"address"`
	PID         int    `json:"pid"`
	Started     string `json:"process_start"`
	Fingerprint string `json:"certificate_sha256"`
}
type status struct {
	Phase       string `json:"phase"`
	Message     string `json:"message,omitempty"`
	Bytes       int64  `json:"download_bytes,omitempty"`
	Requests    int64  `json:"requests"`
	Errors      int64  `json:"errors"`
	InferenceMS int64  `json:"total_inference_ms"`
	LoadMS      int64  `json:"model_load_ms"`
}
type service struct{ dir string }

func secret(n int) string {
	b := make([]byte, n)
	if _, err := rand.Read(b); err != nil {
		panic(err)
	}
	return hex.EncodeToString(b)
}
func (s service) path(name string) string { return filepath.Join(s.dir, name) }
func save(path string, value any) error {
	b, err := json.Marshal(value)
	if err != nil {
		return err
	}
	return atomicFile(path, append(b, '\n'))
}
func atomicFile(path string, data []byte) error {
	f, err := os.CreateTemp(filepath.Dir(path), ".write-*")
	if err != nil {
		return err
	}
	defer os.Remove(f.Name())
	_, err = f.Write(data)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	if closeErr != nil {
		return closeErr
	}
	return os.Rename(f.Name(), path)
}
func (s service) read(name string, value any) error {
	b, e := os.ReadFile(s.path(name))
	if e != nil {
		return e
	}
	return json.Unmarshal(b, value)
}
func (s service) log(msg string) {
	f, e := os.OpenFile(s.path("service.log"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if e == nil {
		fmt.Fprintf(f, "%s %s\n", time.Now().UTC().Format(time.RFC3339), msg)
		f.Close()
	}
}
func (s service) native(ctx context.Context) (string, error) {
	var cmd *exec.Cmd
	if runtime.GOOS == "windows" {
		path := s.path("native-install.ps1")
		if err := atomicFile(path, nativePS); err != nil {
			return "", err
		}
		cmd = exec.CommandContext(ctx, powershell(), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", path)
	} else {
		cmd = exec.CommandContext(ctx, "/bin/sh", "-c", nativeSH, "classify", "--locate")
	}
	// Installers emit progress and download failures on stderr, never requests.
	// OS-managed jobs have no attached terminal.
	diagnostics, err := os.OpenFile(s.path("service.log"), os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0600)
	if err != nil {
		return "", err
	}
	defer diagnostics.Close()
	cmd.Stderr = diagnostics
	b, e := cmd.Output()
	return strings.TrimSpace(string(b)), e
}
func powershell() string {
	return filepath.Join(os.Getenv("SystemRoot"), "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
}
func workerCommand(ctx context.Context, exe string) *exec.Cmd {
	return exec.CommandContext(ctx, exe, "infer", "--profile", filepath.Join(filepath.Dir(exe), "model", "profile.json"))
}
func (s service) direct() error {
	exe, e := s.native(context.Background())
	if e != nil {
		return e
	}
	cmd := workerCommand(context.Background(), exe)
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}
func requestedPort() (int, error) {
	v, ok := os.LookupEnv("NATIVELANG_CLASSIFY_PORT")
	if !ok {
		return 0, nil
	}
	n, e := strconv.Atoi(v)
	if e != nil || n < 1 || n > 65535 {
		return 0, errors.New("NATIVELANG_CLASSIFY_PORT must be an integer from 1 to 65535")
	}
	return n, nil
}
func (s service) report() error {
	var r record
	var i instance
	if s.read("instance.json", &i) == nil && s.read("endpoint.json", &r) == nil && r.ID == i.ID {
		st, e := probe(r, i)
		if e == nil {
			return json.NewEncoder(os.Stdout).Encode(struct {
				record
				status
			}{r, st})
		}
		if owned(s, i, r) {
			return fmt.Errorf("Classify PID %d is unresponsive; see classify service logs", r.PID)
		}
	}
	var fallback string
	if s.read("fallback.json", &fallback) == nil {
		fmt.Println("stopped: " + fallback)
		return nil
	}
	fmt.Println("stopped")
	return nil
}
func run(args []string) error {
	home, e := os.UserHomeDir()
	if e != nil {
		return e
	}
	s := service{filepath.Join(home, ".nativelang", "classify", "service")}
	if e = privateDir(s.dir); e != nil {
		return e
	}
	if len(args) > 0 && args[0] == "infer" {
		return s.bridge()
	}
	if len(args) == 2 && args[0] == "daemon" {
		id := args[1]
		if !validID(id) {
			return errors.New("invalid instance")
		}
		e := confine()
		if e == nil {
			e = s.serve(id)
		}
		if e != nil {
			s.log(e.Error())
			save(s.path("startup-error.json"), startFailure{id, e.Error()})
		}
		return e
	}
	if len(args) != 2 || args[0] != "service" {
		return errors.New("usage: classify service start|stop|status|logs")
	}
	switch args[1] {
	case "start":
		_, _, e := s.ensure(nil)
		if e != nil {
			return e
		}
		return s.report()
	case "stop":
		unlock, e := lock(s.path("control.lock"))
		if e != nil {
			return e
		}
		defer unlock()
		return s.stop()
	case "status":
		return s.report()
	case "logs":
		f, e := os.Open(s.path("service.log"))
		if os.IsNotExist(e) {
			return nil
		}
		if e != nil {
			return e
		}
		defer f.Close()
		_, e = io.Copy(os.Stdout, f)
		return e
	}
	return errors.New("unknown service command")
}
func main() {
	if err := run(os.Args[1:]); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func scanLines(r io.Reader) *bufio.Scanner {
	s := bufio.NewScanner(r)
	s.Buffer(make([]byte, 4096), maxRequest+1)
	return s
}
func validAddress(address string) bool {
	host, p, e := net.SplitHostPort(address)
	n, err := strconv.Atoi(p)
	return e == nil && err == nil && host == "127.0.0.1" && n > 0 && n <= 65535
}
