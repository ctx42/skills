#!/usr/bin/env bash
set -euo pipefail
mkdir -p tmp
touch tmp/.gitkeep
mkdir -p calc
(
cd calc
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/calc

go 1.22
EOF_0
cat > calc.go <<'EOF_1'
// Package calc does integer arithmetic.
package calc

// Div returns a divided by b.
func Div(a, b int) int {
	return a / b
}
EOF_1
cat > calc_test.go <<'EOF_2'
package calc

import "testing"

func TestDiv(t *testing.T) {
	if have := Div(6, 3); have != 2 {
		t.Fatalf("have %d, want 2", have)
	}
}
EOF_2
mkdir -p tmp/agent
cat > tmp/agent/agent-bug-div-zero.md <<'EOF_3'
# Bug: Div panics on zero

`Div(1, 0)` panics with "integer divide by zero". Change `Div` to `func Div(a, b int) (int, error)` and return the exported `ErrDivZero` when `b` is 0. No other code calls `Div`.
EOF_3
cat > .gitignore <<'EOF_4'
tmp/
EOF_4
go vet ./... && go test ./... >/dev/null
git add -A
git commit -qm 'initial'
)
mkdir -p text
(
cd text
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
cat > go.mod <<'EOF_0'
module example.com/text

go 1.22
EOF_0
cat > text.go <<'EOF_1'
// Package text holds string helpers.
package text

import "strings"

// Trim removes leading and trailing spaces.
func Trim(s string) string {
	return strings.TrimSpace(s)
}
EOF_1
cat > text_test.go <<'EOF_2'
package text

import "testing"

func TestTrim(t *testing.T) {
	if have := Trim("  a  "); have != "a" {
		t.Fatalf("have %q, want %q", have, "a")
	}
}
EOF_2
cat > README.md <<'EOF_3'
# text

Helpers to recieve and clean strings.
EOF_3
mkdir -p tmp/agent
cat > tmp/agent/agent-plan-text.md <<'EOF_4'
# Text helpers

## Summary

| #  | Item             | Status |
|----|------------------|--------|
| 1  | Add Trim         | N      |
| 2  | Add Upper        | N      |
| 3  | Remove this plan | N      |

Legend: Y implemented · N not yet · X rejected

## 1. Add Trim — [ ]

Add `Trim(s string) string` that removes leading and trailing spaces.

Done when: `TestTrim` passes.

## 2. Add Upper — [ ]

Add `Upper(s string) string` returning `strings.ToUpper(s)`.

Done when: `TestUpper` passes.

## 3. Remove this plan — [ ]

When every other item is `Y` or `X`, ask the user whether to delete this file.
EOF_4
mkdir -p tmp/agent
cat > tmp/agent/agent-dept-docs.md <<'EOF_5'
# Docs debt

## Open

- `README.md` misspells "receive" as "recieve".

## Notes, not debt

None.
EOF_5
cat > .gitignore <<'EOF_6'
tmp/
EOF_6
go vet ./... && go test ./... >/dev/null
git add -A
git commit -qm 'initial'
)
