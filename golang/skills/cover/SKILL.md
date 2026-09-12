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
- `../style/SKILL.md` (on-demand: before writing a test — read only its Test
  section) — obey it in every test written; it is the rule spec, do not
  restate it.
- The package's own tests, then a sibling package (on-demand: when writing) —
  for the assertion library and helper conventions the style rules defer to.

## Target

`$1` is the target token; read controls from the rest of `$ARGUMENTS`. Resolve
`$1` to one of five execution kinds (fall back to the user's prose if it is not
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

Read from `$ARGUMENTS`, any order after the target:
- `max_tests=N` — hard cap on tests/cases added this run.
- `packages=a,b` — module mode: restrict to these packages.
- `include=all` — also attempt complex lines (build the fakes/scaffolding);
  un-coverable lines stay reported, never attempted.
- `fanout` — module mode: dispatch one subagent per package (each gets the
  style Test rules and this per-function loop for its package) and merge the
  per-package reports. Use on large modules to keep the main context lean;
  packages are independent, so ordering is preserved per package.

## Per-function loop

For each target function `Foo` (or method `T.Bar`), work in strict order.
**Never start function B until function A's loop is complete and verified.**

1. Map to its direct-test family by style naming: every test whose name
   starts with `Test_Foo` (`Test_Foo`, `Test_Foo_tabular`, `Test_Foo_EdgeCase`,
   …); for a method `T.Bar`, every `Test_T_Bar…`. The prefix plus the
   `($|_)` anchor in step 2 is the whole contract — `Test_Foobar` is not in
   Foo's family. No test in the family, or only off-convention names, means
   the function is uncovered — scaffold `Test_Foo`.
2. Measure in isolation: `go test -run '^Test_Foo($|_)' -coverprofile=<tmp>
   ./<pkg>` (methods: `^Test_T_Bar($|_)`). Read coverage of only Foo's own
   line range from the profile; ignore lines it hits in callees.
3. Classify every uncovered line (next section). Read the style Test section
   and the package's test conventions, then add one targeted case — table row,
   subtest, or assertion — per easy line or branch (complex lines too under
   `include=all`; stop at `max_tests`). Never attempt un-coverable lines.
4. Re-measure once: re-run Foo's direct-test family and re-read the profile;
   confirm Foo's target lines went from 0 to hit. If a target line did not
   rise, bisect — narrow to the case meant to cover it, fix or drop it —
   until every coverable line of Foo is hit or deferred.

## Classify each uncovered line

- easy — reachable with a pure test, a simple branch, an input-triggerable
  error path, an extra table row, or a light fake the project already provides
  (e.g. `tester.Spy`). Cover it now.
- complex — needs heavy scaffolding, concurrency, time, randomness, or
  external I/O. Defer and report; cover only under `include=all`.
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
2. Run `go test -v -race ./<pkg>`; every test in the edited `*_test.go` files
   must show `--- PASS`. Quote the result lines of the tests touched, not the
   full log.

## Un-coverable categories

Never attempt; always name the line and the reason:
- unreachable defensive branches (errors that cannot occur at the call site),
- `init` functions,
- clock, network, hardware, or randomness without an injection seam,
- generated files marked `DO NOT EDIT`,
- panic-only paths with no recoverable contract.

## Output

- Per-function coverage delta (before → after), one row per function in
  scope.
- Tests added: `file:Test_Foo` + what each covers.
- Deferred lines: `file:line — reason`.
- Un-coverable lines: `file:line — reason`.
- Under `max_tests`: what is left.
- Module mode: which packages were covered and which were skipped.
- Never skip a line silently. Suggest running `/review` on the new tests.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/golang/cover.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
