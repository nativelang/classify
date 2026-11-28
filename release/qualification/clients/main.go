package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"runtime"
	"strings"

	"github.com/nativelang/classify/bindings/go"
)

func main() {
	fmt.Println(runtime.GOARCH)
	input := bufio.NewScanner(os.Stdin)
	for input.Scan() {
		fields := strings.Split(input.Text(), "\t")
		label, err := classify.Classify(fields[0], fields[1:])
		if err != nil {
			log.Fatal(err)
		}
		if label == nil {
			fmt.Println()
		} else {
			fmt.Println(*label)
		}
	}
	if err := input.Err(); err != nil {
		log.Fatal(err)
	}
}
