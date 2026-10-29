---
name: cover
description: >
  Improves Vitest coverage of a Vue 3 + TypeScript frontend one function,
  store, or component at a time, counting only each unit's direct tests. Use
  to raise coverage of a function, a component, a line, a file, a directory,
  or the whole frontend, or when asked to add missing unit tests for
  uncovered lines or branches.
license: MIT
argument-hint: "[func=NAME | component=NAME | FILE:LINE | FILE | DIR | all]
  [max=N] [dirs=a,b] [include=all]"
---

# cover

## Usage

```
/web:cover                             the working diff (default), plan-first if several units
/web:cover func=formatDate             one function, composable, or store by name; no plan gate
/web:cover component=DeviceTable       one component; no plan gate
/web:cover src/format.ts:21            the unit enclosing that line
/web:cover src/format.ts               every unit in the file, plan-first
/web:cover src/stores                  every unit in the directory, plan-first
/web:cover all                         every directory, plan-first; fans out when large
/web:cover src max=8                   cap cases added this run
/web:cover all dirs=pages,stores       restrict to these directories
/web:cover func=formatDate include=all also attempt the deferred lines
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
- `../style/references/test.md` and `../style/references/production.md`
  (on-demand: before writing a test — read both files whole, since Test
  inherits every Production rule) — obey them in every test written; do not
  restate them.
- `src/testing.ts` and the unit's existing tests (on-demand: when writing) —
  the fakes, factories, and mount helper the tests must reuse rather than
  rebuild.

## Target

Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. `func=` and `component=` name the
target, not a control. Resolve the frontend root as
`../style/references/checking.md` does (the directory whose `package.json`
depends on `vue`), then one of six kinds; each fixes an order, always worked one
unit at a time:

- diff (default, no target) — every unit whose code the working diff changes
  (`git diff HEAD`; on a branch with no commits, staged then unstaged); files
  alphabetically, units top to bottom. Plan-first when it holds more than one
  unit, else run straight. An empty diff: say so and ask for a target.
- unit — `func=<name>` (an exported function, composable, or `useXxxStore`)
  or `component=<Name>`. Just that one; run straight, then report.
- line — `path/file.ts:42` or `path/Foo.vue:42`: the unit enclosing it; run
  straight.
- file — every unit in the file, top to bottom. Plan-first.
- directory — files alphabetically; units top to bottom. Plan-first.
- all — every directory under `src/` alphabetically (`src` itself first),
  sequentially unless it fans out. Plan-first.

Test helpers (`src/testing.ts`, the setup file), the entry point (`main.ts`),
and the files the coverage config excludes are never units. State the resolved
kind and the unit set before measuring.

## Controls

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

- `max=N` — hard cap on cases added: one per new `test` or `test.each` row;
  a new two-row `test.each` is two, and an assertion added to an existing
  test is none. Under fan-out, give each worker `N` divided by the number of
  directories in scope, rounded down, the remainder one at a time to the
  most-uncovered directory first; a directory whose share is 0 gets no worker
  and is reported as skipped for the cap.
- `dirs=a,b` — restrict `all` to these directories.
- `include=all` — also attempt deferred lines (below) that need more
  scaffolding than `src/testing.ts` offers, built in the test file. A line
  only a production change could reach stays deferred.

Fan-out is automatic: a target spanning several directories with more than ~40
files or ~3000 lines of `.vue`/`.ts` in scope (the threshold `web:style` and
`web:review` use) runs one subagent per directory, each given this file's path
and the two style rule files' paths, merged into one report; a smaller target
runs sequentially.

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
   measures 0% unmeasured; scaffold one, named so, in step 3 — after the
   plan's approval when there is a plan, never before.
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
   assertion — to the unit's own `describe`, stopping at `max`; an assertion
   added to an existing test costs no slot, so it goes in at the cap too.
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

## Plan (diff / file / directory / all)

Run loop steps 1–2 for every unit in scope, then present: whether the run
fans out and why (the file and line count against the threshold); current
coverage per unit; the proposed cases (`test file:describe` and the line each
targets) — under `max`, only as many as it allows, in unit order, with the
easy lines left over listed after them; deferred lines and un-coverable
lines, each as `file:line — reason`. Wait for approval, then run steps 3–4
unit by unit.

## Delegated by web:audit

Delegation is recognized from the invocation, never guessed: `web:audit` says
it is invoking for gaps only and passes the target. A run not told so is not
delegated, and runs its target kind as usual.

Resolve the target, run loop steps 1–2 for every unit in scope, classify each
uncovered statement and branch, and return only the lines below — not Output's
labels or its `web:review` pointer — then stop. Step 1 scaffolds nothing here:
a unit with no direct tests is reported, not measured.
- per unit with a coverable uncovered line: `file:line unit — statements
  covered/total, branches covered/total`, the line being where its declaration
  starts, or `file:line unit — no direct tests` for a unit with none; then each
  coverable uncovered line as `file:line — easy|deferred (reason) —
  branch|statement`, a branch arm counting as `branch`. A unit fully covered,
  or uncovered only on un-coverable lines, gets no line;
- un-coverable lines, counted per directory;
- every command run.

No plan gate, no test written, no Verify, no fan-out — the audit already split
the work, and a worker cannot dispatch one. A control token passed anyway
(`max`, `dirs`, `include`) is ignored, since the target already carries the
scope, and the return says so. Coverage JSON still goes to `tmp/cover/`.

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
- Cases added this run, counted the way `max` counts them, and under a
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
fallback `~/.agent-data/ctx42-skills/lessons/web/cover.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
