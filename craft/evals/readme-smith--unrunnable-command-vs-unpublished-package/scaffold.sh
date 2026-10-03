#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module github.com/acme/tally

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
mkdir -p cmd/tally
cat > cmd/tally/main.go <<'EOF_3'
// Command tally prints count, sum, min, and max of every numeric CSV column.
package main

import (
	"encoding/csv"
	"fmt"
	"math"
	"os"
	"strconv"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: tally file.csv")
		os.Exit(2)
	}
	f, err := os.Open(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer f.Close()
	rows, err := csv.NewReader(f).ReadAll()
	if err != nil || len(rows) == 0 {
		fmt.Fprintln(os.Stderr, "tally: no rows")
		os.Exit(1)
	}
	for c, name := range rows[0] {
		n, sum, lo, hi := 0, 0.0, math.Inf(1), math.Inf(-1)
		for _, r := range rows[1:] {
			v, err := strconv.ParseFloat(r[c], 64)
			if err != nil {
				continue
			}
			n++
			sum += v
			lo, hi = math.Min(lo, v), math.Max(hi, v)
		}
		if n > 0 {
			fmt.Printf("%-10s count=%d sum=%g min=%g max=%g\n", name, n, sum, lo, hi)
		}
	}
}
EOF_3
cat > Makefile <<'EOF_4'
.PHONY: demo test

# demo generates sample data with the Zig generator, then tallies it.
demo:
	zig run tools/gen.zig > testdata/sample.csv
	go run ./cmd/tally testdata/sample.csv

test:
	go test ./...
EOF_4
mkdir -p tools
cat > tools/gen.zig <<'EOF_5'
const std = @import("std");

pub fn main() !void {
    const out = std.io.getStdOut().writer();
    try out.print("region,orders,revenue\n", .{});
    var i: u32 = 1;
    while (i <= 5) : (i += 1) {
        try out.print("r{d},{d},{d}.50\n", .{ i, i * 3, i * 120 });
    }
}
EOF_5
mkdir -p testdata
: > testdata/.gitkeep
cat > HACKING.md <<'EOF_7'
# Hacking on tally

The quickstart demo (`make demo`) needs Zig 0.13 on PATH: `tools/gen.zig`
generates the sample CSV that `go run ./cmd/tally` then summarizes. Go alone
builds and tests the CLI (`go test ./...`).
EOF_7
cat > RELEASING.md <<'EOF_8'
# Releasing

tally is not published yet. The repository at github.com/acme/tally is still
private and has no tag; it goes public with the first tag, v0.1.0, after the
security review. Until then `go install github.com/acme/tally/cmd/tally@latest`
fails for everyone outside the team.
EOF_8
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
git remote add origin https://github.com/acme/tally.git
git add -A
git commit -q -m 'chore: initial import'
