---
name: perf
description: >
  Makes a running web app faster one measured, committed fix at a time:
  profiles its UI in a visible Chrome at a 4x CPU slowdown and fixes slow
  interactions, long tasks, layout shift, memory leaks, wasted requests, and
  bundle bloat without changing what users see. Use to speed up or profile a
  web app, page, or interaction, front end or back end.
argument-hint: "[auto] [loop] [max=N] [<focus>]"
license: MIT
---

# perf

## Usage

```
/web:perf                   measure the app, build the top fix, stop for commit, drop, or a prompt
/web:perf auto              the same, committing without stopping
/web:perf loop              one change after another until the stop rule
/web:perf auto loop max=5   unattended, at most 5 commits
/web:perf <focus>           do what the focus asks to the part it names or a screenshot shows
```

Modes and controls come first, in any order; the first other word starts the
focus, which runs to the end — reserved words in it are text. A pasted image, or
an image path in the focus, shows the part. `max=N` counts change commits only
(a `docs(perf): never` one included; not drops, discards, or the final check's)
and needs `loop`: given without it, say "`max` needs `loop`" and stop before any
other step. Without `loop` a run makes at most one change. No focus measures the
whole app. The CPU slowdown is always 4x.

A `key=value` that names no control here, or a word left over once the modes and
the focus are read: say it was not recognized, name the ones that exist, and run
with the defaults as if it were absent — unless dropping it would widen what the
run changes; then ask. A focus that resolves to nothing: say so and ask — never
guess what to work on.

Arguments: $ARGUMENTS

Report tersely: no preamble or narration; state each fact once. Committing
each kept change is this skill's job, whatever rule forbids an agent to
commit; never push, amend, rebase, or touch a commit the run did not make.

Write every code change to `../style/references/production.md`, plus
`../style/references/test.md` for a test, an e2e spec, or a benchmark, each
read once before the first edit it governs, a comment-only edit included;
the project's checks stay the gate, and no `web:style` pass runs here.

The goal is code that runs faster or uses less memory, never at the cost of
architecture, readability, or testability (section 5).

## 1. Start — before any edit

Check in order. The first that fails is named as the missing prerequisite and
the run stops, editing and committing nothing:

1. The working directory is a web app's source tree: markup, styles, or
   scripts the app serves, beside a manifest or dev config (`package.json`, a
   framework or bundler config, a `Makefile` target that serves it).
2. A dev server is reachable. Never start one, even when the config says how.
   Find its URL as [references/start.md](references/start.md#dev-server) says
   (read it before this step); nothing listening: stop.
3. Chrome DevTools MCP is available and its window is visible, checked as
   [references/start.md](references/start.md#chrome) says; a `HeadlessChrome`
   user agent means headless.
4. The craft plugin is installed: `craft:cm` is in your skill list.

Then:

5. Record the start commit (`git rev-parse HEAD`) and the dirty files
   (`git status --porcelain`). Make a scratch directory outside the repo
   (`mktemp -d`); every build, trace, snapshot, and capture of the run goes
   there, never into the tree.
6. Back end: the server answering the app's API
   ([references/start.md](references/start.md#back-end)), if its source is in
   this repo. Back-end edits are on only when its dev setup live-reloads;
   otherwise every back-end idea goes to Recommendations.
7. Build: the repo's build command
   ([references/start.md](references/start.md#build)). It runs only with its
   output pointed at the scratch directory. No build command, or no way to
   redirect its output: skip bundle and leak findings and say so under Not
   measured.
8. Find the project's checks as
   [references/start.md](references/start.md#checks) says. The targeted checks
   are the static ones plus the tests covering the files a change touches; the
   full checks are all of them. Run the full checks once on the untouched tree;
   a check already red there is known, gated as that section says.
9. Send one message and wait, as
   [references/start.md](references/start.md#message) says. The start asks
   nothing else.

## 2. Measure

Every measurement runs under `emulate` with `cpuThrottlingRate: 4`, passed
every time ([references/measure.md](references/measure.md#setup)), and no
network throttling, except heap snapshots: those run at
`cpuThrottlingRate: 1` ([references/measure.md](references/measure.md#leaks)).
Interactions, a view's load (its long tasks and layout shift), and API calls
are measured on the dev server; bundle size only from the scratch build, never
from the dev server. How to take each number:
[references/measure.md](references/measure.md).

Scope: with no focus, every page reachable from the app's navigation (its
shared header, sidebar, menus, and footer); with a focus, only the views that
show the focused part. Play with each view the way a user reads it
([references/measure.md](references/measure.md#exploring)). Never click
logout, nor trigger a write — a POST, PUT, PATCH, or DELETE — unless the focus
names that flow. Watch the network log after every action; a write seen outside
a named flow means that control is never used again this run and goes under
Not measured.

Findings — a timed one exists only while past its threshold:

- Slow interaction: INP over 200 ms.
- Long task: over 50 ms during an interaction or a view's load.
- Layout shift: CLS over 0.1.
- Leak: a view whose heap size in bytes, compiled code aside, after a forced
  GC, grows by more than 50 KB on every one of 5 navigate-away-and-back cycles;
  read [references/measure.md](references/measure.md#leaks) before the first
  cycle.

A counted one is a finding at every instance:

- A duplicate request or sequential independent calls
  ([references/measure.md](references/measure.md#network)).
- A route or library in the first-load bundle that could load lazily, or a
  library imported whole
  ([references/measure.md](references/measure.md#bundle)).

Noise: a timed metric is measured 5 times and its median used; a counted one
once. A change is kept only when its after median beats the before median by
more than the spread (max − min) of the 5 before runs; for a counted metric any
reduction counts. A leak fix is kept by the leak rule in
[references/measure.md](references/measure.md#leaks). A change with a
benchmark is also kept by the keep rule in
[references/benchmarks.md](references/benchmarks.md). A change with no gain
beyond that is discarded and listed under Dropped, "no measurable gain" —
a focus instruction included.

Before choosing a change, search the source for `PERF:` comments
(`grep -rn 'PERF:'`, skipping dependency and build dirs). A `PERF:` comment is
the only binding previous decision: it states what never to do at the code it
sits on. Never act against one unless the focus asks for what it forbids
(section 4); a finding it forbids goes to Recommendations, citing the
comment. Test assertions and earlier commits do not bind. A `UX:` comment
governs what users see, which no commit here changes, so it never blocks a fix
(section 11 flags it).

Rank, top first:

1. Timed findings, the worst ratio of value to threshold first; a leak ranks
   above every other timed finding.
2. Network waste: duplicate requests and sequential calls.
3. Bundle findings.
4. Within a tier, shared chrome (header, navigation, footer, a layout every
   page uses) and the landing page before deeper pages; ties go to the
   smaller change.

## 3. Back end

Back-end code in this repo may change, its API included, only when start step
6 turned back-end edits on. APIs outside the repo are never changed: what would
help there (a field, a batch call, caching headers) goes to Recommendations as
feedback for their owners.

Two calls merge into one endpoint only as
[references/merge-rule.md](references/merge-rule.md) allows; read it before
merging or recommending a merge. Never bundle unrelated resources for one page.

After a back-end edit, wait for the reload as
[references/measure.md](references/measure.md#back-end-reload) says before
measuring.

## 4. Focus

A focus is an instruction about one part of the UI; with one, read
[references/focus.md](references/focus.md) before the first change: it beats a
`PERF:` comment, may name a visible change, and keeps every commit to that part.

## 5. What a change may be

- **Nothing the user sees changes.** Pagination, virtualization, debounce
  delays, new loading placeholders, and reordered content go to
  Recommendations unless a focus names them. Content appearing sooner is the
  goal, not a change. Proof: the visible-change check in
  [references/measure.md](references/measure.md#visible-change-check) passes
  on every view the change touches.
- **Tests.** Every code path a change adds — a cache and its invalidation, a
  merged endpoint, a lazy boundary — gets unit or integration tests in the
  same commit.
- **Benchmarks.** A gain in code that runs in isolation (a function or
  handler) also gets a benchmark, written first and run before and after as
  [references/benchmarks.md](references/benchmarks.md) says.
- **Never, for speed:** duplicate or inline logic, bypass a layer (a handler
  querying storage directly, a component calling an API a store owns), add
  global mutable state, weaken or delete a test, or hand-roll what the
  framework provides (`computed`, `useMemo`, lazy routes, async components).
- Before committing, reread the diff against the project's conventions
  (`AGENTS.md`, `CLAUDE.md`, the linters). A gain that needs one of these
  rules broken goes to Recommendations, naming the rule.

## 6. Change cycle

One commit per performance change. One rule applied in several places is one
commit; unrelated changes never share a commit. Per change:

1. Pick the top-ranked finding not dropped this run, not forbidden by a
   `PERF:` comment (a focus instruction beats one, section 4), allowed by
   sections 3 to 5, and touching no file the start found dirty (that one goes
   to Recommendations, naming the file — a focus instruction included).
2. Before any edit, take the 5 before measurements of the finding's metric and
   the visible-change check's two before captures of each view the change will
   touch. A focus-named visible change skips that check (step 6) and takes
   pictures as [references/focus-pictures.md](references/focus-pictures.md)
   says.
3. Make the smallest change that fixes the finding, with its tests and any
   benchmark (section 5).
4. Run the targeted checks right after the edit, on exit status, never on
   piped or filtered output; the full checks wait for the final check. A
   check red that was green at the start gets one repair;
   still red: under `auto`, discard the change and list it under Dropped with
   the failing check; interactive, show the failure at the stop.
5. Reload (wait for the back end, section 3) and take the 5 after
   measurements. No gain beyond the noise: discard the change (restore its
   files, delete its new files) and list it under Dropped, "no measurable
   gain".
6. Run the visible-change check; a mismatch discards the change and lists the
   idea under Recommendations as a visible change.
7. Interactive: stop (section 8). `auto`: commit.
8. Commit as
   [references/commit-message.md](references/commit-message.md#committing)
   says: stage by path, then in one command re-run the targeted checks, each
   gated on exit status, and commit. A red re-run commits nothing and returns
   to step 4, one repair per change in all.

## 7. Commit message

Invoke `craft:cm` at `mini` on the staged diff for the summary and body, then
append the `Perf-` fields as
[references/commit-message.md](references/commit-message.md) says; read it
before the first commit. Never add a trailer beyond what `cm` allows.

## 8. Interactive stops

Without `auto`, stop once per change, after building, measuring, and checking
it; read [references/stops.md](references/stops.md) before the first stop: the
stop message and its replies (`commit`, `drop`, a prompt, "never …", stop).

## 9. Loop and stop rule

With `loop`, go on after each commit or drop as
[references/loop.md](references/loop.md) says (read it then), until nothing
the run may fix is left or `max` change commits are made. Without `loop`, stop
after one change, committed, dropped, or discarded. Every stop runs the final
check (section 10), whose repair or revert still commits, then reports.

## 10. Final check

After the last change, run the full checks as
[references/final-check.md](references/final-check.md) says; skip this when
the run committed no code (a `docs(perf): never` commit alone is none). A check
red that was green at the start is bisected to its commit, repaired once
keeping the gain, else reverted.

## 11. Report

Read every count and hash off `git log <start>..HEAD`, never from memory.
Interactive runs end with the same report. Read
[references/end-of-run.md](references/end-of-run.md) before writing it; every
finding left goes under Recommendations.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/perf.md` (pass `~` as is, the
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
