package num

import "testing"

func Test_Foo_tabular(t *testing.T) {
	tt := []struct {
		testN string

		n    int
		want string
	}{
		{"positive", 3, "positive"},
	}

	for _, tc := range tt {
		t.Run(tc.testN, func(t *testing.T) {
			// --- When ---
			have := Foo(tc.n)

			// --- Then ---
			if have != tc.want {
				t.Errorf("want %q, have %q", tc.want, have)
			}
		})
	}
}
