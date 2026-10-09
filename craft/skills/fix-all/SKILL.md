---
name: fix-all
description: >
  Fixes every finding already raised in the conversation (a review, lint or
  test output, an audit) and commits each fix as its own commit, working
  unattended: every question it needs is asked once, up front, and only for a
  fix that changes an API contract, breaks backward compatibility, or cannot be
  done without the user. Use when asked to fix all of them, fix everything
  found, work through the findings and commit, or clear the review unattended.
argument-hint: "[skip <n,n…>]"
license: MIT
---

# fix-all

## Usage

```
/fix-all            fix every finding in the conversation, one commit each
/fix-all skip 3,7   the same, leaving findings 3 and 7 untouched
```

Turn the findings already in the conversation into commits without
supervision. All the user's attention is spent in one round at the start; after
it, the run never asks again. Report tersely: no preamble or narration; state
each fact once.

The findings are the ones this conversation already produced or the user
pasted into it. Never re-review the code to add findings, and never fix
something no finding names. No findings in the conversation: say so and stop.

## 1. Triage — before any edit

1. List the findings, numbered as their source numbered them, else in the
   order given. Drop the ones the arguments skip.
2. Read the code each finding touches and classify it:
   - **contract** — the fix changes an API contract: an exported symbol's name,
     signature, or documented behavior; a wire, file, or config format; a CLI
     flag or exit code; an error type callers match on.
   - **compat** — the fix breaks backward compatibility: code, data, or config
     that worked before stops working, even through an undocumented behavior.
   - **needs-user** — the fix needs a fact or choice only the user has: two
     defensible fixes that behave differently, a credential, a product call.
   - **auto** — everything else.
3. Find the project's checks from `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
   a `Makefile`, or the package manifest — build, test, lint, format — and run
   them once on the untouched tree. Red before any edit is a question for the
   round below: which failures are known and may stay.
4. Note the working tree. A fix whose files hold uncommitted changes the
   findings did not make is a question too: commit them in with the fix, or
   skip the fix — a file is staged whole, never by hunk.
5. Ask the round: one message, every contract, compat, and needs-user finding
   plus any baseline or dirty-tree question, numbered, each with the
   situation, the options, and your recommendation in plain terms. Nothing
   to ask: say "no questions; working unattended" and go on in the same turn.
   Wait for the answers. Unanswered takes the safe side: the finding is
   skipped, a baseline failure counts as known.

From here on, never ask: not to confirm a fix, not to commit, not to continue.

## 2. Fix — one commit per fix

Work in dependency order, else the findings' order. One commit holds one
logical fix: findings with one root cause share a commit; one finding never
spans two unless its parts stand alone.

For each fix:

1. Make the smallest change that resolves the finding as stated. An edit
   script spanning several files validates every replacement before writing
   any file, so a failed assertion never leaves a fix half-applied. Before
   proving a new test red on the old code, read what the old code does with
   that input: a test that shells out from the package directory (a runner
   invoking `go test ./...`) can recurse, so run it in a temp dir.
2. Check before committing. A fix that turns out to need a contract or compat
   change nobody foresaw is not applied: restore its files, defer it with the
   reason, and go on.
3. Run the project's checks, gated on exit status in the same command that
   commits (`make test >out 2>&1 || exit 1`), never on piped or filtered
   output. A failure the baseline did not have: repair it once; still red,
   restore the fix's files and defer it with the failing check named.
   Per-file checks (formatter, line width) skip the fix's deleted paths;
   staging still includes them.
4. Stage only the fix's files by path (`git add -- <paths>`), compare
   `git diff --cached --name-only` with that list in the same command, and
   commit with a message written per [../cm/SKILL.md](../cm/SKILL.md) at
   `mini`, from the staged diff alone (`git commit -F -`).

Never push, amend, rebase, or touch a commit the run did not make. Never add a
trailer beyond what `cm` allows.

## 3. Report

Read every count and hash off `git log` and the tree, never from memory.

```
fixed 5 of 7 in 4 commits

| #  | Commit  | Summary                          |
|----|---------|----------------------------------|
| 1  | a1b2c3d | fix(auth): reject an empty token |

Deferred
- #6 compat: removing `Opts.Retry` breaks callers that set it
- #7 check: `go test ./auth` fails after the fix (restored)
```

`fixed N of M`: M counts every finding but those the arguments skip, which
the report leaves out. Align the table's columns. Name every other finding
not fixed under Deferred with its reason; a finding already fixed or not
reproducible counts as not fixed and goes there too. Omit an empty section.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/fix-all.md`,
the sibling winning a conflict — a read-only install writes the second, and
what it learned there stays true once the checkout is writable again. Most runs
have none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from
the project at hand (its files, tests, tickets) — to the sibling when this
directory is writable, else to the fallback, creating it, and report where.
