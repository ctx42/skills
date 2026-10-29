package api

import "testing"

func Test_Route_tabular(t *testing.T) {
	tt := []struct {
		testN string

		path string
		want string
	}{
		{"page", "/about", "page"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Route(tc.path)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

func Test_Method_tabular(t *testing.T) {
	tt := []struct {
		testN string

		m    string
		want string
	}{
		{"post", "post", "POST"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Method(tc.m)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
