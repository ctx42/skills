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
