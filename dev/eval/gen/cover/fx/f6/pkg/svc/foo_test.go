package svc

import "testing"

func Test_Encode_tabular(t *testing.T) {
	tt := []struct {
		testN string

		v       any
		want    string
		pending bool
	}{
		{"int", 42, "42", false},
		{"string", "a b", `"a b"`, false},
		{"other", 1.5, "1.5", false},
		{"bool", true, "true", true},
		{"int slice", []int{1, 2}, "[1,2]", true},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			if tc.pending {
				skipPending(t)
			}

			// --- When ---
			have := Encode(tc.v)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
