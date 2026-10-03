#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/demo

go 1.22
EOF_0
mkdir -p pkg/sink
cat > pkg/sink/sink.go <<'EOF_1'
// Package sink writes byte streams to their destinations.
package sink

import (
	"io"
	"os"
)

var _ io.Writer = (*fileSink)(nil)
var _ io.Writer = (*teeSink)(nil)

// fileSink writes to an open file.
type fileSink struct {
	fil *os.File
}

// Write writes p to the file. It returns the number of bytes written
// and any error encountered.
func (snk *fileSink) Write(p []byte) (int, error) {
	return snk.fil.Write(p)
}

// teeSink writes to a primary writer and a mirror.
type teeSink struct {
	primary io.Writer
	mirror  io.Writer
}

// Write writes p to the primary writer. It returns the number of bytes
// written and any error encountered.
func (tee *teeSink) Write(p []byte) (int, error) {
	n, err := tee.primary.Write(p)
	if err != nil {
		return n, err
	}
	_, _ = tee.mirror.Write(p)
	return len(p), nil
}
EOF_1
