# cover

Improve Go test coverage one function at a time, from direct tests only.

## Usage

```
/cover ./pkg/foo                package (default): per function, plan-first
/cover func=Foo                 one function by name; no plan gate
/cover func=T.Bar               one method
/cover pkg/svc/foo.go:42        the function enclosing that line
/cover pkg/svc/foo.go           every function in the file, plan-first
/cover module                   every package, sequential, plan-first
/cover ./pkg/foo max_tests=8    cap tests/cases added this run
/cover module packages=svc,api  module mode: restrict to these packages
/cover func=Foo include=all     also attempt the deferred complex lines
/cover module fanout            module mode: one subagent per package, merged
```

It runs the toolchain — measures coverage, writes the easy tests, re-runs to
verify — and reports the lines it could not cover and why.

The rule it lives by: a function's coverage counts only from its own direct
test (the style-named `Test_Foo`), run in isolation, measuring only that
function's own lines. Coverage picked up incidentally from other tests does
not count. The function, not the package, is the unit of work.

## Controls

- `max_tests=N` — cap on tests/cases added; reports what is left.
- `packages=a,b` — module mode only; restrict to these packages.
- `include=all` — attempt the deferred complex lines (fakes, scaffolding) too;
  still reports anything genuinely un-coverable.
- `fanout` — module mode only; one subagent per package, merged report. Keeps
  the main context lean on large modules.

## Relationship to style and review

- `style` — the Test rules cover writes to (naming, table tests,
  `have`/`want`, helpers).
- `cover` — adds the missing tests and measures the result.
- `review` — run it after to review the new tests for correctness and style.

## Evaluations

### 1. Single function, measured in isolation

**Request:** `/cover func=Parse` where `Parse` has one happy-path test and
two uncovered error branches.

**Expected behavior:**
- Runs straight (no plan gate), mapping to the `Test_Parse` direct-test family.
- Measures with `-run '^Test_Parse($|_)'` and reads only `Parse`'s own line
  range — does not credit coverage from callers' tests.
- Adds table rows aimed at the two error branches, re-measures, and confirms
  those lines went 0 → hit.
- The new rows follow the style Test rules: `have`/`want` names, never `got`;
  error-path subtests named `error - <condition>`.

### 2. Package target is plan-first

**Request:** `/cover ./pkg/svc` on a package with several partly-covered
functions.

**Expected behavior:**
- States the resolved kind (package) and the function set before measuring.
- Presents a plan — per-function current coverage, proposed easy cases,
  deferred and un-coverable lines — and waits for approval before writing.
- Works one function to completion and verification before starting the next.

### 3. Deferred and un-coverable lines are reported, not skipped silently

**Request:** `/cover func=Dial` where one branch needs a network seam and one
is an unreachable defensive `return`.

**Expected behavior:**
- Covers the easy lines; defers the network branch with a reason; names the
  defensive branch as un-coverable.
- Never attempts the un-coverable line.
- Re-run with `include=all`: builds the fake for the network branch and covers
  it; the defensive `return` is still reported as un-coverable, not attempted.

### 4. Line target resolves to its function and runs straight

**Request:** `/cover pkg/svc/foo.go:42` where line 42 sits inside `Load`.

**Expected behavior:**
- Resolves the target to `Load` and states the kind (line) and function.
- Runs `Load`'s full per-function loop without a plan gate.
- Measures with `-run '^Test_Load($|_)'`, never with whole-package coverage.

### 5. Module mode honors packages, fanout, and the cap

**Request:** `/cover module packages=svc,api fanout max_tests=5`.

**Expected behavior:**
- Touches only `svc` and `api`; dispatches one subagent per package and
  merges their reports, listing packages covered and skipped.
- Adds at most five tests/cases across the run and reports what is left.
- Each subagent still finishes and verifies one function before the next.

### 6. Writes into existing tests and cleans up helpers

**Request:** `/cover pkg/svc/foo.go` where `Test_Encode_tabular` exists and a
helper in `all_test.go` loses its last caller during the edit.

**Expected behavior:**
- Adds rows to `Test_Encode_tabular` rather than a parallel test function.
- Deletes the now-unused helper from `all_test.go`; drops the file if empty.
- Ends with `gofmt -l` clean and `go test -v -race` showing `--- PASS` for
  every test in the edited files.

### 7. Terse output

**Request:** `/cover func=Foo`.

**Expected behavior:**
- No preamble or narration ("I'll now measure…"); opens with the result.
- Reports the before → after coverage delta, the tests added, and any
  deferred/un-coverable lines — each stated once, with no closing restatement
  of the table just shown.
- Quotes only the `--- PASS` lines of the tests touched, not the full
  `go test -v` log.
