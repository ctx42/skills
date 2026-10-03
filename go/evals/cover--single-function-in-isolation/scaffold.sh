#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/cfg
cat > pkg/cfg/parse.go <<'EOF_2'
// Package cfg parses key=value configuration lines.
package cfg

import (
	"errors"
	"fmt"
	"strings"
)

// ErrEmpty is returned for an empty line.
var ErrEmpty = errors.New("empty line")

// Config is one parsed key=value pair.
type Config struct {
	Key   string
	Value string
}

// Parse parses a "key=value" line.
func Parse(s string) (Config, error) {
	if s == "" {
		return Config{}, ErrEmpty
	}
	k, v, ok := strings.Cut(s, "=")
	if !ok {
		return Config{}, fmt.Errorf("missing '=' in %q", s)
	}
	return Config{Key: k, Value: v}, nil
}

// Load parses a line read from a file, trimming surrounding space.
func Load(line string) (Config, error) {
	cfg, err := Parse(strings.TrimSpace(line))
	if err != nil {
		return Config{}, fmt.Errorf("load: %w", err)
	}
	return cfg, nil
}
EOF_2
cat > pkg/cfg/parse_test.go <<'EOF_3'
package cfg

import (
	"errors"
	"testing"
)

func Test_Parse(t *testing.T) {
	// --- Given ---
	line := "name=svc"

	// --- When ---
	have, err := Parse(line)

	// --- Then ---
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := Config{Key: "name", Value: "svc"}
	if have != want {
		t.Errorf("want %+v, have %+v", want, have)
	}
}

func Test_Load(t *testing.T) {
	// --- Given ---
	line := "   "

	// --- When ---
	_, err := Load(line)

	// --- Then ---
	if !errors.Is(err, ErrEmpty) {
		t.Errorf("want ErrEmpty, have %v", err)
	}
}
EOF_3
