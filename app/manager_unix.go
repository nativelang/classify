//go:build !windows

package main

import (
	"encoding/xml"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"syscall"
)

func lock(path string) (func(), error) {
	f, e := os.OpenFile(path, os.O_CREATE|os.O_RDWR, 0600)
	if e != nil {
		return nil, e
	}
	for {
		e = syscall.Flock(int(f.Fd()), syscall.LOCK_EX)
		if e != syscall.EINTR {
			break
		}
	}
	if e != nil {
		f.Close()
		return nil, e
	}
	return func() { f.Close() }, nil
}
func windowsStart(int) (string, error) { return "", errors.New("Windows only") }
func label(i instance) string          { return "org.nativelang.classify." + i.ID }
func domain() string                   { return fmt.Sprintf("gui/%d", os.Getuid()) }
func escape(s string) string           { var b strings.Builder; xml.EscapeText(&b, []byte(s)); return b.String() }
func register(s service, i instance, exe string) error {
	name := label(i)
	if runtime.GOOS == "linux" {
		_, e := managerCommand(nil, "systemd-run", "--user", "--collect", "--unit="+name, "--property=TimeoutStopSec=5s", "--", exe, "daemon", i.ID)
		return e
	}
	// Keep the plist outside LaunchAgents: the service starts only on demand.
	plist := `<?xml version="1.0"?><plist version="1.0"><dict><key>Label</key><string>` + name + `</string><key>ProgramArguments</key><array><string>` + escape(exe) + `</string><string>daemon</string><string>` + i.ID + `</string></array><key>RunAtLoad</key><true/><key>ExitTimeOut</key><integer>5</integer></dict></plist>`
	path := s.path(name + ".plist")
	if e := atomicFile(path, []byte(plist)); e != nil {
		return e
	}
	_, e := managerCommand(nil, "/bin/launchctl", "bootstrap", domain(), path)
	return e
}
func managerOwns(s service, i instance, pid int) bool {
	if runtime.GOOS == "linux" {
		v, e := managerCommand(nil, "systemctl", "--user", "show", "--property=MainPID", "--value", label(i)+".service")
		return e == nil && v == strconv.Itoa(pid)
	}
	v, e := managerCommand(nil, "/bin/launchctl", "print", domain()+"/"+label(i))
	if e != nil {
		return false
	}
	for _, line := range strings.Split(v, "\n") {
		if strings.TrimSpace(line) == fmt.Sprintf("pid = %d", pid) {
			return true
		}
	}
	return false
}
func unregister(s service, i instance) error {
	name := label(i)
	if runtime.GOOS == "linux" {
		_, e := managerCommand(nil, "systemctl", "--user", "stop", name+".service")
		if e != nil && !strings.Contains(e.Error(), "not loaded") && !strings.Contains(e.Error(), "not found") {
			return e
		}
		return nil
	}
	_, e := managerCommand(nil, "/bin/launchctl", "bootout", domain()+"/"+name)
	if e != nil && !strings.Contains(e.Error(), "No such process") && !strings.Contains(e.Error(), "Could not find service") {
		return e
	}
	e = os.Remove(filepath.Join(s.dir, name+".plist"))
	if os.IsNotExist(e) {
		return nil
	}
	return e
}
func confine() error { return nil }

func privateDir(path string) error {
	if e := os.MkdirAll(path, 0700); e != nil {
		return e
	}
	return os.Chmod(path, 0700)
}
