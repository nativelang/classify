# Classify a movie review in Go

```sh
go get github.com/nativelang/classify/bindings/go@v0.2.2
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

The first call downloads the model. Later calls work offline.

[Platforms, download sizes and Windows setup](../../SPECIFICATION.md#language-package-platform-support)
