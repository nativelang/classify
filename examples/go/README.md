# Classify a movie review in Go

```sh
go get github.com/nativelang/classify/bindings/go
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

[Speed up startup with the local API service](../../docs/service.md).
