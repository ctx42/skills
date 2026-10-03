package svc

import "testing"

func Test_Trunc_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		n    int
		want string
	}{
		{"long", "abcdef", 3, "abc..."},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Trunc(tc.s, tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

func Test_squash_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		sep  string
		want string
	}{
		{"runs", "a--b---c", "-", "a-b-c"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := squash(tc.s, tc.sep)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
