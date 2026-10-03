#!/usr/bin/env bash
set -euo pipefail
mkdir -p pkg/net
cat > go.mod <<'EOF_GO_MOD'
module example.com/netx

go 1.26

require github.com/ctx42/testing v0.56.0
EOF_GO_MOD
cat > go.sum <<'EOF_GO_SUM'
github.com/ctx42/testing v0.56.0 h1:+yZwRy+5JQb+14YtRTGJxWbAMAP9qlU9pMa8TPqgdzE=
github.com/ctx42/testing v0.56.0/go.mod h1:wRBqNRtlxDZnXIjgCX3zr05Acl6JC1D6cSBN2IpaMIs=
EOF_GO_SUM
cat > pkg/net/net.go <<'EOF_PKG_NET_NET_GO'
// Package net wraps byte streams with connection and buffer
// bookkeeping.
package net
EOF_PKG_NET_NET_GO
cat > pkg/net/conn.go <<'EOF_PKG_NET_CONN_GO'
package net

import (
	"fmt"
	"io"
)

var _ io.Closer = (*Conn)(nil)

// Conn is a connection over an underlying stream.
type Conn struct {
	rwc io.ReadWriteCloser
}

// NewConn returns a Conn over rwc.
func NewConn(rwc io.ReadWriteCloser) *Conn {
	return &Conn{rwc: rwc}
}

// Close implements io.Closer. The behavior of Close after the first
// call is undefined. Specific implementations may document their own
// behavior.
func (con *Conn) Close() error {
	if err := con.rwc.Close(); err != nil {
		return fmt.Errorf("close conn: %w", err)
	}
	return nil
}
EOF_PKG_NET_CONN_GO
cat > pkg/net/buffer.go <<'EOF_PKG_NET_BUFFER_GO'
package net

import "strings"

// Buffer collects text until it is closed.
type Buffer struct {
	parts  []string
	closed bool
}

// Append adds s to the buffer and reports whether it was added; a
// closed buffer drops s.
func (buf *Buffer) Append(s string) bool {
	if buf.closed {
		return false
	}
	buf.parts = append(buf.parts, s)
	return true
}

// Close marks the buffer closed, so later appends are dropped. It
// always returns nil.
func (buf *Buffer) Close() error {
	buf.closed = true
	return nil
}

// String returns the appended text joined in order.
func (buf *Buffer) String() string {
	return strings.Join(buf.parts, "")
}
EOF_PKG_NET_BUFFER_GO
cat > pkg/net/all_test.go <<'EOF_PKG_NET_ALL_TEST_GO'
package net

import "io"

// stream is an io.ReadWriteCloser whose Close returns err.
type stream struct {
	io.ReadWriter
	err error
}

// Close returns the stream's err.
func (stm *stream) Close() error {
	return stm.err
}
EOF_PKG_NET_ALL_TEST_GO
cat > pkg/net/conn_test.go <<'EOF_PKG_NET_CONN_TEST_GO'
package net

import (
	"errors"
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_NewConn(t *testing.T) {
	// --- Given ---
	stm := &stream{}

	// --- When ---
	have := NewConn(stm)

	// --- Then ---
	assert.Same(t, stm, have.rwc)
}

func Test_Conn_Close(t *testing.T) {
	t.Run("closes stream", func(t *testing.T) {
		// --- Given ---
		con := NewConn(&stream{})

		// --- When ---
		err := con.Close()

		// --- Then ---
		assert.NoError(t, err)
	})

	t.Run("error - stream close fails", func(t *testing.T) {
		// --- Given ---
		cause := errors.New("pipe broken")

		con := NewConn(&stream{err: cause})

		// --- When ---
		err := con.Close()

		// --- Then ---
		assert.ErrorIs(t, cause, err)
	})
}
EOF_PKG_NET_CONN_TEST_GO
cat > pkg/net/buffer_test.go <<'EOF_PKG_NET_BUFFER_TEST_GO'
package net

import (
	"testing"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Buffer_Append(t *testing.T) {
	t.Run("open buffer", func(t *testing.T) {
		// --- Given ---
		buf := &Buffer{}

		s := "abc"

		// --- When ---
		have := buf.Append(s)

		// --- Then ---
		assert.True(t, have)

		assert.Equal(t, "abc", buf.String())
	})

	t.Run("closed buffer", func(t *testing.T) {
		// --- Given ---
		buf := &Buffer{closed: true}

		s := "abc"

		// --- When ---
		have := buf.Append(s)

		// --- Then ---
		assert.False(t, have)

		assert.Empty(t, buf.String())
	})
}

func Test_Buffer_Close(t *testing.T) {
	// --- Given ---
	buf := &Buffer{}

	// --- When ---
	err := buf.Close()

	// --- Then ---
	assert.NoError(t, err)

	assert.True(t, buf.closed)
}

func Test_Buffer_String(t *testing.T) {
	// --- Given ---
	buf := &Buffer{parts: []string{"ab", "c"}}

	// --- When ---
	have := buf.String()

	// --- Then ---
	assert.Equal(t, "abc", have)
}
EOF_PKG_NET_BUFFER_TEST_GO
# Runs have no network: fill the run's module cache now, from the local cache
# that dev/eval-changed.sh serves as GOPROXY.
go mod download
