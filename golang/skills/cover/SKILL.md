---
name: cover
description: >
  Improves Go test coverage one function at a time. Runs the toolchain:
  measures each function via its own direct test only, then adds the easy
  cases (rows, subtests, light fakes) until every coverable line is hit.
  Plan-first for a file, package, or module; runs straight for a single
  function or line.
  Reports deferred and un-coverable lines with reasons. Honors max_tests,
  packages, include=all.
license: MIT
---

# cover

Executing skill: it runs `go test -coverprofile`, reads the profile, edits and
creates `*_test.go` files, and re-runs to verify. Unlike `/review` it acts
on the code.

**Governing rule — coverage is per-function, from direct tests only.** A
function's coverage is judged solely by running its own style-named test
(`Test_Foo`) in isolation, counting only that function's own lines. Coverage a
function picks up incidentally from other functions' tests does not count. The
function — never the package — is the unit of work.

Sources of truth:
- `../style/SKILL.md` — Test rules; obey them in every test written.
- The package's own tests, then a sibling package, for assertion/helper
  conventions.

## Target

Resolve the invocation to one of five execution kinds. Each fixes an order;
always work it one function/method at a time.

- **function / method** — `func=Foo` or `func=T.Bar`. Just that one. Run
  straight (no plan gate), then report.
- **line** — `path/to/foo.go:42`. Resolve to the enclosing function/method and
  run its full per-function loop. Run straight, then report.
- **file** — `path/to/foo.go`. Every function/method in the file, **top to
  bottom**. Plan-first.
- **package** (default) — a path like `./pkg/foo` or an import path. Files
  **alphabetically**; within each, functions **top to bottom**. Plan-first.
- **module** (opt-in) — `./...`, a `go.mod` dir, or an explicit "module".
  Packages **alphabetically and sequentially** — no coverage ranking, no
  fan-out; within each package, files alphabetically; within each file,
  functions top to bottom. Plan-first.

State the resolved kind and the function/file set before measuring.

## Controls

- `max_tests=N` — hard cap on tests/cases added this run; report what is left.
- `packages=a,b` — module mode: restrict to these packages.
- `include=all` — also attempt the deferred complex lines (build the needed
  fakes/scaffolding); still report anything un-coverable.

Plan-first applies to file, package, and module targets; function and line
targets run straight.

## Per-function loop

For each target function `Foo` (or method `T.Bar`), work in strict order.
**Never start function B until function A's loop is complete and verified.**

1. **Map to its direct-test family** by style naming: every test whose name
   starts with `Test_Foo` (`Test_Foo`, `Test_Foo_tabular`, `Test_Foo_EdgeCase`,
   …); for a method `T.Bar`, every `Test_T_Bar…`. This `Test_Foo` prefix family
   is the only contract for "directly tests Foo" — a different function
   `Foobar` is excluded by the `_`/end-of-name anchor below. No test in the
   family, or only off-convention names, means the function is **uncovered** —
   scaffold `Test_Foo`.
2. **Measure in isolation:** `go test -run '^Test_Foo($|_)'
   -coverprofile=<tmp> ./<pkg>` (methods: `^Test_T_Bar($|_)`). Read coverage of
   **only Foo's own line range** from the profile; ignore lines it hits in
   callees.
3. **Add the targeted cases** — table rows, subtests, or assertions, each aimed
   at a specific uncovered line or branch (easy or light-fake only, unless
   `include=all`; respect `max_tests`). Defer lines needing heavy scaffolding,
   concurrency, time, randomness, or external I/O (report them); never attempt
   un-coverable lines.
4. **Re-measure once.** Re-run Foo's direct-test family and re-read the profile;
   confirm Foo's target lines went from 0 to hit. If some target line did not
   rise, bisect — narrow to the case meant to cover it, fix or drop it — until
   every coverable line of Foo is hit or deferred.

Do not use `-coverpkg` or whole-suite coverage to credit Foo — it breaks the
direct-test rule.

## Classify each uncovered line

- **easy** — reachable with a pure test, a simple branch, an
  input-triggerable error path, an extra table row, or a light fake the
  project already provides (e.g. `tester.Spy`). Cover it now.
- **complex (deferred)** — needs heavy scaffolding, concurrency, time,
  randomness, or external systems. Skip on the default pass; report. Cover it
  only under `include=all`.
- **un-coverable** — see the list below. Never attempt; report with the
  reason.

## Plan (file / package / module)

Before writing, present:
- current coverage per function in scope,
- proposed easy cases (`file:Test_Foo` + the line each targets),
- deferred lines (`file:line — reason`),
- un-coverable lines (`file:line — reason`).

Wait for approval. Then write and verify, following the per-function loop:
finish and verify one function before starting the next.

## Write

- Edit existing tests when cleanest: add a row to a table-driven test, insert a
  subtest under the existing `t.Run`. Otherwise add a new test func or file.
- Put any new shared test helper in the package's `all_test.go` (create it if
  absent); never scatter helpers across individual `_test.go` files.
- When an edit removes a helper's last caller, delete the now-unused helper
  from `all_test.go` (the Go compiler will not flag it); drop `all_test.go`
  entirely if it becomes empty.
- Mirror the package's own test conventions; if none, a sibling package's; if
  none anywhere, follow style Test rules with the project tester lib
  (`tester.T` / `tester.Spy`).
- Obey style Test rules: `Test_Func` / `Test_Type_Method` naming, `_tabular`
  for table tests, `t.Run` subtests, `t.Helper()` in helpers, subtest-name
  charset `[a-zA-Z0-9 _-]` with `/` for hierarchy.
- Respect `max_tests`.

## Verify

- Per function: re-run its direct-test family (must pass) and confirm its
  coverage rose (check the profile, not just the headline percentage).
- End of run — final pass:
  1. Run `gofmt -l` on every edited `*_test.go` file; fix any issues.
  2. Run `go test -v -race ./<pkg>` and display the full output. Every
     `Test_Foo` in the target `*_test.go` file must appear as `--- PASS`.
  3. Present the before/after coverage table, one row per function in scope.

## Module mode

Walk packages **alphabetically and sequentially** — no coverage ranking, no
subagent fan-out. Within each package, files alphabetically; within each file,
functions top to bottom. The `packages` filter restricts which packages run;
`max_tests` caps the whole run. Report which packages were covered and which
were skipped.

## Un-coverable categories

Never attempt; always name the line and the reason:
- unreachable defensive branches (errors that cannot occur at the call site),
- `init` functions,
- clock, network, hardware, or randomness without an injection seam,
- generated files marked `DO NOT EDIT`,
- panic-only paths with no recoverable contract.

## Output

- Per-function coverage delta (before → after).
- Tests added: `file:Test_Foo` + what each covers.
- Deferred lines: `file:line — reason`.
- Un-coverable lines: `file:line — reason`.
- Never skip a line silently. Suggest running `/review` on the new tests.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.
