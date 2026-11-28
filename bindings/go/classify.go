// Package classify classifies text locally using the Classify runtime.
package classify

import (
	_ "embed"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"sync"
)

//go:embed bootstrap.sh
var bootstrap string

var (
	mu      sync.Mutex
	current *session
)

type session struct {
	cmd     *exec.Cmd
	request *json.Encoder
	reply   *json.Decoder
}

func start() (*session, error) {
	cmd := exec.Command("/bin/sh", "-c", bootstrap)
	cmd.Stderr = os.Stderr
	in, err := cmd.StdinPipe()
	if err != nil {
		return nil, err
	}
	out, err := cmd.StdoutPipe()
	if err != nil {
		in.Close()
		return nil, err
	}
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	return &session{cmd: cmd, request: json.NewEncoder(in), reply: json.NewDecoder(out)}, nil
}

func reset() {
	current.cmd.Process.Kill()
	current.cmd.Wait()
	current = nil
}

// Classify returns a matching category, or nil if the model abstains.
// Calls reuse one local runtime process. A failure is returned as an error.
func Classify(text string, categories []string) (*string, error) {
	mu.Lock()
	defer mu.Unlock()
	if current == nil {
		s, err := start()
		if err != nil {
			return nil, err
		}
		current = s
	}

	if err := current.request.Encode(map[string]any{"text": text, "categories": categories}); err != nil {
		reset()
		return nil, fmt.Errorf("write Classify request: %w", err)
	}
	var result struct {
		Status   string
		Category *string
		Error    *struct{ Message string }
	}
	if err := current.reply.Decode(&result); err != nil {
		reset()
		return nil, fmt.Errorf("read Classify response: %w", err)
	}
	if result.Error != nil {
		return nil, errors.New(result.Error.Message)
	}
	if result.Status == "matched" && result.Category != nil || result.Status == "unknown" && result.Category == nil {
		return result.Category, nil
	}
	reset()
	return nil, errors.New("unexpected Classify response")
}
