#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/svc
cat > pkg/svc/foo.go <<'EOF_2'
// Package svc loads and stores service settings.
package svc

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// ErrNoPort is returned when a settings line carries no port.
var ErrNoPort = errors.New("no port")

// Settings are the parsed service settings.
type Settings struct {
	Host string
	Port int
}

// Addr returns the "host:port" form of s.
func Addr(s Settings) string {
	return s.Host + ":" + strconv.Itoa(s.Port)
}

// Valid reports whether s has a host and a port in range.
func Valid(s Settings) bool {
	if s.Host == "" {
		return false
	}
	return s.Port > 0 && s.Port < 65536
}

// Load parses a "host:port" settings line.
func Load(line string) (Settings, error) {
	host, port, ok := strings.Cut(line, ":")
	if !ok {
		return Settings{}, ErrNoPort
	}
	n, err := strconv.Atoi(port)
	if err != nil {
		return Settings{}, fmt.Errorf("bad port %q: %w", port, err)
	}
	if n <= 0 || n > 65535 {
		return Settings{}, fmt.Errorf("port %d out of range", n)
	}
	return Settings{Host: host, Port: n}, nil
}

// Store renders s as a settings line.
func Store(s Settings) string {
	return Addr(s)
}
EOF_2
cat > pkg/svc/foo_test.go <<'EOF_3'
package svc

import "testing"

func Test_Addr(t *testing.T) {
	// --- Given ---
	s := Settings{Host: "db", Port: 5432}

	// --- When ---
	have := Addr(s)

	// --- Then ---
	if have != "db:5432" {
		t.Errorf("want %q, have %q", "db:5432", have)
	}
}

func Test_Load(t *testing.T) {
	// --- Given ---
	line := "db:5432"

	// --- When ---
	have, err := Load(line)

	// --- Then ---
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := Settings{Host: "db", Port: 5432}
	if have != want {
		t.Errorf("want %+v, have %+v", want, have)
	}
}

func Test_Store(t *testing.T) {
	// --- Given ---
	s := Settings{Host: "db", Port: 1}

	// --- When ---
	have := Store(s)

	// --- Then ---
	if have != "db:1" {
		t.Errorf("want %q, have %q", "db:1", have)
	}
}
EOF_3
