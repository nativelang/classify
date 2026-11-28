# Go

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
		fmt.Println(*label)
	}
}
```

Run `go run main.go`. It prints `negative`. The first call downloads the model and runtime. Later calls use the local cache. A successful call returns a nil label when no category fits.
