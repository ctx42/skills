package util

import "testing"

func Test_Name(t *testing.T) {
	// --- Given ---
	n := 1

	// --- When ---
	have := Name(n)

	// --- Then ---
	if have != "util" {
		t.Errorf("want %q, have %q", "util", have)
	}
}
