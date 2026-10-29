#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/demo

go 1.22
EOF_0
mkdir -p pkg/svc
cat > pkg/svc/foo.go <<'EOF_1'
// Package svc buffers lines and sends them in batches.
package svc

import (
	"errors"
	"strings"
)

// ErrClosed is returned when a Svc is used after Close.
var ErrClosed = errors.New("svc: closed")

// Svc buffers lines and sends them in batches of ten.
type Svc struct {
	lines  []string
	closed bool
}

// New returns an empty Svc.
func New() *Svc {
	return &Svc{}
}

func (svc *Svc) Add(line string) error {
	if svc.closed {
		return ErrClosed
	}
	// append the line
	svc.lines = append(svc.lines, strings.TrimSpace(line))
	return nil
}

// flush sends the lines.
func (svc *Svc) Flush(send func([]string)) (int, error) {
	if svc.closed {
		return 0, ErrClosed
	}
	i := 0
	for len(svc.lines) > 0 {
		n := min(len(svc.lines), 10)
		send(svc.lines[:n])
		svc.lines = svc.lines[n:]
		// increment i
		i++
	}
	return i, nil
}

// Close marks the svc closed.
func (svc *Svc) Close() {
	// set closed to true
	svc.closed = true
}

// len returns the buffered lines
func (svc *Svc) Len() int {
	return len(svc.lines)
}
EOF_1
