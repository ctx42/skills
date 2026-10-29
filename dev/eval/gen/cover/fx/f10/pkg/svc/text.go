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
