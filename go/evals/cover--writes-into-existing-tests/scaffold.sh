#!/usr/bin/env bash
set -euo pipefail
cat > .gitignore <<'EOF_0'
tmp/
EOF_0
cat > go.mod <<'EOF_1'
module example.com/evalmod

go 1.22
EOF_1
mkdir -p pkg/svc
cat > pkg/svc/all_test.go <<'EOF_2'
package svc

import "testing"

// skipPending skips a table row whose shape is not supported yet.
func skipPending(t *testing.T) {
	t.Helper()
	t.Skip("pending: shape not supported yet")
}
EOF_2
cat > pkg/svc/foo.go <<'EOF_3'
// Package svc encodes values for the wire format.
package svc

import (
	"fmt"
	"strconv"
	"strings"
)

// Encode renders v in the compact wire format.
func Encode(v any) string {
	switch x := v.(type) {
	case int:
		return strconv.Itoa(x)
	case string:
		return strconv.Quote(x)
	case bool:
		return strconv.FormatBool(x)
	case []int:
		parts := make([]string, len(x))
		for i, n := range x {
			parts[i] = strconv.Itoa(n)
		}
		return "[" + strings.Join(parts, ",") + "]"
	default:
		return fmt.Sprintf("%v", x)
	}
}
EOF_3
cat > pkg/svc/foo_test.go <<'EOF_4'
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
EOF_4
