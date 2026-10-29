---
name: cover
description: >
  Improves Go test coverage one function at a time. Use to raise coverage of a
  function, a line, a file, a package, or a module, or when asked to add
  missing tests for uncovered lines or branches.
license: MIT
argument-hint: "[func=NAME | FILE:LINE | FILE.go | ./pkg | all] [max=N]
  [packages=a,b] [include=all]"
---

# cover

## Usage

```
/cover                          the functions the working diff touches (default)
/cover func=Foo                 one function by name; no plan gate
/cover func=T.Bar               one method
/cover pkg/svc/foo.go:42        the function enclosing that line
/cover pkg/svc/foo.go           every function in the file, plan-first
/cover ./pkg/foo                one package, per function, plan-first
/cover all                      every package of the module, plan-first
/cover /path/to/project         that module (a go.mod dir)
/cover ./pkg/foo max=8          cap tests/cases added this run
/cover all packages=svc,api     restrict to these packages
/cover func=Foo include=all     also attempt the deferred complex lines
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
  reads Test alone writes tests that break the line-limit rule, and `gofmt -l`
  does not measure line length, so Verify passes them.
- The package's own tests, then a sibling package (on-demand: when writing) —
  for the assertion library and helper conventions the style rules defer to.
  Test *names* are not among them: style fixes those outright, so a package
  whose tests carry suffixes style does not sanction is a package with a style
  debt, not a local convention to copy.

## Target

Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. `func=` names the target, not a
control. Resolve the target to one of six execution kinds (fall back to the
user's prose if it is not one of the forms below). Each fixes an order; always
work it one function/method at a time.

- diff (default: no target) — every function/method in a non-test `.go` file
  whose lines the working diff adds or changes: `git diff HEAD`, or on a branch
  with no commits, the staged then the unstaged diff. Files alphabetically;
  within each, functions top to bottom. Plan-first when it holds more than one
  function; one runs straight. An empty diff: say so and ask for a target.
- function / method — `func=Foo` or `func=T.Bar`. Just that one. Run
  straight (no plan gate), then report.
- line — `path/to/foo.go:42`. Resolve to the enclosing function/method and
  run its full per-function loop. Run straight, then report.
- file — `path/to/foo.go`. Every function/method in the file, top to
  bottom. Plan-first.
- package — a path like `./pkg/foo` or an import path. Files
  alphabetically; within each, functions top to bottom. Plan-first.
- module — `all` (every package of the current module), a package pattern
  (`./...`, `./pkg/...`), or a `go.mod` dir. Packages alphabetically,
  sequentially unless large (below) — no coverage ranking; within each
  package, files alphabetically; within each file, functions top to bottom.
  Plan-first.

State the resolved kind and the function/file set before measuring.

Fan-out is automatic, never asked for: when the target spans more than ~6
packages and more than ~500 lines of Go in scope, dispatch one subagent per
package (under `max=`, per package whose share is above 0; each gets the style
Test rules and this per-function loop for its package) and merge the
per-package reports. It keeps the main context lean; packages are independent,
so ordering is preserved per package. The plan says it will fan out and why —
the package and line counts that crossed the threshold.

## Controls

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

- `max=N` — hard cap on cases added this run: count one per table row or
  subtest, and one for a test function that holds neither. A new two-row
  table function is two, not three — the wrapper is not itself a case. Turning
  an existing single-case test into a table counts the rows you add, not the
  one that was already there: the cap bounds new coverage, and re-shaping a
  case that already ran adds none. Under fan-out the cap cannot be enforced
  live across workers, so divide it before dispatch: give each worker
  `N / packages` rounded down, name each worker's share in the plan, and
  report the total actually added against `N`. Hand the remainder out one at
  a time, most-uncovered package first, until it is gone. The cap wins over
  coverage: a package whose share is 0 gets no worker — with more packages
  than `N`, only the `N` most-uncovered run, one case each. Once the workers
  report, any share left unused goes, in one follow-up dispatch, to packages
  that still have easy lines, most-uncovered first; the total still never
  passes `N`.
- `packages=a,b` — module kind: restrict to these packages.
- `include=all` — also attempt complex lines (build the fakes/scaffolding) in
  `*_test.go`, which is the whole of this skill's write scope. A line reachable
  only behind a seam the production code does not have stays deferred even
  under this flag: report what the seam would be and leave it to the author.
  Adding one is an API change, not a test;
  un-coverable lines stay reported, never attempted.

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
   stray name is `go:style`'s to fix, not this run's.
2. Measure in isolation: `go test -run '^Test_Foo($|_)'
   -coverprofile=tmp/cover/Foo.before ./<pkg>` (methods: `^Test_T_Bar($|_)`).
   Read coverage of only Foo's own line range from the profile; ignore blocks
   belonging to callees. The
   profile's rows are `file:startLine.col,endLine.col stmts count` — one row
   per basic block, not per line, and `stmts` is how many statements that
   block holds.
   Select the rows whose start line lies inside Foo's range and sum `stmts` by
   script, never by eye from a grep window — a hand tally picks up a
   neighbouring function's block. Treat `count > 0` as covered,
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
   `include=all`; stop at `max=`). Never attempt un-coverable lines.
4. Re-measure into `tmp/cover/Foo.after`: re-run Foo's direct-test family and
   re-read the profile;
   confirm Foo's target lines went from 0 to hit. One measurement is the
   expected cost — do not re-measure per case added. If a target line did not
   rise, that is the exception: bisect it — narrow to the case meant to cover
   it, fix or drop it — and re-measure, until every coverable line of Foo is
   hit or deferred, or `max=` is reached. A fixed case replaces the one
   it fixes and does not count again; a dropped case is not added, so it
   frees its slot.

## Classify each uncovered line

- easy — reachable with a pure test, a simple branch, an input-triggerable
  error path, an extra table row, or a light fake the project already provides
  (e.g. `tester.Spy`). Cover it now.
- complex — needs heavy scaffolding, concurrency, time, randomness, or
  external I/O. Defer and report; cover only under `include=all`. A line a test
  reaches by paying real time or real I/O — waiting out a `time.Sleep`, hitting
  a real socket — is complex, not easy and not un-coverable: nothing is
  unreachable and no seam is missing, so it is the cost that defers it. A fake
  the test must write itself is complex too, however small, even against an
  existing seam (a package `dialer` var).
- un-coverable — one of the categories below. Never attempt; report with the
  reason.

## Plan (diff / file / package / module)

Run loop steps 1–2 for every function in scope, then present:
- fan-out, when the target is large: that it will, why, and each worker's
  `max=` share,
- current coverage per function,
- proposed easy cases (`file:Test_Foo` + the line each targets),
- deferred lines (`file:line — reason`),
- un-coverable lines (`file:line — reason`).

Wait for approval, then run steps 3–4 function by function: `Foo.after` is
measured before any test for the next function is written, even when one batch
would be quicker.

## Delegated by go:audit

Delegation is recognized from the invocation, never guessed: `go:audit` says
it is invoking for gaps only and passes the target. A run not told so is not
delegated, and runs its target kind as usual.

Resolve the target, run loop steps 1–2 for every function in scope, classify
each uncovered line, and return, then stop:
- per function with a coverable uncovered line: `file:line Func — covered/total
  stmts`, or `0/total — no direct tests` for an empty family; then each such
  line as `file:line — easy|complex (reason) — error-path|branch|statement`.
  A line deferred behind a missing seam is listed here as complex, reason
  `seam`, never counted as un-coverable.
  error-path: reached only when an error is returned or handled; branch:
  reached only on one arm of an `if`, `switch`, or `select`; statement:
  anything else. Fully covered functions get no line;
- un-coverable lines, counted per package;
- every command run.

No plan gate, no test written, no Verify, no fan-out — the audit already split
the work, and a worker cannot dispatch one; a control token passed anyway is
ignored, and the return says so. Profiles still go to `tmp/cover/`.

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

Use the labels below verbatim ("Deferred lines:", not "Left for later"):
readers and callers scan for them.

- Per-function coverage delta (before → after), one row per function in
  scope.
- Tests added: `file:Test_Foo` + what each covers; one bullet per case added,
  table rows nested under their test function, so the list counts.
- Deferred lines: `file:line — reason`.
- Un-coverable lines: `file:line — reason`.
- Cases added this run, counted the way `max=` counts them — and under
  `max=`, what is left. Report the count on every run, capped or not: it is
  the number the reader checks the tests-added list against, and a run with no
  cap is exactly the run where nobody else is counting.
- Module kind: which packages were covered and which were skipped.
- Never skip a line silently. Suggest running `/review` on the new tests.

Every number in that report is read back off the finished artifact, never
carried from the work: the case count off the tests-added list, each coverage
figure off the function's `.after` profile. The per-function profiles are kept
precisely so this is a lookup and not a recollection.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/go/cover.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
