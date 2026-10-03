#!/usr/bin/env bash
set -euo pipefail
git init -q
git config user.email eval@example.com
git config user.name Eval
git config commit.gpgsign false
mkdir -p go/skills/style
cat > go/skills/style/SKILL.md <<'EOF_0'
---
name: style
description: >
  Enforced Go coding style for this project (production and test code).
license: MIT
---

# style

Authoritative Go style rules. Apply the Production section to `*.go` and the
Test section to `*_test.go`; Test inherits Production unless a Test rule
overrides it. Per-rule detection detail lives in [rules.md](rules.md).

Change the rules only through `go:review`; never hand-edit them.

## Production

### Formatting

- gofmt + goimports always; never hand-format or reorder imports manually.
- Separate multi-line switch cases with a blank line; none before the first.

### Naming

- No name stutter: `pkg.Thing`, not `pkg.PkgThing`.
- Receivers are a short type abbreviation, never a single letter: `pag *page`,
  `cfg *config`.

### Functions & methods

- A func whose sole parameter is a local `*T`/`T` belongs on T as a method
  (`pag.f()`, not `f(pag)`).
- No naked returns in non-trivial functions.

### Errors

- Wrap errors with `%w` and add context; never swallow the error.
- Match errors with `errors.Is`/`errors.As`, never `==`.

### API design

- `context.Context` is the first parameter when used; never store it in a
  struct.
- Assert implementations at compile time: `var _ Iface = (*T)(nil)` near the
  top of the file.
- No work in `init()`; no package-level mutable state or singletons.

## Test

### Structure

- Structure every test body with the `--- Given ---`, `--- When ---`, and
  `--- Then ---` comment markers, in order.
- Table-driven subtests via `t.Run`; one case per table row.

### Naming

- Test function names are `Test_Func` and `Test_Type_Method`; add `_tabular`
  for table tests.
- Name the actual value `have` and the expected value `want`, never `got`.

### Helpers & fixtures

- Test helpers call `t.Helper()`.
- Simple test helpers shared within a package live in `all_test.go`.
EOF_0
mkdir -p go/skills/style
cat > go/skills/style/rules.md <<'EOF_1'
# Go style — deep rules

Keyed detection detail for the rules in `SKILL.md` (same directory). An entry
adds only what a capable reviewer can't infer from the one-line rule — an
exemption or a detection heuristic — in two short sentences. Open an entry only
when about to flag its rule; never preload the file. Grows via
`go:review add`.

## Contents

- No name stutter (Production)
- Method over a single-receiver-arg func (Production)
- Assert implementations at compile time (Production)
- Test helpers in all_test.go (Test)

## No name stutter (Production)

Exemption: a name fixed by a contract outside the package, such as a method
another type is asserted against. Detect: a member repeating its type or
package qualifier (`client.ClientDo`) with no same-file pin.

## Method over a single-receiver-arg func (Production)

Exemption: the arg is one of several equals with no clear receiver. Detect: an
unexported func with a single local-type parameter.

## Assert implementations at compile time (Production)

Exemption: an unexported type only ever used through its concrete type. Detect:
a type passed as an interface with no `var _ Iface = (*T)(nil)` in its file.

## Test helpers in all_test.go (Test)

Exemption: a helper used by one test file only may stay beside it. Detect: a
helper declared in a `_test.go` file other than `all_test.go` and called from
two or more test files.
EOF_1
cat > go.mod <<'EOF_2'
module example.com/pollr

go 1.22
EOF_2
mkdir -p poll
cat > poll/poll.go <<'EOF_3'
// Package poll fetches readings from remote stations on a fixed interval.
package poll

import (
	"context"
	"time"
)

// Fetcher reads the current value of one item.
type Fetcher interface {
	Fetch(ctx context.Context, name string) (float64, error)
}

// Poller fetches every item on a fixed interval.
type Poller struct {
	ctx      context.Context
	fet      Fetcher
	items    []string
	interval time.Duration
}

// Run polls until the context is cancelled.
func (pol *Poller) Run(out chan<- float64) error {
	for {
		select {
		case <-pol.ctx.Done():
			return pol.ctx.Err()
		case <-time.After(pol.interval):
			for _, name := range pol.items {
				val, err := pol.fet.Fetch(pol.ctx, name)
				if err != nil {
					return err
				}
				out <- val
			}
		}
	}
}

// Summary lists the polled items, comma separated.
func (pol *Poller) Summary() string {
	s := ""
	for i, name := range pol.items {
		if i > 0 {
			s += ", "
		}
		s += name
	}
	return s
}
EOF_3
git add -A
git commit -qm 'initial'
mkdir -p poll
cat > poll/poll.go <<'EOF_0'
// Package poll fetches readings from remote stations on a fixed interval.
package poll

import (
	"context"
	"strings"
	"time"
)

// Fetcher reads the current value of one item.
type Fetcher interface {
	Fetch(ctx context.Context, name string) (float64, error)
}

// Poller fetches every item on a fixed interval.
type Poller struct {
	fet      Fetcher
	stations []string
	interval time.Duration
}

// Run polls until the context is cancelled.
func (pol *Poller) Run(ctx context.Context, out chan<- float64) error {
	tick := time.NewTicker(pol.interval)
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-tick.C:
			for _, name := range pol.stations {
				val, err := pol.fet.Fetch(ctx, name)
				if err != nil {
					return err
				}
				out <- val
			}
		}
	}
}

// Summary lists the polled stations, comma separated.
func (pol *Poller) Summary() string {
	var buf strings.Builder
	for i, name := range pol.stations {
		if i > 0 {
			buf.WriteString(", ")
		}
		buf.WriteString(name)
	}
	return buf.String()
}
EOF_0
