# Go

[Start the Classify server](../../self-hosting/README.md). With Go installed, save this as `main.go`.

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
)

const classifyURL = "http://127.0.0.1:8080/v1/classify"

func main() {
	request := strings.NewReader(`{"text":"This is a terrible movie","categories":["positive","negative","neutral"]}`)
	response, err := http.Post(classifyURL, "application/json", request)
	if err != nil {
		log.Fatal(err)
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		log.Fatal(response.Status)
	}

	var result map[string]any
	if err := json.NewDecoder(response.Body).Decode(&result); err != nil {
		log.Fatal(err)
	}
	fmt.Println(result["category"])
}
```

Run it in a second terminal.

```sh
go run main.go
```

Output: `negative`
