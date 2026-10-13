#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/app

go 1.22
EOF_0
mkdir -p fetch
cat > fetch/fetch.go <<'EOF_1'
// Package fetch downloads documents over HTTP.
package fetch

import (
	"io"
	"net/http"
	"strings"
)

// Get returns the body of the document at url.
func Get(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}

// Post sends body to url as plain text and returns the response body.
func Post(url, body string) ([]byte, error) {
	resp, err := http.Post(url, "text/plain", strings.NewReader(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}
EOF_1
cat > README.md <<'EOF_2'
# app

Downlaods documents over HTTP.
EOF_2
git add -A
git commit -qm 'feat(fetch): add document fetcher'
mkdir -p fetch
cat > fetch/fetch.go <<'EOF_0'
// Package fetch downloads documents over HTTP.
package fetch

import (
	"fmt"
	"io"
	"net/http"
	"strings"
)

// Get returns the body of the document at url.
func Get(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("get %s: %s", url, resp.Status)
	}
	return io.ReadAll(resp.Body)
}

// Post sends body to url as plain text and returns the response body.
func Post(url, body string) ([]byte, error) {
	resp, err := http.Post(url, "text/plain", strings.NewReader(body))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}

// Head returns the response headers of the document at url without
// downloading its body, so callers can check the type and size first.
func Head(url string) (http.Header, error) {
	resp, err := http.Head(url)
	if err != nil {
		return nil, err
	}
	resp.Body.Close()
	return resp.Header, nil
}
EOF_0
cat > README.md <<'EOF_1'
# app

Downloads documents over HTTP.
EOF_1
mkdir -p cmd/size
cat > cmd/size/main.go <<'EOF_2'
// Command size prints the Content-Length of the document at a URL.
package main

import (
	"fmt"
	"os"

	"example.com/app/fetch"
)

func main() {
	hdr, err := fetch.Head(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(hdr.Get("Content-Length"))
}
EOF_2
git add README.md fetch/fetch.go
