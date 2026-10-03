package net

import (
	"errors"
	"testing"
)

func Test_Dial_emptyAddress(t *testing.T) {
	// --- Given ---
	addr := ""

	// --- When ---
	have, err := Dial(addr)

	// --- Then ---
	if !errors.Is(err, ErrNoAddr) {
		t.Errorf("want ErrNoAddr, have %v", err)
	}
	if have != nil {
		t.Errorf("want nil conn, have %v", have)
	}
}
