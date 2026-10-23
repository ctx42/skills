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
5. Ask the round: every contract, compat, and needs-user finding plus any
   baseline or dirty-tree question and, when the user's instructions or the
   harness forbid committing, one asking leave to commit, answered once for
   every fix — in order, one question per question-tool call (one numbered
   message without such a tool), each with the situation, the options, and
   your recommendation in plain terms. Nothing to ask: say "no questions;
   working unattended" and go on in the same turn. Ask every one and wait for
   the answers. Each left unanswered takes the safe side: the finding is
   skipped, a baseline failure counts as known, and without leave to commit
   the run lists the triage, writes no Report, and stops before any edit.

From here on, never ask: not to confirm a fix, not to commit, not to continue.

## 2. Fix — one commit per fix

Work in dependency order, else the findings' order. One commit holds one
logical fix: findings with one root cause share a commit; one finding never
spans two unless its parts stand alone.

For each fix:

1. Make the smallest change that resolves the finding as stated. An edit
   script asserts every replacement changed the text — a pattern that
   matches nothing fails silently — and, spanning several files, validates
   every replacement before writing any file and holds its intermediate text
   in memory, never in a temp file beside the sources, so a failed assertion
   leaves the tree untouched. An
   edit to hard-wrapped Markdown rewraps the whole paragraph it touches,
   never splitting an inline code span across lines. Before proving a new
   test red on the old code, read what the old code does with that input:
   shape the fixture so only the check under test can fire, and run a test
   that shells out from the package directory (a runner invoking
   `go test ./...`) in a temp dir, since it can recurse. Prove it red as it
   will be committed — after it passes the per-file checks, line width
   included — and before changing any signature it calls, which leaves the old
   code unbuildable.
2. Check before committing. A fix that turns out to need a contract or compat
   change nobody foresaw is not applied: restore its files, defer it with the
   reason, and go on.
3. Run the project's checks, per-file ones (formatter, line width) included,
   gated on exit status in the same command that commits
   (`make test >out 2>&1 || exit 1`), never on piped or filtered output. A
   failure the baseline did not have: repair it once; still red, restore the
   fix's files and defer it with the failing check named. Per-file checks skip
   the fix's deleted paths; staging still includes them.
4. Stage only the fix's files by path (`git add -- <paths>`), first unstaging
   anything else the index holds, the user's own staged changes included
   (`git restore --staged` keeps them in the tree; a `git rm` or `git mv`
   stages at once), compare `git diff --cached --name-only` with that list in
   the same command, and commit with a message written per
   [../cm/SKILL.md](../cm/SKILL.md) at `mini`, from the staged diff alone
   (`git commit -F -`).

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
the report leaves out. Align the table's columns, sizing each from its
longest cell before writing the table. Name every other finding not fixed
under Deferred with its reason; a finding already fixed or not reproducible
counts as not fixed and goes there too. Omit an empty section.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/fix-all.md` (pass `~` as is,
the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
