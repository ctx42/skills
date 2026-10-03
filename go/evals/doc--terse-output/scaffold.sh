#!/usr/bin/env bash
set -euo pipefail
cat > go.mod <<'EOF_0'
module example.com/text

go 1.22
EOF_0
mkdir -p text
cat > text/text.go <<'EOF_1'
// Package text counts words.
package text

import "strings"

// counts the words in s, splitting on runs of white space.
func Foo(s string) int {
	count := 0
	for range strings.Fields(s) {
		// increment count
		count++
	}
	return count
}
EOF_1
