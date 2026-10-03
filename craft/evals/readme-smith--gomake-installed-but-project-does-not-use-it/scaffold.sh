#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/linecount

go 1.22
EOF_0
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'EOF_1'
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
EOF_1
cat > LICENSE <<'EOF_2'
MIT License

Copyright (c) 2026 Acme
EOF_2
mkdir -p cmd/linecount
cat > cmd/linecount/main.go <<'EOF_3'
// Command linecount prints the number of non-blank lines in each file.
package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/acme/linecount/internal/count"
)

func main() {
	all := flag.Bool("all", false, "count blank lines too")
	flag.Parse()
	for _, name := range flag.Args() {
		n, err := count.File(name, *all)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		fmt.Printf("%8d %s\n", n, name)
	}
}
EOF_3
mkdir -p internal/count
cat > internal/count/count.go <<'EOF_4'
// Package count counts lines.
package count

import (
	"bufio"
	"os"
	"strings"
)

// File returns the number of lines in name, skipping blank ones unless all.
func File(name string, all bool) (int, error) {
	f, err := os.Open(name)
	if err != nil {
		return 0, err
	}
	defer f.Close()
	n := 0
	sc := bufio.NewScanner(f)
	for sc.Scan() {
		if all || strings.TrimSpace(sc.Text()) != "" {
			n++
		}
	}
	return n, sc.Err()
}
EOF_4
mkdir -p internal/count
cat > internal/count/count_test.go <<'EOF_5'
package count

import (
	"os"
	"path/filepath"
	"testing"
)

func TestFile(t *testing.T) {
	p := filepath.Join(t.TempDir(), "a.txt")
	if err := os.WriteFile(p, []byte("a\n\nb\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	n, err := File(p, false)
	if err != nil || n != 2 {
		t.Fatalf("File = %d, %v; want 2", n, err)
	}
}
EOF_5
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin https://github.com/acme/linecount.git
git add -A
git commit -q -m 'chore: initial import'
