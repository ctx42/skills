---
name: style
description: >
  Enforced Go coding style for this project (production and test code): the
  rulebook to read before writing or editing any .go file, however small, and
  a runnable style-only pass that lists style offenses across a diff, package,
  or module and proposes fixes to apply. Use before touching Go, or to check
  or fix Go style; adding or changing a rule belongs to go:review.
license: MIT
argument-hint: "[func=NAME | FILE:LINE | FILE.go | ./pkg | all]
  [packages=a,b] [max=N] [depth=light|standard*|full] [plan_first] [fix]"
---

# style

## Usage

```
/go:style                             style-check the current git diff (default)
/go:style func=Parse                  check one function (func=T.Bar: a method)
/go:style pkg/foo/foo.go:42           check the function enclosing that line
/go:style pkg/foo/foo.go              check one file
/go:style ./pkg/foo                   check one package
/go:style all                         check every package of the module
/go:style /path/to/project            check that module (a go.mod dir)
/go:style ./pkg/foo fix               apply every offense's fix without asking
/go:style all plan_first              propose the budget, then stop
/go:style all packages=a,b            restrict a module check to these packages
/go:style all max=15 depth=light      cap offenses; set depth
```

Authoritative Go style rules and the style-only pass that enforces them. The
rules live in two files:

- [references/production.md](references/production.md) — the Production
  section: formatting, naming, functions, declarations, godoc, errors, output,
  API design, and examples.
- [references/test.md](references/test.md) — the Test section: structure,
  naming, assertions, helpers and fixtures, and coverage.

Two uses:

- Reference — when loaded as context before writing Go (the default): apply
  the Production section to `*.go` and the Test section to `*_test.go`; Test
  inherits Production unless a Test rule overrides it. Before editing a `*.go`
  file, read `references/production.md`; before editing a `*_test.go` file,
  read `references/test.md` and `references/production.md` both. Read each
  file once per session, the first time an edit needs it; a one-line edit
  needs it too.
- Run a pass — when invoked as `/style [target]`: check finished code against
  these rules and propose fixes. Read
  [references/checking.md](references/checking.md) and follow it; per-rule
  detection detail lives in [rules.md](rules.md), opened one entry at a time.

Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. `func=` names the target, not a
control. A `key=value` that names no control here, or a word left over once the
modes, the target, and any text the skill takes are read: say it was not
recognized, name the ones that exist, and run with the defaults as if it were
absent — unless dropping it would widen what the run changes; then ask. A target
that resolves to nothing: say so and ask — never guess what to work on.

Change the rules only through `go:review` (state a preference, or
`go:review learn` to mine an editing session); never hand-edit them.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see — when citing a rule, name it and the fix, not
its full text.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/go/style.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
