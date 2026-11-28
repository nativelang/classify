// Launch the CI probe in the existing interactive logon session with Administrator
// membership disabled and maximum privileges removed. The child checks its token.
package main

import (
	"fmt"
	"os"
	"os/exec"
	"syscall"
	"unsafe"
)

func run() error {
	if len(os.Args) < 2 {
		return fmt.Errorf("missing test command")
	}
	process, err := syscall.GetCurrentProcess()
	if err != nil {
		return err
	}
	var token syscall.Token
	err = syscall.OpenProcessToken(process, syscall.TOKEN_QUERY|syscall.TOKEN_DUPLICATE|syscall.TOKEN_ASSIGN_PRIMARY, &token)
	if err != nil {
		return err
	}
	defer token.Close()
	admins, err := syscall.StringToSid("S-1-5-32-544")
	if err != nil {
		return err
	}
	group := syscall.SIDAndAttributes{Sid: admins}
	var restricted syscall.Token
	create := syscall.NewLazyDLL("advapi32.dll").NewProc("CreateRestrictedToken")
	ok, _, err := create.Call(uintptr(token), 1, 1, uintptr(unsafe.Pointer(&group)), 0, 0, 0, 0, uintptr(unsafe.Pointer(&restricted)))
	if ok == 0 {
		return err
	}
	defer restricted.Close()
	child := exec.Command(os.Args[1], os.Args[2:]...)
	child.SysProcAttr = &syscall.SysProcAttr{Token: restricted}
	child.Stdout = os.Stdout
	child.Stderr = os.Stderr
	return child.Run()
}
func main() {
	if err := run(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
