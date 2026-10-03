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
cat > pkg/svc/math.go <<'EOF_2'
// Package svc holds small numeric and text helpers.
package svc

// Clamp limits n to the range [lo, hi].
func Clamp(n, lo, hi int) int {
	if n < lo {
		return lo
	}
	if n > hi {
		return hi
	}
	return n
}

// Sign returns -1, 0, or 1 for negative, zero, and positive n.
func Sign(n int) int {
	if n < 0 {
		return -1
	}
	if n == 0 {
		return 0
	}
	return 1
}
EOF_2
cat > pkg/svc/math_test.go <<'EOF_3'
package svc

import "testing"

func Test_Clamp_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		lo   int
		hi   int
		want int
	}{
		{"inside", 5, 1, 10, 5},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Clamp(tc.n, tc.lo, tc.hi)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}

func Test_Sign_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		want int
	}{
		{"positive", 7, 1},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Sign(tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}
EOF_3
cat > pkg/svc/text.go <<'EOF_4'
package svc

import "strings"

// Trunc cuts s to at most n bytes, marking a cut with "...".
func Trunc(s string, n int) string {
	if n <= 0 {
		return ""
	}
	if len(s) <= n {
		return s
	}
	return s[:n] + "..."
}

// squash replaces runs of sep in s with a single sep.
func squash(s, sep string) string {
	if sep == "" {
		return s
	}
	if !strings.Contains(s, sep+sep) {
		return s
	}
	for strings.Contains(s, sep+sep) {
		s = strings.ReplaceAll(s, sep+sep, sep)
	}
	return s
}
EOF_4
cat > pkg/svc/text_test.go <<'EOF_5'
package svc

import "testing"

func Test_Trunc_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		n    int
		want string
	}{
		{"long", "abcdef", 3, "abc..."},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Trunc(tc.s, tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

func Test_squash_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		sep  string
		want string
	}{
		{"runs", "a--b---c", "-", "a-b-c"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := squash(tc.s, tc.sep)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
EOF_5
