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
