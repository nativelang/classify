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
func processStart(pid int) (string, error) {
	if pid <= 0 {
		return "", errors.New("invalid PID")
	}
	if runtime.GOOS == "linux" {
		// /proc/PID/stat field 22 is the immutable start tick within a boot.
		// The command name in field 2 may itself contain spaces and parentheses.
		data, err := os.ReadFile(fmt.Sprintf("/proc/%d/stat", pid))
		if err != nil {
			return "", err
		}
		end := strings.LastIndex(string(data), ")")
		if end < 0 {
			return "", errors.New("invalid process record")
		}
		fields := strings.Fields(string(data[end+1:]))
		if len(fields) < 20 || fields[0] == "Z" {
			return "", errors.New("process unavailable")
		}
		boot, err := os.ReadFile("/proc/sys/kernel/random/boot_id")
		if err != nil {
			return "", err
		}
		return strings.TrimSpace(string(boot)) + ":" + fields[19], nil
	}
	return managerCommand([]string{"LC_ALL=C", "TZ=UTC"}, "/bin/ps", "-p", strconv.Itoa(pid), "-o", "lstart=")
}
func label(i instance) string { return "org.nativelang.classify." + i.ID }
func domain() string          { return fmt.Sprintf("gui/%d", os.Getuid()) }
func escape(s string) string {
	var b strings.Builder
	xml.EscapeText(&b, []byte(s))
	return b.String()
}
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
