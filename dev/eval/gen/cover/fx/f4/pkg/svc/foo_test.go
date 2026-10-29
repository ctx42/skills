package svc

import "testing"

func Test_Addr(t *testing.T) {
	// --- Given ---
	s := Settings{Host: "db", Port: 5432}

	// --- When ---
	have := Addr(s)

	// --- Then ---
	if have != "db:5432" {
		t.Errorf("want %q, have %q", "db:5432", have)
	}
}

func Test_Load(t *testing.T) {
	// --- Given ---
	line := "db:5432"

	// --- When ---
	have, err := Load(line)

	// --- Then ---
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	want := Settings{Host: "db", Port: 5432}
	if have != want {
		t.Errorf("want %+v, have %+v", want, have)
	}
}

func Test_Store(t *testing.T) {
	// --- Given ---
	s := Settings{Host: "db", Port: 1}

	// --- When ---
	have := Store(s)

	// --- Then ---
	if have != "db:1" {
		t.Errorf("want %q, have %q", "db:1", have)
	}
}
