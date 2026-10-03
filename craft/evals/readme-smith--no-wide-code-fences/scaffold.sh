#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/wiretap

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
cat > wiretap.go <<'EOF_3'
// Package wiretap renders HTTP/1.1 requests as the exact bytes sent on the wire.
package wiretap

import (
	"bytes"
	"fmt"
	"sort"
)

// Request renders an HTTP/1.1 request line, headers sorted by name, a blank
// line, and the body, exactly as they travel over the connection.
func Request(method, target, host string, header map[string]string, body string) []byte {
	var b bytes.Buffer
	fmt.Fprintf(&b, "%s %s HTTP/1.1\r\n", method, target)
	fmt.Fprintf(&b, "Host: %s\r\n", host)
	keys := make([]string, 0, len(header))
	for k := range header {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	for _, k := range keys {
		fmt.Fprintf(&b, "%s: %s\r\n", k, header[k])
	}
	fmt.Fprintf(&b, "Content-Length: %d\r\n\r\n", len(body))
	b.WriteString(body)
	return b.Bytes()
}
EOF_3
cat > example_test.go <<'EOF_4'
package wiretap_test

import (
	"fmt"

	"github.com/acme/wiretap"
)

func ExampleRequest() {
	wire := wiretap.Request("POST", "/v1/orders", "api.shop.example", map[string]string{
		"Accept":        "application/json",
		"Authorization": "Bearer 7f3c9a1e",
		"Content-Type":  "application/json",
		"User-Agent":    "wiretap/0.3",
		"X-Request-Id":  "c0ffee-42-b7d1",
	}, `{"sku":"KB-104","qty":2,"note":"gift wrap"}`)
	fmt.Printf("%q\n", wire)
	// Output:
	// "POST /v1/orders HTTP/1.1\r\nHost: api.shop.example\r\nAccept: application/json\r\nAuthorization: Bearer 7f3c9a1e\r\nContent-Type: application/json\r\nUser-Agent: wiretap/0.3\r\nX-Request-Id: c0ffee-42-b7d1\r\nContent-Length: 43\r\n\r\n{\"sku\":\"KB-104\",\"qty\":2,\"note\":\"gift wrap\"}"
}
EOF_4
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin https://github.com/acme/wiretap.git
git add -A
git commit -q -m 'chore: initial import'
