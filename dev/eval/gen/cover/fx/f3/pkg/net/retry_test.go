package net

import "testing"

func Test_Retry_firstTry(t *testing.T) {
	// --- Given ---
	calls := 0
	fn := func() error { calls++; return nil }

	// --- When ---
	err := Retry(3, fn)

	// --- Then ---
	if err != nil {
		t.Errorf("want nil error, have %v", err)
	}
	if calls != 1 {
		t.Errorf("want 1 call, have %d", calls)
	}
}
