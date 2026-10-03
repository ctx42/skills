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
EOF_1
git add -A
git commit -qm 'feat(fetch): add document fetcher'
mkdir -p fetch
cat > fetch/fetch.go <<'EOF_0'
// Package fetch downloads documents over HTTP.
package fetch

import (
	"io"
	"net/http"
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
git add -A
