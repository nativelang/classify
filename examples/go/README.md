# Classify a movie review in Go

```sh
go get github.com/nativelang/classify/bindings/go@v0.2.0
```

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

[Run Classify on Windows or an Intel Mac](../../self-hosting/README.md)
