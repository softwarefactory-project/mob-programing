package main

import "fmt"
import "os"
import "encoding/hex"
import "encoding/base64"

func solve(s string) (int, string) {
        data, err := hex.DecodeString(s)
        if err != nil {
                return 1, ""
        }
        return 0, base64.StdEncoding.EncodeToString(data)
}

func main() {
        text := os.Args[1]
        err, res := solve(text);
        if err == 1 {
			panic("oops, invalid input")
		}
        fmt.Println(res)
}
