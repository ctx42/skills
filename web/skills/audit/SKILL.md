---
name: audit
description: >
  Read-only audit of a Vue 3 + TypeScript frontend across every dimension the
  web skills own in code: correctness, style, and the API contract, unit
  coverage, TSDoc, and end-to-end route coverage. Merges them into one Blocker
  / Should-fix / Nit report naming the command that fixes each finding. Use to
  audit a web app's code, or to find everything it still needs.
license: MIT
argument-hint: "[TARGET | all] [dirs=a,b] [only=review,cover,doc,e2e] [max=N]
  [depth=light|standard*|full] [plan_first]"
---

# audit

## Usage

```
/web:audit                          the working diff (default)
/web:audit all                      the whole frontend
/web:audit src/pages                one directory
/web:audit src/pages/SitePage.vue   one file
/web:audit all dirs=pages,stores    restrict to these directories
/web:audit all only=review,doc      restrict to these dimensions
/web:audit all max=60               cap findings reported (default 40)
/web:audit all depth=light          review depth, passed through
/web:audit all plan_first           propose the budget, then stop
```

Whole-frontend audit. Runs every dimension through the sibling skill that
owns it, merges the results into one findings report, and names on each finding
the command that fixes it. It reports only: it edits no source, applies no fix,
and writes no plan — fixing stays with the owning skills, and turning the
report into a plan or a fix run is the user's next step. Run it again after the
fixes; a `ship` verdict ends the loop.

It owns no rules. Every judgement comes from a sibling; the audit dispatches,
merges, grades, and orders.

Sources of truth (workers load the sibling skills, never this context):
- `../review/SKILL.md` — correctness, the API contract, and style through
  `web:style`; its Output rubric is the grading rubric here, and its Scale
  section the merge for split review work (on-demand: at the merge).
- `../cover/SKILL.md`, `../doc/SKILL.md`, `../e2e/SKILL.md` — unit coverage,
  TSDoc, and route coverage gaps, each through its "Delegated by web:audit"
  section.
- `../style/references/checking.md` (on-demand: before resolving the target)
  — the frontend root, and the pinned style rule-id and severity list for more
  than one review worker.

## Dimensions

- `review` — correctness, the API contract, and style. `style` is never a
  dimension or a worker of its own: `review` delegates to it, so running both
  reports every offense twice.
- `cover` — units (exported functions, composables, stores, components) with
  uncovered lines, measured from direct tests.
- `doc` — TSDoc, component header blocks, and inline comments failing `doc`'s
  checklist.
- `e2e` — routes no spec reaches and controls no spec drives.

The running app's UX and speed are not audited: `web:improve` and `web:perf`
need a live dev server and one visible Chrome window, which parallel workers
cannot share, and each fixes as it measures. The report names them as the next
step.

## Target

Resolve the frontend root as `../style/references/checking.md` does. Read the
tokens in any order: a reserved word is a mode or flag, `key=value` is a
control, and anything else is the target.
- empty — the files under the root that the working diff touches
  (`git diff HEAD`; on a branch with no commits, staged then unstaged):
  `review`, `cover`, and `doc` get the diff, and `e2e` the routes whose page,
  or a component it renders, the diff touches. An empty diff resolves to
  nothing.
- `all` — the whole frontend: every directory under `src/`, plus `e2e/`, and
  every route.
- a directory or a file — those files; `e2e` gets the routes whose page, or a
  component it renders, lies in the target.

## Controls

- `dirs=a,b` — restrict to these directories; `e2e` then gets only the routes
  whose page, or a component it renders, lies in them.
- `only=a,b` — run these dimensions; default all four.
- `max=N` — cap findings reported (default 40), highest severity first.
- `depth=light|standard|full` — passed to `review`; default `standard`.
- `plan_first` — propose the budget, then stop.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

## Budget

Before dispatching, state the root, the target, the file and route counts, the
dimensions, and the worker count. Measure after `dirs=` narrows the target. A
broad target — more than ~40 files or ~3000 lines of `.vue`/`.ts`, the threshold
`web:style` and `web:review` use — switches to `plan_first`: propose that list —
the user's `only=` and `depth=` applied, the rest at their defaults — and stop.
`dirs=` or `max=` skips that automatic proposal, however broad the target:
either is a budget the user already set, though `max` caps only the report.
`only=` and `depth=` alone are not. A typed `plan_first` still proposes and
stops, whatever else is given. Nothing is dispatched before the answer; findings
shown with the proposal have already spent the budget it asks about.

## Dispatch

A subagent cannot dispatch subagents, so the audit splits all the work and no
worker fans out.
- Not broad: one worker per dimension over the whole target.
- Broad: one worker per directory in scope for each of `review`, `cover`, and
  `doc` — `web:review`'s split: `components`, `pages`, `stores`, top-level
  `src`, `e2e`. A directory with nothing for a dimension gets no worker
  (`cover` has no units in `e2e/`). On the diff, each gets its directory's
  share of the diff.
- Always one worker for `e2e`.

When `web:review` puts the API contract in scope for the target, one `review`
worker runs the contract check: the one whose files hold the API client module,
else the top-level `src` one. Its brief says so; no other brief does.

Dispatch them all in one message. Each brief says the worker is delegated by
`web:audit` for findings or gaps only, gives the sibling's `SKILL.md` path to
load (not its text) and its target, and adds:
- `review` — `depth`, no cap, and, with more than one `review` worker, the
  pinned rule-id and severity list, derived once here per `checking.md`; for
  the one worker that runs it, "run the contract check";
- `e2e` — the route set.

Every worker is read-only on source; `cover` writes only its coverage JSON
under `tmp/cover/`.

## Grade

Severities follow `review`'s Output: Blocker / Should-fix / Nit. `review`
findings keep their grade, except a Blocker the Merge regrades; style offenses
keep the tier `web:style` gave them.
- `cover`, one finding per unit: Should-fix when it has no direct tests
  (lines other units' tests run do not count) or an uncovered branch arm; Nit
  when only statement lines are uncovered.
  Un-coverable lines are counted per directory, never findings.
- `doc`, one finding per item: Should-fix for item 3 (inaccurate), or item 1
  (missing) on a module, a component header, or an exported symbol; Nit for
  every other item and every unverifiable flag. Never-touch items are not
  findings.
- `e2e`, one finding per route: Should-fix when no spec reaches it, or a
  control no spec drives writes data or recovers from an error (a submit, a
  delete, a retry), even if it is the only one; Nit when no undriven control
  does either (a sort header, a toggle, a link). Un-coverable gaps are counted
  per route, never findings.
- `cover`, `doc`, and `e2e` never grade a Blocker: a missing test or comment
  is not a wrong result. A test that passes while the code is wrong is
  `review`'s Blocker.

## Merge

1. Check every worker's `file:line` against the file; drop what does not hold
   and count the drops.
2. Split `review` work merges as `review`'s Scale merges its own fan-out: fold
   style by rule id, and regrade every correctness and contract Blocker
   against its Output rubric.
3. Deduplicate across dimensions — the same unit, route, or `file:line` and the
   same concern is one finding, naming both dimensions. The dimension whose
   skill fixes that concern owns it: its grade, its command, its fix-order slot.
   A `review` "reachable branch with no test" on a unit `cover` reported is
   `cover`'s, which measured it, at `cover`'s grade; a `web:style` TSDoc
   offense on an item `doc` reported is `doc`'s.
4. Cap at `max` after deduplicating, highest severity first, fix order
   (below) within a severity.

Each finding names the narrowest invocation of its owning skill that reaches
it:
- correctness and contract — `/web:review <file> fix`; style —
  `/web:style <file> fix`;
- `cover` — `/web:cover <file>:<line>`, any uncovered line of the unit; add
  `include=all` when every uncovered line is deferred;
- `doc` — `/web:doc <file>:<line>`, the line the item starts on;
- `e2e` — `/web:e2e route=<name>`.

## Fix order

Dependency order, not severity: `review` correctness and contract, then style,
then `doc`, then `cover`, then `e2e`. Correctness fixes change code, comments
describe the final code, unit tests cover it, and specs drive the finished
routes last. A `doc`, `cover`, or `e2e` finding on a unit or route that also
has a correctness finding ends with `re-check after <command>`.

## Output

```
Audit: <target> · <F> files · <R> routes · <dimensions> · <W> workers

### Blocker (<n>)
- `file:line` — the problem in one line.
  <dimension>[, rule id] · `<command>`
### Should-fix (<n>)
### Nit (<n>)

### Fix order
1. <one command per directory and dimension, in dependency order>
Then, on the running app: `/web:improve loop`, `/web:perf loop`.

Verdict: <ship | fix-first> per directory; overall.
Counts: severity × dimension.
Budget: depth, and the Nits `depth=light` left out; files and routes audited
and skipped; findings past `max`; findings dropped at the line check.
Ran: <every command the workers ran>.
```

Verdict is fix-first with any Blocker, else ship — counting every finding, one
cut by `max` included. The headings and the Counts line count the findings
listed; Budget names how many went past the cap. Read every count off the
finished report, never carry it from the workers' returns. A dimension with
nothing found says so in one line. The `Ran:` line names `cover`'s Vitest runs:
the audit edits no source, but it does execute the project's tests.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/audit.md` (pass `~` as is, the
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
