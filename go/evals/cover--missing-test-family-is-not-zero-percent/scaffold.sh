#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/text
cat > pkg/text/normalize.go <<'EOF_2'
// Package text cleans user-entered text.
package text

import "strings"

// Normalize trims s, collapses inner runs of spaces, and lower-cases it.
func Normalize(s string) string {
	s = strings.TrimSpace(s)
	if s == "" {
		return ""
	}
	return strings.ToLower(strings.Join(strings.Fields(s), " "))
}
EOF_2
cat > pkg/text/normalize_test.go <<'EOF_3'
package text

import "testing"

func TestNormalizeHelper(t *testing.T) {
	// --- Given ---
	s := "  Hello   World "

	// --- When ---
	have := Normalize(s)

	// --- Then ---
	if have != "hello world" {
		t.Errorf("want %q, have %q", "hello world", have)
	}
}
EOF_3
