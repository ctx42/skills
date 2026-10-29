#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/portcheck

go 1.22
EOF_0
mkdir -p cmd/portcheck
cat > cmd/portcheck/main.go <<'EOF_1'
// Command portcheck reports which host:port targets accept TCP connections.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/acme/portcheck/internal/scan"
)

func main() {
	timeout := flag.Duration("timeout", 2*time.Second, "per-target dial timeout")
	asJSON := flag.Bool("json", false, "print one JSON object per target")
	concurrency := flag.Int("concurrency", 64, "maximum simultaneous dials")
	flag.Usage = func() {
		fmt.Fprintln(os.Stderr, "usage: portcheck [flags] host:port...")
		flag.PrintDefaults()
	}
	flag.Parse()
	if flag.NArg() == 0 {
		flag.Usage()
		os.Exit(2)
	}

	results := scan.Check(context.Background(), flag.Args(), *timeout, *concurrency)
	failed := false
	for _, r := range results {
		if !r.Open {
			failed = true
		}
		if *asJSON {
			_ = json.NewEncoder(os.Stdout).Encode(r)
			continue
		}
		state := "open"
		if !r.Open {
			state = "closed: " + r.Err
		}
		fmt.Printf("%-24s %s (%s)\n", r.Target, state, r.Took.Round(time.Millisecond))
	}
	if failed {
		os.Exit(1)
	}
}
EOF_1
mkdir -p internal/scan
cat > internal/scan/scan.go <<'EOF_2'
// Package scan dials host:port targets concurrently.
package scan

import (
	"context"
	"net"
	"sync"
	"time"
)

// Result is the outcome of dialing one target.
type Result struct {
	Target string        `json:"target"`
	Open   bool          `json:"open"`
	Err    string        `json:"error,omitempty"`
	Took   time.Duration `json:"took_ns"`
}

// Check dials every target over TCP with at most concurrency dials in flight
// and returns one Result per target, in input order.
func Check(ctx context.Context, targets []string, timeout time.Duration, concurrency int) []Result {
	if concurrency < 1 {
		concurrency = 1
	}
	out := make([]Result, len(targets))
	sem := make(chan struct{}, concurrency)
	var wg sync.WaitGroup
	for i, t := range targets {
		wg.Add(1)
		sem <- struct{}{}
		go func(i int, t string) {
			defer wg.Done()
			defer func() { <-sem }()
			start := time.Now()
			d := net.Dialer{Timeout: timeout}
			conn, err := d.DialContext(ctx, "tcp", t)
			r := Result{Target: t, Took: time.Since(start)}
			if err != nil {
				r.Err = err.Error()
			} else {
				r.Open = true
				_ = conn.Close()
			}
			out[i] = r
		}(i, t)
	}
	wg.Wait()
	return out
}
EOF_2
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF_3'
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
      - run: go vet ./...
      - run: go test ./...
EOF_3
mkdir -p assets
printf '%s' 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==' | base64 -d > assets/logo.png
cat > .editorconfig <<'EOF_4'
root = true

[*]
end_of_line = lf
insert_final_newline = true

[*.go]
indent_style = tab

[*.md]
max_line_length = 100
EOF_4
