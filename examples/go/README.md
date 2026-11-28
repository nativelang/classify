# Classify text from Go

[Start the local Classify server](../../self-hosting/README.md), then open a second terminal. This example uses only the Go standard library. Save it as `main.go`.

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
)

func main() {
	request := strings.NewReader(`{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}`)
	response, err := http.Post("http://127.0.0.1:8080/v1/classify", "application/json", request)
	if err != nil {
		log.Fatal(err)
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		log.Fatal(response.Status)
	}

	var result struct {
		Category *string `json:"category"`
	}
	if err := json.NewDecoder(response.Body).Decode(&result); err != nil {
		log.Fatal(err)
	}
	if result.Category == nil {
		fmt.Println("unknown")
		return
	}
	fmt.Println(*result.Category)
}
```

Run it with Go installed.

```sh
go run main.go
```

The example prints `negative`.
