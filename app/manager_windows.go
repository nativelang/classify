package main

import (
	"errors"
	"fmt"
	"os"
	"strconv"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

var kernel = syscall.NewLazyDLL("kernel32.dll")

func lock(path string) (func(), error) {
	p, e := syscall.UTF16PtrFromString(path)
	if e != nil {
		return nil, e
	}
	for {
		h, e := syscall.CreateFile(p, syscall.GENERIC_READ|syscall.GENERIC_WRITE, 0, nil, syscall.OPEN_ALWAYS, syscall.FILE_ATTRIBUTE_NORMAL, 0)
		if e == nil {
			return func() { syscall.CloseHandle(h) }, nil
		}
		if !errors.Is(e, syscall.Errno(32)) {
			return nil, e
		}
		time.Sleep(100 * time.Millisecond)
	}
}
func windowsStart(pid int) (string, error) {
	h, e := syscall.OpenProcess(0x1000, false, uint32(pid))
	if e != nil {
		return "", e
	}
	defer syscall.CloseHandle(h)
	var start, exit, k, u syscall.Filetime
	e = syscall.GetProcessTimes(h, &start, &exit, &k, &u)
	if e != nil {
		return "", e
	}
	return strconv.FormatUint(uint64(start.HighDateTime)<<32|uint64(start.LowDateTime), 10), nil
}

const scheduler = `$ErrorActionPreference='Stop';$ts=New-Object -ComObject Schedule.Service;$ts.Connect();$folder=$ts.GetFolder('\');$name='NativeLang.Classify.'+$env:CLASSIFY_INSTANCE;`

func task(i instance, exe, script string) (string, error) {
	return managerCommand([]string{"CLASSIFY_INSTANCE=" + i.ID, "CLASSIFY_EXECUTABLE=" + exe}, powershell(), "-NoProfile", "-NonInteractive", "-Command", scheduler+script)
}
func register(s service, i instance, exe string) error {
	_, e := task(i, exe, `$d=$ts.NewTask(0);$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value;$d.Principal.UserId=$sid;$d.Principal.LogonType=3;$d.Principal.RunLevel=0;$d.Settings.ExecutionTimeLimit='PT0S';$d.Settings.DisallowStartIfOnBatteries=$false;$d.Settings.StopIfGoingOnBatteries=$false;$a=$d.Actions.Create(0);$a.Path=$env:CLASSIFY_EXECUTABLE;$a.Arguments='daemon '+$env:CLASSIFY_INSTANCE;$t=$folder.RegisterTaskDefinition($name,$d,2,$sid,$null,3,$null);[void]$t.Run($null)`)
	return e
}
func managerOwns(s service, i instance, pid int) bool {
	v, e := task(i, "", fmt.Sprintf(`$t=$folder.GetTask($name);$action=$t.Definition.Actions.Item(1);$p=Get-CimInstance Win32_Process -Filter 'ProcessId=%d';if($t.State -eq 4 -and $p.ExecutablePath -eq $action.Path -and $p.CommandLine.EndsWith('daemon '+$env:CLASSIFY_INSTANCE)){Write-Output owned}`, pid))
	return e == nil && strings.TrimSpace(v) == "owned"
}
func unregister(s service, i instance) error {
	_, e := task(i, "", `try{$t=$folder.GetTask($name)}catch{if(($_.Exception.HResult -band 65535) -eq 2){return};throw};$t.Stop(0);$folder.DeleteTask($name,0)`)
	return e
}

// Keep the native model worker within a job so a stopped scheduled task also
// releases a stalled worker and its model memory. Windows supports nested jobs.
func confine() error {
	h, _, e := kernel.NewProc("CreateJobObjectW").Call(0, 0)
	if h == 0 {
		return e
	}
	// JOBOBJECT_EXTENDED_LIMIT_INFORMATION on the supported 64-bit architectures.
	var info [144]byte
	*(*uint32)(unsafe.Pointer(&info[16])) = 0x2000
	ok, _, e := kernel.NewProc("SetInformationJobObject").Call(h, 9, uintptr(unsafe.Pointer(&info[0])), uintptr(len(info)))
	if ok == 0 {
		return e
	}
	proc, _, _ := kernel.NewProc("GetCurrentProcess").Call()
	ok, _, e = kernel.NewProc("AssignProcessToJobObject").Call(h, proc)
	if ok == 0 {
		return e
	}
	// The kernel closes this non-inheritable handle when the daemon exits.
	return nil
}

func privateDir(path string) error {
	if e := os.MkdirAll(path, 0700); e != nil {
		return e
	}
	token, e := syscall.OpenCurrentProcessToken()
	if e != nil {
		return e
	}
	defer token.Close()
	user, e := token.GetTokenUser()
	if e != nil {
		return e
	}
	sid, e := user.User.Sid.String()
	if e != nil {
		return e
	}
	sddl, _ := syscall.UTF16PtrFromString("D:P(A;OICI;FA;;;SY)(A;OICI;FA;;;" + sid + ")")
	var sd uintptr
	adv := syscall.NewLazyDLL("advapi32.dll")
	ok, _, e := adv.NewProc("ConvertStringSecurityDescriptorToSecurityDescriptorW").Call(uintptr(unsafe.Pointer(sddl)), 1, uintptr(unsafe.Pointer(&sd)), 0)
	if ok == 0 {
		return e
	}
	defer kernel.NewProc("LocalFree").Call(sd)
	name, e := syscall.UTF16PtrFromString(path)
	if e != nil {
		return e
	}
	ok, _, e = adv.NewProc("SetFileSecurityW").Call(uintptr(unsafe.Pointer(name)), 0x80000004, sd)
	if ok == 0 {
		return e
	}
	return nil
}
