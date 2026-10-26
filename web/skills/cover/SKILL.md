---
name: cover
description: >
  Improves Vitest coverage of a Vue 3 + TypeScript frontend one function,
  store, or component at a time, counting only each unit's direct tests. Use
  to raise coverage of a function, a component, a line, a file, a directory,
  or the whole frontend, or when asked to add missing unit tests for
  uncovered lines or branches.
license: MIT
argument-hint: "[func=NAME | component=NAME | FILE:LINE | FILE | DIR* | all]
  [max_tests=N] [dirs=a,b] [include=all] [fanout]"
---

# cover

## Usage

```
/web:cover src/stores                  directory (default): per unit, plan-first
/web:cover func=formatDate             one function, composable, or store by name; no plan gate
/web:cover component=DeviceTable       one component; no plan gate
/web:cover src/format.ts:21            the unit enclosing that line
/web:cover src/format.ts               every unit in the file, plan-first
/web:cover all                         every directory, sequential, plan-first
/web:cover src max_tests=8             cap cases added this run
/web:cover all dirs=pages,stores       restrict to these directories
/web:cover func=formatDate include=all also attempt the deferred lines
/web:cover all fanout                  one subagent per directory, merged
```

Executing skill: it runs Vitest with coverage, reads the coverage JSON, edits
and creates `*.test.ts` files, and re-runs to verify. Unlike `web:review` it
acts on the code. End-to-end coverage of routes is `web:e2e`'s.

**Governing rule — coverage is per unit, from direct tests only.** A unit is
an exported function, composable, or store (with its actions) in a `.ts`
module, or a component (`Foo.vue`). Its coverage is judged solely by running
its own tests in isolation, counting only its own lines: for a `.ts` unit,
the `describe("<name>")` blocks in its module's colocated test file; for a
component, `Foo.test.ts`. Coverage a unit picks up from a caller's tests or a
parent component's tests does not count. The unit — never the file or the
directory — is the unit of work. Never lower the project's coverage
thresholds.

Sources of truth:
- `../style/SKILL.md` (on-demand: before writing a test — its Test section
  and the Production rules Test inherits) — obey it in every test written; do
  not restate it.
- `src/testing.ts` and the unit's existing tests (on-demand: when writing) —
  the fakes, factories, and mount helper the tests must reuse rather than
  rebuild.

## Target

The first token is the target; controls follow it. Resolve the frontend root
as `../style/references/checking.md` does (the directory whose `package.json`
depends on `vue`), then one of five kinds; each fixes an order, always worked
one unit at a time:

- unit — `func=<name>` (an exported function, composable, or `useXxxStore`)
  or `component=<Name>`. Just that one; run straight, then report.
- line — `path/file.ts:42` or `path/Foo.vue:42`: the unit enclosing it; run
  straight.
- file — every unit in the file, top to bottom. Plan-first.
- directory (default) — files alphabetically; units top to bottom.
  Plan-first.
- all — every directory under `src/` alphabetically (`src` itself first),
  sequentially unless `fanout`. Plan-first.

Test helpers (`src/testing.ts`, the setup file), the entry point (`main.ts`),
and the files the coverage config excludes are never units. State the resolved
kind and the unit set before measuring.

## Controls

Read from `$ARGUMENTS`, any order after the target. A token that is none of
these: say it was not recognized, name the controls, and run with defaults.

- `max_tests=N` — hard cap on cases added: one per new `test` or
  `test.each` row; a new two-row `test.each` is two, and an assertion added
  to an existing test is none. Under `fanout`, give each worker `N` divided
  by the number of directories in scope, rounded down, the remainder one at
  a time to the most-uncovered directory first; a directory whose share is 0
  gets no worker and is reported as skipped for the cap.
- `dirs=a,b` — restrict `all` to these directories.
- `include=all` — also attempt deferred lines (below) that need more
  scaffolding than `src/testing.ts` offers, built in the test file. A line
  only a production change could reach stays deferred.
- `fanout` — `all` only: one subagent per directory, each given this file's
  path and `../style/SKILL.md`'s, merged into one report.

## Per-unit loop

For each unit, in strict order. **Never start unit B until unit A's loop is
complete and verified.** A plan-first target runs steps 1–2 for every unit
before the plan (below); the one-at-a-time rule governs steps 3–4. Keep each
unit's coverage JSON in a scratch directory git ignores — `<scratch>` below:
`tmp/cover/` at the repository root, as an absolute path, unless the user
names another, added to `.git/info/exclude` when no ignore rule covers it — as
`<unit>.before/` from step 2 and `<unit>.after/` from step 4.

1. Map to its direct tests: a `.ts` unit's `describe` blocks whose title is
   its name, exactly or followed by a space, in the test file beside its
   module; a component's `Foo.test.ts`. No such block or file: the unit
   measures 0% — scaffold one, named so.
2. Measure in isolation, from the frontend root:

   ```
   bunx vitest run <test file> -t '^<name>( |$)' --coverage
     --coverage.include=<unit's file> --coverage.reporter=json
     --coverage.reportsDirectory=<scratch>/<unit>.before
     --coverage.thresholds.lines=0 --coverage.thresholds.functions=0
     --coverage.thresholds.branches=0 --coverage.thresholds.statements=0
   ```

   (one command line; a component drops `-t`). The thresholds are zeroed for
   this measurement only, so a partial run does not fail on them; the
   config is never edited. A `-t` that matches nothing still exits 0 with
   every test skipped — that is an uncovered unit, not a clean one.
   Read `coverage-final.json` by script, never by eye: for a `.ts` unit, the
   statements and branches whose start line lies inside the unit's `fnMap`
   range; for a component, the whole file. Covered means a count above 0,
   and each arm of a branch (each entry of its `b` list) counts as one;
   report covered over total, statements and branches.
3. Classify every uncovered statement and branch (below). Then add one
   targeted case per easy line or branch — a `test.each` row, a `test`, an
   assertion — to the unit's own `describe`, stopping at `max_tests`.
4. Re-measure into `<scratch>/<unit>.after/` and confirm every target went
   from 0 to hit. A target still dark: narrow to the case meant to cover it,
   fix or drop it, re-measure. A fixed case replaces the one it fixes; a
   dropped case frees its slot.

## Classify each uncovered line

- easy — reachable through the unit's inputs, props, emitted events, the fake
  `fetch` answers, or another fake `src/testing.ts` already offers
  (`stalled()`, `networkError()`, `blockedStorage()`). Cover it now.
- deferred — needs a fake or harness the project lacks (a fake clock beyond
  `vi.useFakeTimers`, a held answer the helpers do not build, a third-party
  module mock), or layout and sizes happy-dom does not compute (that line is
  `web:e2e`'s). Cover only under `include=all`, except layout. A line only a
  production change could reach is deferred too; both report under
  Deferred lines, naming `web:e2e` or the change.
- un-coverable — never attempt; report the line and the reason:
  - a defensive branch no input can reach (a `??` fallback on a value the
    type and every caller guarantee);
  - a build-time branch (`import.meta.env.DEV`, `import.meta.env.PROD`);
  - generated files.

## Plan (file / directory / all)

Run loop steps 1–2 for every unit in scope, then present: current coverage
per unit, the proposed cases (`test file:describe` and the line each targets)
— under `max_tests`, only as many as it allows, in unit order, with the easy
lines left over listed after them — deferred lines, and un-coverable lines,
each as `file:line — reason`. Wait
for approval, then run steps 3–4 unit by unit.

## Write

- Extend the unit's existing `describe` when it has one — a `test.each` row,
  a `test` — else add the `describe` to the colocated test file, creating
  `Foo.test.ts` for a component that has none.
- Reuse `src/testing.ts`; a fake two tests need goes there, documented, never
  copied into a test file.
- Test what the user or caller observes (the rendered DOM, an emitted event,
  a returned value, a request sent), never a component's internals through
  `wrapper.vm`.

## Verify

End of run: run `bun run check` (Biome, `vue-tsc`, Vitest) and then
`bun run coverage` from the frontend root; both must pass — a test this run
never touched going red is still this run's problem. A run that edited
nothing has nothing to verify: say so. Never lower a threshold to pass; when
the measured totals now sit above them, say by how much and leave raising
them to the user.

## Output

Use the labels below verbatim; readers scan for them.

- Per-unit coverage (before → after), statements and branches, one row per
  unit in scope.
- Tests added: `test file:describe` + what each case covers; `test.each` rows
  nested under their test, so the list counts.
- Deferred lines: `file:line — reason`.
- Un-coverable lines: `file:line — reason`.
- Cases added this run, counted the way `max_tests` counts them, and under a
  cap, what is left.
- `all`: which directories were covered and which skipped.
- Never skip a line silently. Suggest running `web:review` on the new tests.

Every number is read off the finished artifacts — the case count off the
tests-added list, each coverage figure off the unit's `.after` JSON — never
carried from the work. Report tersely: no preamble or narration; state each
fact once.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/cover.md` (pass `~` as is,
the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
