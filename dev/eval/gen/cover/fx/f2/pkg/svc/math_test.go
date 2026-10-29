package svc

import "testing"

func Test_Abs_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		want int
	}{
		{"negative", -3, 3},
		{"positive", 4, 4},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Abs(tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}

func Test_Clamp_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		lo   int
		hi   int
		want int
	}{
		{"inside", 5, 1, 10, 5},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Clamp(tc.n, tc.lo, tc.hi)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}

func Test_Sign_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		want int
	}{
		{"positive", 7, 1},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Sign(tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}
