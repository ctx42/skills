# cover

Improve Go test coverage, one function at a time. It runs the toolchain —
measures coverage, writes the easy tests, re-runs to verify — and reports the
lines it could not cover and why.

**The rule it lives by:** a function's coverage counts only from its own
direct test (the style-named `Test_Foo`), run in isolation, measuring only
that function's own lines. Coverage picked up incidentally from other tests
does not count. The function, not the package, is the unit of work.

It writes tests to the `style` Test rules. Run `/review` after to audit
them.

## Usage

```
/cover func=Foo                       # one function, by name
/cover func=T.Bar                     # one method
/cover pkg/svc/foo.go:42              # function enclosing that line
/cover ./pkg/foo                      # a package, plan-first
/cover module packages=svc,api        # module opt-in, selected packages
/cover func=Bar include=all max_tests=5
```

Targets:
- **single function** (`func=`, or `file.go:line`) — runs straight, no
  approval gate, then reports.
- **package** (default, `./pkg/foo`) — iterates function by function,
  plan-first.
- **module** (`./...`, a `go.mod` dir, or "module") — packages → functions,
  sequentially with no fan-out, plan-first.

## Controls

```
/cover ./pkg/foo max_tests=8          # cap tests added this run
/cover module packages=svc,api        # module mode: restrict packages
/cover func=Foo include=all           # also attempt the deferred hard lines
```

- `max_tests=N` — cap on tests/cases added; reports what is left.
- `packages=a,b` — module mode only; restrict to these packages.
- `include=all` — attempt the deferred complex lines (fakes, scaffolding) too;
  still reports anything genuinely un-coverable.
- `fanout` — module mode only; one subagent per package, merged report. Keeps
  the main context lean on large modules.

## Relationship to style and review

- `style` — the Test rules cover writes to (naming, table tests,
  helpers).
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

### 2. Package target is plan-first

**Request:** `/cover ./pkg/svc` on a package with several partly-covered
functions.

**Expected behavior:**
- States the resolved kind (package) and the function set before measuring.
- Presents a plan — per-function current coverage, proposed easy cases, deferred
  and un-coverable lines — and waits for approval before writing.
- Works one function to completion and verification before starting the next.

### 3. Deferred and un-coverable lines are reported, not skipped silently

**Request:** `/cover func=Dial` where one branch needs a network seam and one
is an unreachable defensive `return`.

**Expected behavior:**
- Covers the easy lines; defers the network branch with a reason; names the
  defensive branch as un-coverable.
- Never attempts the un-coverable line.

### 4. Terse output

**Request:** `/cover func=Foo`.

**Expected behavior:**
- No preamble or narration ("I'll now measure…"); opens with the result.
- Reports the before → after coverage delta, the tests added, and any
  deferred/un-coverable lines — each stated once, with no closing restatement of
  the table just shown.
