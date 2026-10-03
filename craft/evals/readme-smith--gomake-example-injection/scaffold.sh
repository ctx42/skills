#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/httpc

go 1.22
EOF_0
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF_1'
name: ci
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go install github.com/ctx42/gomake@latest
      - name: gomake check
        run: gomake :go:check
EOF_1
cat > LICENSE <<'EOF_2'
MIT License

Copyright (c) 2026 Acme
EOF_2
cat > client.go <<'EOF_3'
// Package httpc is a small HTTP client that resolves request paths against a
// base URL.
package httpc

import (
	"context"
	"io"
	"net/http"
	"strings"
)

// Client sends requests to paths below one base URL.
type Client struct {
	base string
	hc   *http.Client
}

// New returns a Client for base, e.g. "https://api.example.com/v1".
func New(base string) *Client {
	return &Client{base: strings.TrimRight(base, "/"), hc: http.DefaultClient}
}

// Response is a fully read HTTP response.
type Response struct {
	Status int
	Body   string
}

// Do sends a request with method to path below the base URL and reads the
// whole response body.
func (c *Client) Do(ctx context.Context, method, path string) (*Response, error) {
	req, err := http.NewRequestWithContext(ctx, method, c.base+"/"+strings.TrimLeft(path, "/"), nil)
	if err != nil {
		return nil, err
	}
	res, err := c.hc.Do(req)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()
	b, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, err
	}
	return &Response{Status: res.StatusCode, Body: string(b)}, nil
}
EOF_3
cat > header.go <<'EOF_4'
package httpc

import (
	"fmt"
	"strings"
)

// Header maps canonical header names to values.
type Header map[string]string

// Parse parses "Name: value" lines into a Header. Blank lines are skipped.
func Parse(raw string) (Header, error) {
	h := Header{}
	for _, line := range strings.Split(raw, "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		k, v, ok := strings.Cut(line, ":")
		if !ok {
			return nil, fmt.Errorf("httpc: malformed header line %q", line)
		}
		h[strings.TrimSpace(k)] = strings.TrimSpace(v)
	}
	return h, nil
}
EOF_4
cat > client_test.go <<'EOF_5'
package httpc

import "testing"

func TestParse(t *testing.T) {
	h, err := Parse("Accept: text/plain\n\nX-Id: 7")
	if err != nil {
		t.Fatal(err)
	}
	if h["Accept"] != "text/plain" || h["X-Id"] != "7" {
		t.Fatalf("unexpected header %v", h)
	}
}
EOF_5
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin https://github.com/acme/httpc.git
git add -A
git commit -q -m 'chore: initial import'
