#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/num
cat > pkg/num/foo.go <<'EOF_2'
// Package num describes numbers.
package num

// Foo names the sign of n.
func Foo(n int) string {
	if n < 0 {
		return "negative"
	}
	if n == 0 {
		return "zero"
	}
	return "positive"
}
EOF_2
cat > pkg/num/foo_test.go <<'EOF_3'
package num

import "testing"

func Test_Foo_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		want string
	}{
		{"positive", 3, "positive"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Foo(tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
EOF_3
