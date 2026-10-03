#!/usr/bin/env bash
set -euo pipefail
mkdir -p pkg/foo
cat > go.mod <<'EOF_GO_MOD'
module example.com/foo

go 1.26

require github.com/ctx42/testing v0.56.0
EOF_GO_MOD
cat > go.sum <<'EOF_GO_SUM'
github.com/ctx42/testing v0.56.0 h1:+yZwRy+5JQb+14YtRTGJxWbAMAP9qlU9pMa8TPqgdzE=
github.com/ctx42/testing v0.56.0/go.mod h1:wRBqNRtlxDZnXIjgCX3zr05Acl6JC1D6cSBN2IpaMIs=
EOF_GO_SUM
cat > pkg/foo/foo.go <<'EOF_PKG_FOO_FOO_GO'
// Package foo parses "key=value" settings.
package foo

import (
	"bufio"
	"fmt"
	"io"
	"strconv"
	"strings"
)

// Setting is one parsed key-value pair.
type Setting struct {
	Key   string
	Value int
}

// Parse parses one "key=value" line.
func Parse(line string) (Setting, error) {
	// split at the first equals sign
	key, raw, _ := strings.Cut(line, "=")
	val, err := strconv.Atoi(raw)
	if err != nil {
		return Setting{}, fmt.Errorf("parse %s: %v", key, err)
	}
	return Setting{Key: key, Value: val}, nil
}

func FirstLine(rd io.Reader) (string, error) {
	line, err := bufio.NewReader(rd).ReadString('\n')
	if err != nil && err != io.EOF {
		return "", fmt.Errorf("failed to read line: %w", err)
	}
	return strings.TrimSpace(line), nil
}

// String returns the setting in its "key=value" form.
func (s Setting) String() string {
	return s.Key + "=" + strconv.Itoa(s.Value)
}
EOF_PKG_FOO_FOO_GO
cat > pkg/foo/foo_test.go <<'EOF_PKG_FOO_FOO_TEST_GO'
package foo

import (
	"errors"
	"strings"
	"testing"
	"testing/iotest"

	"github.com/ctx42/testing/pkg/assert"
)

func Test_Parse(t *testing.T) {
	t.Run("valid", func(t *testing.T) {
		// --- Given ---
		line := "a=1"

		// --- When ---
		have, err := Parse(line)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, Setting{Key: "a", Value: 1}, have)
	})

	t.Run("error - value not a number", func(t *testing.T) {
		// --- Given ---
		line := "a=x"

		// --- When ---
		have, err := Parse(line)

		// --- Then ---
		assert.ErrorContain(t, "invalid syntax", err)
		assert.Zero(t, have)
	})
}

func Test_FirstLine(t *testing.T) {
	t.Run("line with newline", func(t *testing.T) {
		// --- Given ---
		rd := strings.NewReader("a=1\nb=2\n")

		// --- When ---
		have, err := FirstLine(rd)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, "a=1", have)
	})

	t.Run("last line without newline", func(t *testing.T) {
		// --- Given ---
		rd := strings.NewReader("a=1")

		// --- When ---
		have, err := FirstLine(rd)

		// --- Then ---
		assert.NoError(t, err)
		assert.Equal(t, "a=1", have)
	})

	t.Run("error - reader fails", func(t *testing.T) {
		// --- Given ---
		rd := iotest.ErrReader(errors.New("disk gone"))

		// --- When ---
		have, err := FirstLine(rd)

		// --- Then ---
		assert.ErrorContain(t, "disk gone", err)
		assert.Empty(t, have)
	})
}

func Test_Setting_String(t *testing.T) {
	// --- Given ---
	set := Setting{Key: "a", Value: 1}

	// --- When ---
	have := set.String()

	// --- Then ---
	assert.Equal(t, "a=1", have)
}
EOF_PKG_FOO_FOO_TEST_GO
# Runs have no network: fill the run's module cache now, from the local cache
# that dev/eval-changed.sh serves as GOPROXY.
go mod download
