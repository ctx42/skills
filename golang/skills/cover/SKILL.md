---
name: cover
description: >
  Improves Go test coverage one function at a time. Use to raise coverage of a
  function, a line, a file, a package, or a module, or when asked to add
  missing tests for uncovered lines or branches.
license: MIT
argument-hint: "[func=NAME | FILE:LINE | FILE.go | ./pkg* | module]
  [max_tests=N] [packages=a,b] [include=all] [fanout]"
---

# cover

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

Executing skill: it runs `go test -coverprofile`, reads the profile, edits and
creates `*_test.go` files, and re-runs to verify. Unlike `/review` it acts
on the code.

**Governing rule — coverage is per-function, from direct tests only.** A
function's coverage is judged solely by running its own style-named test
family (`Test_Foo…`) in isolation, counting only that function's own lines.
Coverage it picks up from other functions' tests, `-coverpkg`, or a
whole-suite run does not count. The function — never the package — is the
unit of work.

Sources of truth:
- `../style/SKILL.md` (on-demand: before writing a test — read its Test
  section and the Production rules Test inherits, Formatting and Naming
  above all) — obey it in every test written; it is the rule spec, do not
  restate it. Test does not replace Production, it adds to it: a run that
  reads Test alone writes tests that break the 80-column rule, and `gofmt -l`
  does not measure line length, so Verify passes them.
- The package's own tests, then a sibling package (on-demand: when writing) —
  for the assertion library and helper conventions the style rules defer to.
  Test *names* are not among them: style fixes those outright, so a package
  whose tests carry suffixes style does not sanction is a package with a style
  debt, not a local convention to copy.

## Target

The first token of the invocation is the target; read controls from the tokens
after it. Resolve that target to one of five execution kinds (fall back to the
user's prose if it is not
one of the forms below). Each fixes an order; always work it one function/method
at a time.

- function / method — `func=Foo` or `func=T.Bar`. Just that one. Run
  straight (no plan gate), then report.
- line — `path/to/foo.go:42`. Resolve to the enclosing function/method and
  run its full per-function loop. Run straight, then report.
- file — `path/to/foo.go`. Every function/method in the file, top to
  bottom. Plan-first.
- package (default) — a path like `./pkg/foo` or an import path. Files
  alphabetically; within each, functions top to bottom. Plan-first.
- module (opt-in) — `./...`, a `go.mod` dir, or an explicit "module".
  Packages alphabetically, sequentially by default (see `fanout` in
  Controls) — no coverage ranking; within each package, files alphabetically;
  within each file, functions top to bottom. Plan-first.

State the resolved kind and the function/file set before measuring.

## Controls

Read from `$ARGUMENTS`, any order after the target. A token that is not one of
these and is not the target is not a silent no-op: say it was not recognized,
name the controls that exist, and run with the defaults rather than guessing
what it meant.

- `max_tests=N` — hard cap on cases added this run: count one per table row
  or subtest, and one for a test function that holds neither. A new two-row
  table function is two, not three — the wrapper is not itself a case. Turning
  an existing single-case test into a table counts the rows you add, not the
  one that was already there: the cap bounds new coverage, and re-shaping a
  case that already ran adds none. Under
  `fanout` the cap cannot be enforced live across workers, so divide it before
  dispatch: give each worker `N / packages` rounded down (minimum 1), name
  each worker's share in the plan, and report the total actually added against
  `N`. Hand the remainder out one at a time, most-uncovered package first,
  until it is gone.
- `packages=a,b` — module mode: restrict to these packages.
- `include=all` — also attempt complex lines (build the fakes/scaffolding) in
  `*_test.go`, which is the whole of this skill's write scope. A line reachable
  only behind a seam the production code does not have stays deferred even
  under this flag: report what the seam would be and leave it to the author.
  Adding one is an API change, not a test;
  un-coverable lines stay reported, never attempted.
- `fanout` — module mode: dispatch one subagent per package (each gets the
  style Test rules and this per-function loop for its package) and merge the
  per-package reports. Use on large modules to keep the main context lean;
  packages are independent, so ordering is preserved per package.

## Per-function loop

For each target function `Foo` (or method `T.Bar`), work in strict order.
**Never start function B until function A's loop is complete and verified.**
Keep each function's profiles rather than overwriting one scratch file. They go
in a gitignored scratch directory under the module — `tmp/cover/` unless the
user names another — as `<Func>.before` from step 2 and `<Func>.after` from
step 4. Both names are needed, not just the after: the plan runs step 2 for
every function in scope before a line is written, so a single scratch path
makes each function's before-measurement erase the last one, and the deltas the
report owes have nothing behind them. Writing every test first and then
measuring them all produces the same final numbers and the same green suite, so
nothing in the result distinguishes it — the per-function profiles are what do,
and they are also what tells you which case covered which line when one of them
does not.

1. Map to its direct-test family by style naming: every test whose name
   starts with `Test_Foo`, whatever follows it — matching has to find the tests
   that are there; for a method `T.Bar`, every `Test_T_Bar…`. The prefix plus
   the `($|_)` anchor in step 2 is the whole contract — `Test_Foobar` is not in
   Foo's family. What you may **write** is narrower than what this matches:
   style sanctions `Test_Foo` and `Test_Foo_tabular`, so a suffix found in an
   existing family is not a suffix to coin for a new test. A function whose
   tests are all named off-convention (`TestFooFails`) has an empty family and
   measures 0% — an uncovered function to scaffold `Test_Foo` for, and the
   stray name is `golang:style`'s to fix, not this run's.
2. Measure in isolation: `go test -run '^Test_Foo($|_)'
   -coverprofile=tmp/cover/Foo.before ./<pkg>` (methods: `^Test_T_Bar($|_)`).
   Read coverage of only Foo's own line range from the profile; ignore blocks
   belonging to callees. The
   profile's rows are `file:startLine.col,endLine.col stmts count` — one row
   per basic block, not per line, and `stmts` is how many statements that
   block holds.
   Select the rows whose range falls inside Foo, treat `count > 0` as covered,
   and report coverage as covered statements over total, which is what the
   percentages elsewhere count; a rolled-up
   percentage from `go tool cover -func` is per function but is computed from
   whatever ran, so it cannot tell you *which* line is still dark. A family
   that matches nothing prints `no tests to run` and still exits 0 — that is
   an uncovered function, not a clean one, so check the family exists before
   reading a 0% as a measurement.
3. Classify every uncovered line (next section). Read the style Test section
   and the package's test conventions, then add one targeted case — table row,
   subtest, or assertion — per easy line or branch (complex lines too under
   `include=all`; stop at `max_tests`). Never attempt un-coverable lines.
4. Re-measure into `tmp/cover/Foo.after`: re-run Foo's direct-test family and
   re-read the profile;
   confirm Foo's target lines went from 0 to hit. One measurement is the
   expected cost — do not re-measure per case added. If a target line did not
   rise, that is the exception: bisect it — narrow to the case meant to cover
   it, fix or drop it — and re-measure, until every coverable line of Foo is
   hit or deferred.

## Classify each uncovered line

- easy — reachable with a pure test, a simple branch, an input-triggerable
  error path, an extra table row, or a light fake the project already provides
  (e.g. `tester.Spy`). Cover it now.
- complex — needs heavy scaffolding, concurrency, time, randomness, or
  external I/O. Defer and report; cover only under `include=all`. A line a test
  reaches by paying real time or real I/O — waiting out a `time.Sleep`, hitting
  a real socket — is complex, not easy and not un-coverable: nothing is
  unreachable and no seam is missing, so it is the cost that defers it.
- un-coverable — one of the categories below. Never attempt; report with the
  reason.

## Plan (file / package / module)

Run loop steps 1–2 for every function in scope, then present:
- current coverage per function,
- proposed easy cases (`file:Test_Foo` + the line each targets),
- deferred lines (`file:line — reason`),
- un-coverable lines (`file:line — reason`).

Wait for approval, then run steps 3–4 function by function.

## Write

- Extend an existing test when cleanest — a row in a table-driven test, a
  subtest under its `t.Run`; otherwise add a new test func or file.
- When an edit removes a helper's last caller, delete the helper from
  `all_test.go` (the compiler will not flag it); drop the file if it becomes
  empty.

## Verify

End of run, after every function's loop:

1. Run `gofmt -l` on every edited `*_test.go` file; fix any issues.
2. Run `go test -v -race` over every package this run edited — `./<pkg>` for
   one, `./...` for a module or fan-out run. A run that edited nothing has
   nothing to verify: say so and skip both steps rather than reporting a gate
   that guarded no change. Each must pass — a test this
   run never touched going red is still this run's problem, and the most
   likely cause is a helper it edited. Quote only the result lines of the tests
   this run touched; report any other failure as a regression rather than
   quoting the full log.

## Un-coverable categories

Never attempt; always name the line and the reason:
- unreachable defensive branches (errors that cannot occur at the call site),
- `init` functions,
- clock, network, hardware, or randomness that no injection seam can reach —
  a real device, a real wall clock the code reads directly. Where the only
  obstacle is a missing seam, the line is **deferred**, not un-coverable:
  someone can add the seam, and this skill may not (see `include=all`).
  Un-coverable means no test could reach it whatever the author does; deferred
  means not from here.
- generated files marked `DO NOT EDIT`,
- panic-only paths with no recoverable contract. A *documented* panic is a
  contract, not this category: a `MustFoo` that panics by design, or any panic
  the godoc states, is easy — assert it. This category is the undocumented
  defensive `panic("unreachable")` no caller is promised.

## Output

- Per-function coverage delta (before → after), one row per function in
  scope.
- Tests added: `file:Test_Foo` + what each covers.
- Deferred lines: `file:line — reason`.
- Un-coverable lines: `file:line — reason`.
- Cases added this run, counted the way `max_tests` counts them — and under
  `max_tests`, what is left. Report the count on every run, capped or not: it is
  the number the reader checks the tests-added list against, and a run with no
  cap is exactly the run where nobody else is counting.
- Module mode: which packages were covered and which were skipped.
- Never skip a line silently. Suggest running `/review` on the new tests.

Every number in that report is read back off the finished artifact, never
carried from the work: the case count off the tests-added list, each coverage
figure off the function's `.after` profile. The per-function profiles are kept
precisely so this is a lookup and not a recollection.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md`
and `$HOME/.agent-data/ctx42-skills/lessons/golang/cover.md`, the sibling
winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.