package svc

import "testing"

func Test_Pad_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		w    int
		want string
	}{
		{"short", "ab", 4, "ab  "},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Pad(tc.s, tc.w)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

func Test_Title_tabular(t *testing.T) {
	tt := []struct {
		testN string

		s    string
		want string
	}{
		{"empty", "", ""},
		{"word", "go", "Go"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Title(tc.s)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}

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
