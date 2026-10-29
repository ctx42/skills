---
name: audit
description: >
  Read-only audit of a Go project or package across every dimension the go
  skills own: correctness and style, test coverage, godoc, and the API of the
  local libraries it uses. Merges them into one Blocker / Should-fix / Nit
  report naming the command that fixes each finding. Use to audit a Go
  project, or to find everything it still needs.
license: MIT
argument-hint: "[TARGET | all] [packages=a,b] [only=review,cover,doc,reshape]
  [libs=a,b] [max=N] [depth=light|standard*|full] [plan_first]"
---

# audit

## Usage

```
/audit                          the working diff (default)
/audit all                      the current module
/audit /path/to/project         that module (a go.mod dir)
/audit ./pkg/foo                one package
/audit all packages=a,b         restrict to these packages
/audit all only=review,doc      restrict to these dimensions
/audit all libs=must            reshape only these libraries
/audit all max=60               cap findings reported (default 40)
/audit all depth=light          review depth, passed through
/audit all plan_first           propose the budget, then stop
```

Whole-project Go audit. Runs every dimension through the sibling skill that
owns it, merges the results into one findings report, and names on each finding
the command that fixes it. It reports only: it edits no source, applies no fix,
and writes no plan — fixing stays with the owning skills, and turning the
report into a plan or a fix run is the user's next step.

It owns no rules. Every judgement comes from a sibling; the audit dispatches,
merges, grades, and orders.

Sources of truth (workers load the sibling skills, never this context):
- `../review/SKILL.md` — correctness, plus style through `go:style`; its
  Output rubric is the grading rubric here, and its Scale section the merge
  for split review work (on-demand: at the merge).
- `../cover/SKILL.md`, `../doc/SKILL.md` — coverage and godoc gaps, each
  through its "Delegated by go:audit" section.
- `../reshape/SKILL.md` — API proposals for one library.
- `../style/references/checking.md` (on-demand: before dispatching more than
  one review worker) — derives the pinned style rule-id list.

## Dimensions

- `review` — correctness and style. `style` is never a dimension of its own:
  `review` delegates to it, so running both reports every offense twice.
- `cover` — functions with uncovered lines, measured from direct tests.
- `doc` — godoc and inline comments failing `doc`'s checklist.
- `reshape` — API changes to a library the project uses (see Libraries).

## Target

Read the tokens in any order: a reserved word is a mode or flag, `key=value`
is a control, and anything else is the target.
- empty — the packages the working diff touches: `review`, `cover`, and `doc`
  get the diff, and the default reshape picks libraries those packages import.
  An empty diff resolves to nothing.
- `all` — every package of the current module.
- a package pattern (`./...`, `./pkg/...`) or a directory holding `go.mod` —
  those packages, or every package of that module. A path outside the working
  directory is that module; run every command against it there.
- a package path or import path — that one package.

## Controls

- `packages=a,b` — restrict to these packages.
- `only=a,b` — run these dimensions; default all four.
- `libs=a,b` — reshape these libraries (import path or short name), editable
  or not, instead of the default pick.
- `max=N` — cap findings reported (default 40), highest severity first; the
  Library API section is capped separately, 3 proposals per library.
- `depth=light|standard|full` — passed to `review`; default `standard`.
- `plan_first` — propose the budget, then stop.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

## Budget

Before dispatching, state the target, the package list, the dimensions, the
libraries, and the worker count. A broad target — more than ~6 packages and over
~500 lines of Go, the `review`/`style` threshold — switches to `plan_first`:
propose that list with the defaults and stop. `packages=` or `max=` is a budget
the user already set — dispatch without proposing; `only=` and `depth=` alone
are not. Nothing is dispatched before the answer; findings shown with the
proposal have already spent the budget it asks about.

## Libraries

Without `libs=`, reshape the editable modules the target imports: required
through a `replace` to a local path, or used by a `go.work`. Rank them by
import count in scope and take the top 3. The default never picks a package of
the target module itself — that is the project, and `review` covers it; `libs=`
may name one. Name the 3 most-imported modules left out, editable or not, as
"Not reshaped". None editable and no `libs=`: the
dimension has nothing to run; say so in the report.

## Dispatch

A subagent cannot dispatch subagents, so the audit splits all the work and no
worker fans out.
- Not broad: one worker per dimension over the whole target.
- Broad: one worker per package for `review`, `cover`, and `doc` each; on
  the diff, each gets its package's share of the diff.
- Always one worker per library for `reshape`.

Dispatch them all in one message. Each brief says the worker is delegated by
`go:audit` for findings or gaps only, gives the sibling's `SKILL.md` path to
load (not its text) and its target, and adds:
- `review` — `depth`, no cap, and, with more than one `review` worker, the
  pinned rule-id list, derived once here per `checking.md`;
- `reshape` — `<lib> max=3`, plus `packages=<a,b>` naming the packages in
  scope when they are narrower than the module; it is read-only already and
  returns its Output.

Every worker is read-only on source; `cover` writes only its profiles under
`tmp/cover/`.

## Grade

Severities follow `review`'s Output: Blocker / Should-fix / Nit. `review`
findings keep their grade; style offenses keep the tier `go:style` gave them.
- `cover`, one finding per function: Should-fix when it has no direct tests or
  an uncovered error-path or branch line; Nit when only statement lines are
  uncovered. Un-coverable lines are counted per package, never findings.
- `doc`, one finding per item: Should-fix for item 3 (inaccurate), or item 1
  (missing) on the package or an exported symbol; Nit for every other item and
  every unverifiable flag. Never-touch items are not findings.
- `cover` and `doc` never grade a Blocker: a missing test or comment is not a
  wrong result. A test that passes while the code is wrong is `review`'s
  Blocker.
- `reshape` proposals change another module, so they are not graded here;
  they keep `reshape`'s High / Med in their own section.

## Merge

1. Check every worker's `file:line` against the file; drop what does not hold
   and count the drops.
2. Split `review` work merges as `review`'s Scale merges its own fan-out: fold
   style by rule id, reconcile the spread, and regrade every correctness
   Blocker against its Output rubric.
3. Deduplicate across dimensions — the same function or `file:line` and the
   same concern is one finding, with the higher grade, naming both dimensions.
   A `review` "reachable branch with no test" on a function `cover` reported
   is `cover`'s, which measured it; a `go:style` godoc offense on an item `doc`
   reported is `doc`'s.
4. Cap at `max` after deduplicating, highest severity first, fix order
   (below) within a severity.

Each finding names the narrowest invocation of its owning skill that reaches
it:
- correctness — `/go:review <pkg> fix`; style — `/go:style <pkg> fix`;
- `cover` — `/go:cover <file>:<line>`, any uncovered line of the function;
  add `include=all` when every line is complex;
- `doc` — `/go:doc <file>:<line>` for an inline comment or an existing godoc
  (its first line); `/go:doc <file>` for a missing one.

## Fix order

Dependency order, not severity: library API changes, then `review`
correctness, then style, then `doc`, then `cover`. API changes move call
sites, correctness fixes change code, comments describe the final code, and
tests come last so they cover it. A `doc` or `cover` finding on a function that
also has a correctness finding, or that holds a call site a reshape proposal
rewrites, ends with `re-check after <command>`.

## Output

```
Audit: <target> · <P> packages · <dimensions> · <W> workers

### Blocker (<n>)
- `file:line` — the problem in one line.
  <dimension>[, rule id] · `<command>`
### Should-fix (<n>)
### Nit (<n>)

### Library API (reshape)
| # | Library | Change (archetype) | Reach | Impact | Breakage |
Not reshaped: <modules>

### Fix order
1. Library API changes, in each library's own module.
2. <one command per package and dimension, in dependency order>

Verdict: <ship | fix-first> per package; overall.
Counts: severity × dimension.
Budget: depth; packages audited and skipped; findings past `max`;
findings dropped at the line check.
Ran: <every command the workers ran>.
```

Verdict is fix-first with any Blocker, else ship — counting every finding, one
cut by `max` included. The headings and the Counts line count the
findings listed; Budget names how many went past the cap. Read every count off
the finished report, never carry it from the workers' returns. A dimension with
nothing found says so in one line. The `Ran:` line names `cover`'s `go test`
runs: the audit edits no source, but it does execute the project's tests.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/go/audit.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
