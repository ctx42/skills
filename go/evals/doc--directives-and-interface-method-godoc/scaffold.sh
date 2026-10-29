#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/demo

go 1.22
EOF_0
mkdir -p pkg/io
cat > pkg/io/io.go <<'EOF_1'
//go:build !windows

// Package io serves bytes from an in-memory buffer.
package io

import "io"

//go:generate stringer -type=Mode

// Mode selects how a Source treats its buffer.
type Mode int

// Source modes.
const (
	ModeCopy Mode = iota
	ModeShare
)

var _ io.Reader = (*Source)(nil)

// Source reads from a fixed byte slice.
type Source struct {
	buf []byte
	off int
}

// NewSource returns a Source that reads buf.
func NewSource(buf []byte) *Source {
	return &Source{buf: buf}
}

// Read reads up to len(p) bytes into p. It returns the number of bytes
// read and any error encountered. At end of input it returns 0, io.EOF.
func (src *Source) Read(p []byte) (int, error) {
	if src.off >= len(src.buf) {
		return 0, io.EOF
	}
	n := copy(p, src.buf[src.off:])
	src.off += n
	return n, nil
}
EOF_1
