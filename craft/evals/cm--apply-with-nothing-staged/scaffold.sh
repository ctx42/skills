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
mkdir -p httpx
cat > httpx/client.go <<'EOF_1'
// Package httpx wraps net/http with the service's defaults.
package httpx

import "net/http"

// Client sends requests to upstream services.
type Client struct {
	hc *http.Client
}

// Do sends req once.
func (cli *Client) Do(req *http.Request) (*http.Response, error) {
	return cli.hc.Do(req)
}
EOF_1
git add -A
git commit -qm 'feat(httpx): add client'
mkdir -p httpx
cat > httpx/client.go <<'EOF_0'
// Package httpx wraps net/http with the service's defaults.
package httpx

import (
	"net/http"
	"time"
)

// maxAttempts is how many times Do tries a request before giving up.
const maxAttempts = 3

// Client sends requests to upstream services.
type Client struct {
	hc *http.Client
}

// Do sends req, retrying transport errors with exponential backoff.
func (cli *Client) Do(req *http.Request) (*http.Response, error) {
	var err error
	for attempt := 0; attempt < maxAttempts; attempt++ {
		var resp *http.Response
		resp, err = cli.hc.Do(req)
		if err == nil {
			return resp, nil
		}
		if attempt == maxAttempts-1 {
			break
		}
		time.Sleep(time.Duration(1<<attempt) * 100 * time.Millisecond)
	}
	return nil, err
}
EOF_0
