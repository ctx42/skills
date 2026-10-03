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

// Abs returns the absolute value of n.
func Abs(n int) int {
	if n < 0 {
		return -n
	}
	return n
}

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

func Test_Abs_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		want int
	}{
		{"negative", -3, 3},
		{"positive", 4, 4},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Abs(tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}

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

// Pad right-pads s with spaces to width w; longer strings are returned as is.
func Pad(s string, w int) string {
	if len(s) >= w {
		return s
	}
	return s + strings.Repeat(" ", w-len(s))
}

// Title upper-cases the first byte of s.
func Title(s string) string {
	if s == "" {
		return s
	}
	return strings.ToUpper(s[:1]) + s[1:]
}

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
EOF_4
cat > pkg/svc/text_test.go <<'EOF_5'
package svc

import "testing"

func Test_Pad_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		w    int
		want string
	}{
		{"short", "ab", 4, "ab  "},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Pad(tc.s, tc.w)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

func Test_Title_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		want string
	}{
		{"empty", "", ""},
		{"word", "go", "Go"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Title(tc.s)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

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
EOF_5
