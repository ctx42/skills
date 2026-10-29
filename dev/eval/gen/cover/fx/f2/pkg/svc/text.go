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
