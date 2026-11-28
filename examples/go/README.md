# Classify a movie review in Go

You’ll need Go 1.20 or later. Use an Apple Silicon Mac with macOS 15 or later, or [Debian 12-compatible Linux](../../SPECIFICATION.md#linux-requirements) on ARM64 or x64. On Windows or an Intel Mac, [run the local server](../../self-hosting/README.md).

In an empty folder, create a module and install Classify.

```sh
go mod init movie
go get github.com/nativelang/classify/bindings/go@v0.2.0
```

Save this as `main.go`.

```go
package main

import (
	"fmt"
	"log"

	"github.com/nativelang/classify/bindings/go"
)

func main() {
	label, err := classify.Classify("This is a terrible movie", []string{"positive", "negative", "neutral"})
	if err != nil {
		log.Fatal(err)
	}
	if label != nil {
		fmt.Println(*label) // negative
	}
}
```

The first run downloads the model (about 1.6 GB). Later runs work offline.

```sh
go run main.go
```

If no category fits, `Classify` returns a `nil` label and a `nil` error.
