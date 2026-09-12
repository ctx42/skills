---
name: review
description: >
  Done-time Go quality review: checks finished code — the current diff, a
  package, or a whole module — against the project style rules and for
  general correctness (bugs, edge cases, error handling). Use after edits or
  a feature are complete, and to add, change, or learn style rules from
  feedback.
license: MIT
argument-hint: "[TARGET* | add|change|remove RULE | learn] [packages=a,b]
  [max_issues=N] [depth=light|standard*|full] [plan_first] [fix]"
---

# review

Done-time review for Go code. Read the invocation from `$ARGUMENTS`; `$1` is
the first token. Pick the mode from it:

- Check (default) — a target token or empty input; audit finished code.
- Rule edit — `$1` is `add`/`change`/`remove`, or the input is a plain style
  preference.
- Learn — `$1` is `learn`; mines the current editing session (since the last
  /clear) for convention feedback and proposes rules.

Sources of truth:
- `golang:style` (on-demand: Check mode) — owns the style rules and their
  detection; the whole style dimension is delegated to it.
- `../style/SKILL.md`, `../style/rules.md` (on-demand: Rule-edit/Learn) — the
  terse rules and their keyed detection detail; those modes write here.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Working diff (injected)

!`git diff HEAD`

The Check target when `$1` is empty; a named target ignores it.

## Check mode

### Target

`$1` is the target token:
- empty — review the injected working diff; if it is empty, fall back to the
  current git diff vs the base branch (staged + unstaged).
- a package — a path like `./pkg/foo` or an import path; review that one
  package's `.go` files.
- a module / many packages — `./...`, a directory containing `go.mod`, or an
  explicit "module"; review every package in the module.

State the resolved target and the exact package/file set before reviewing.

### Budget & scope

Read these controls from `$ARGUMENTS` (any order, after the target):
- `packages=a,b` — restrict to these packages within the target.
- `max_issues=N` — hard cap on findings reported (default 25); stop there,
  highest severity first.
- `depth=light|standard|full` — default `standard`. `light` reports only
  blockers and major maintainability with minimal examples; `full` reviews
  everything deeply — use sparingly.
- `plan_first` — produce a short prioritized plan plus the top findings, then
  stop for approval before the full pass.
- `fix` — after reviewing, apply the findings (see Applying fixes).

Default to plan-first: if the target is broad (whole module, many packages, or
large LOC) and no budget was given, switch to `plan_first` automatically,
propose defaults (the caps above, the package list), and ask before the full
review.

### Workflow

1. Resolve the target and budget (above) and list the packages/files in scope.
2. Style dimension — invoke `golang:style` with the resolved target and budget
   (`packages`, `max_issues`, `depth`), instructing it to report offenses only.
   Take its offense list as the style findings; do not re-derive style rules
   here.
3. Review each file for what style does not cover, in this order:
   - Correctness: bugs, wrong logic, nil/bounds, ignored errors, data races.
   - Edge cases: empty/large/concurrent inputs and every error path.
   - Error handling & API: wrapping, sentinels, boundaries, easy misuse.
   - Never report a form the style rules require as a defect: the `"" +`
     segmented multi-line string is the mandated style (raw strings break
     indentation); never propose a backtick raw string for it.
   - Cross-boundary verify (`depth=standard`+): before reporting a claim that
     reaches beyond the diff — a symbol is unused, all callers handle an
     error/nil, an interface is fully implemented, a suspect branch is
     reachable — confirm it with the `LSP` tool (`findReferences`,
     `goToImplementation`, `incomingCalls`, `hover`/`goToDefinition`) rather
     than asserting from the visible code. Skip at `depth=light`; reserve for
     findings that cross a file/package boundary. No language server → fall
     back to grep/read and note the reduced confidence in the finding.
4. Reason only: do not run gofmt, go vet, golangci-lint, or go test — judge by
   reading the code. `LSP` is allowed (read-only navigation).
5. Merge the style offenses with the correctness findings and report (below).
   Do not change code unless asked.

### Scale

- Single package or small module (<= ~6 packages): review in this context,
  package by package, highest-risk first.
- Larger module (> ~6 packages): fan out one review subagent per package (each
  invokes `golang:style` on its package for the style offenses and reviews
  correctness itself, with the `depth` and a share of `max_issues`), then
  synthesize one merged report, re-ranking findings to the global `max_issues`
  cap.
- If the target is too large, do the highest-risk packages first and name the
  skipped ones in the report; never silently truncate.

### Output

Group by severity: Blocker / Should-fix / Nit. Each finding:
- `file:line` — the problem in one line.
- The rule id or dimension (e.g. `style: %w`, `correctness`).
- A minimal suggested fix.

End with a one-line verdict (ship / fix-first) and the per-severity counts. For
a module, give the verdict per package plus an overall summary. Report budget
usage: `depth`, packages/files reviewed, and how many findings went unreported
past `max_issues`.

### Applying fixes

When asked to change code (apply findings, fix, refactor), read
[references/fixing.md](references/fixing.md) first and follow it.

## Rule-edit and Learn modes

When either mode triggers, read
[references/rule-editing.md](references/rule-editing.md) first and follow it;
never write a rule without confirmation.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/golang/review.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
