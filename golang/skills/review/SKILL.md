---
name: review
description: >
  Done-time Go quality review: checks finished code — the current diff, a
  package, or a whole module — against the project style rules and for
  general correctness (bugs, edge cases, error handling). Use after edits or
  a feature are complete, and to add, change, or learn style rules from
  feedback.
license: MIT
argument-hint: "[TARGET* | add RULE | remove RULE | learn]
  [packages=a,b] [max_issues=N] [depth=light|standard*|full] [plan_first] [fix]"
---

# review

Final-gate review for Go code. Read the invocation from `$ARGUMENTS`; `$1` is
the first token. Pick the mode from it:

- Check (default) — a target token or empty input; audit finished code.
- Rule edit — `$1` is `add`/`change`/`remove`, or the input is a plain style
  preference.
- Learn — `$1` is `learn`; mines the current editing session (since the last
  /clear) for convention feedback and proposes rules.

Sources of truth:
- `../style/SKILL.md` (eager) — canonical terse rules (Production + Test).
- `rules.md` — the **Principles** section is read each check (the reasoning
  backbone); keyed entries are on-demand per rule. Deeper rationale / examples
  / how-to-detect, keyed to those rules.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Working diff (injected)

!`git diff HEAD`

This is the default review target when `$1` is empty. A package or module
invocation (`$1` names a path / `./...` / a `go.mod` dir) ignores this diff and
reads the named target instead.

## Check mode

### Target

`$1` is the target token:
- **empty** — review the injected working diff (above); if it is empty, fall
  back to the current git diff vs the base branch (staged + unstaged).
- **a package** — a path like `./pkg/foo` or an import path; review that one
  package's `.go` files.
- **a module / many packages** — `./...`, a directory containing `go.mod`, or
  an explicit "module"; review every package in the module.

State the resolved target and the exact package/file set before reviewing.

### Budget & scope

Read these controls from `$ARGUMENTS` (any order, after the target):
- `packages=a,b` — restrict to these packages within the target.
- `max_issues=N` — hard cap on findings reported (default 25).
- `depth=light|standard|full` — default `standard`.
- `plan_first` — produce a short prioritized plan plus the top findings, then
  stop for approval before the full pass.
- `fix` — after reviewing, apply the findings (see Applying fixes).

Default to plan-first: if the target is broad (whole module, many packages, or
large LOC) and no budget was given, switch to `plan_first` automatically,
propose defaults (the caps above, the package list), and ask before the full
review.

Depth:
- `light` — only blockers and major maintainability; minimal examples.
- `standard` — balanced coverage of the target.
- `full` — deep review of everything; use sparingly.

Stop at `max_issues`; report highest-severity first and say how many findings
were left unreported.

### Workflow

1. Resolve the target and budget (above) and list the packages/files in scope.
2. Read `style`'s `SKILL.md` in full and skim `rules.md`'s **Principles**
   section. Reason from those principles; open a specific keyed `rules.md` entry
   only when about to flag its rule — never preload the whole file.
3. Review each file, in this order:
   - Rules: every applicable style rule (Production for `*.go`, Test for
     `*_test.go`); use `rules.md` for detection detail.
   - Correctness: bugs, wrong logic, nil/bounds, ignored errors, data races.
   - Edge cases: empty/large/concurrent inputs and every error path.
   - Error handling & API: wrapping, sentinels, boundaries, easy misuse.
   - Cross-boundary verify (`depth=standard`+): before reporting any claim
     that reaches beyond the diff — a symbol is unused, all callers handle an
     error/nil, an interface is fully implemented, a suspect branch is
     reachable — confirm it with the `LSP` tool (`findReferences`,
     `goToImplementation`, `incomingCalls`, `hover`/`goToDefinition`) instead of
     asserting from the visible code. Skip at `depth=light`; reserve for
     findings that actually cross a file/package boundary, not every line. If no
     Go language server is configured the tool errors — fall back to grep/read
     and note the reduced confidence in the finding.
4. Reason only. Do not run gofmt, go vet, golangci-lint, or go test — judge by
   reading the code. The `LSP` tool is permitted: it is read-only semantic
   navigation, not the build/test toolchain, and does not mutate code.
5. Report findings (below). Do not change code unless asked.

### Scale

- Single package or small module (<= ~6 packages): review in this context,
  package by package, highest-risk first.
- Larger module (> ~6 packages): fan out one review subagent per package
  (each gets `style`, `rules.md`, the `depth`, and a share of `max_issues`),
  then synthesize one merged report, re-ranking findings to the global
  `max_issues` cap. Keeps the main context lean.
- Always report which packages were reviewed and which were skipped; never
  silently truncate — if the target is too large, do the highest-risk packages
  first and say what you skipped.

### Output

Group by severity: **Blocker / Should-fix / Nit**. Each finding:
- `file:line` — the problem in one line.
- The rule id or dimension (e.g. `style: %w`, `correctness`).
- A minimal suggested fix.

End with a one-line verdict (ship / fix-first) and the per-severity counts. For
a module, give the verdict per package plus an overall summary. Report budget
usage: `depth`, packages/files reviewed, and whether you stayed under
`max_issues` (and how many findings went unreported).

### Applying fixes

When asked to change code (apply findings, fix, refactor), read
[references/fixing.md](references/fixing.md) first and follow it. Check mode
itself stays reason-only.

## Rule-edit and Learn modes

When either mode triggers, read
[references/rule-editing.md](references/rule-editing.md) first and follow it.
Both modes write to `style` and `rules.md`, and never without confirmation.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/golang/review.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
