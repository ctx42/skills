package cfg

import (
	"errors"
	"testing"
)

func Test_Parse(t *testing.T) {
	// --- Given ---
	line := "name=svc"

	// --- When ---
	have, err := Parse(line)

	// --- Then ---
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := Config{Key: "name", Value: "svc"}
	if have != want {
		t.Errorf("want %+v, have %+v", want, have)
	}
}

func Test_Load(t *testing.T) {
	// --- Given ---
	line := "   "

	// --- When ---
	_, err := Load(line)

	// --- Then ---
	if !errors.Is(err, ErrEmpty) {
		t.Errorf("want ErrEmpty, have %v", err)
	}
}
