package svc

import "testing"

func Test_Fee_tabular(t *testing.T) {
	tt := []struct {
		testN string

		total int
		want  int
	}{
		{"small order", 500, 250},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Fee(tc.total)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}

func Test_Tax_tabular(t *testing.T) {
	tt := []struct {
		testN string

		amount int
		rate   int
		want   int
	}{
		{"standard", 1000, 8, 80},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Tax(tc.amount, tc.rate)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %d, have %d", tc.want, have)
			}
		})
	}
}
