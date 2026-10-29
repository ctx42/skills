package svc

import (
	"errors"
	"testing"
)

func Test_Upload(t *testing.T) {
	// --- Given ---
	var body []byte

	// --- When ---
	err := Upload(body)

	// --- Then ---
	if !errors.Is(err, ErrEmpty) {
		t.Errorf("want ErrEmpty, have %v", err)
	}
}
