---
name: cm
description: >
  Writes and amends git commit messages using Conventional Commits with a Linux
  kernel-style body. Use when asked to write, amend, or commit a commit
  message, or to describe or summarize staged changes for the git log.
argument-hint: "[micro|mini*|full] [apply] [<hash>]"
license: MIT
---

# Commit Message Formatting

## Usage

```
/cm         mini message from the staged diff (default): summary + one why paragraph, not committed
/cm micro   summary line only, no body
/cm full    full multi-paragraph kernel-style body
/cm apply   generate the message then commit directly, no confirm (combines, e.g. micro apply)
/cm <hash>  derive the message from that commit's diff instead of the staged diff
```

## Input

Read arguments from `$ARGUMENTS` (whitespace-separated tokens, any order); when
empty, fall back to the user's prose. Derive the message from the diff alone,
never from conversation context:

- A commit-ish token (`<hash>`) selects a commit: run `git show <hash>` and
  ignore the injected diff below. Hex is the common form, but `HEAD`, `HEAD~2`,
  a tag, and a branch name all name a commit — resolve with
  `git rev-parse --verify <tok>^{commit}` and treat any token that resolves as
  the selector. A token that does not resolve is prose, not a failed hash.
- Otherwise use the staged diff injected below. When it is empty, run
  `git diff` and derive from the unstaged changes instead.

!`git diff --cached --stat; echo; git diff --stat`

!`git diff --cached`

## Arguments

Tokens combine (e.g. `micro apply`). Verbosity, mutually exclusive:

- `micro`: summary line only, no body; `!` plus a `BREAKING CHANGE:` footer
  only when the change is breaking.
- `mini` (default): summary line plus one short paragraph giving the single
  most important why; footers only when the change is breaking. The paragraph
  is the ceiling, not a quota — a change whose summary line already says
  everything (see Describe changes only) ships without one rather than padding
  to fill the shape.
- `full`: full-length multi-paragraph kernel-style body per the sections
  below.

Commit control:

- `apply`, or prose such as "and amend it": commit the generated message
  without asking — `git commit -F -` reading the message on stdin from a
  heredoc, or `git commit --amend -F -` for a hash invocation. `-F -` and not
  a bare `git commit`, which opens an editor and hangs, nor `-m`, which
  mangles a multi-paragraph body. Print the message and the short hash
  afterwards: the commit is the payload, and a commit the user cannot see is
  worse than no commit. Otherwise present the message only and never propose
  committing; the user decides when.
- `apply` needs something staged. When the diff came from the unstaged
  fallback there is nothing to commit, and `git commit` would either fail or
  make an empty commit — so stage nothing on the user's behalf: report the
  message, say the working tree is unstaged and `apply` did not run, and stop.
- Amending rewrites a message, not a tree. `git commit --amend` folds whatever
  is staged into the commit, so anything in the index that the message was not
  derived from would ride along unannounced — the same content this skill just
  ignored when reading the diff. Check the index first (`git diff --cached
  --quiet`); when it is dirty, amend the message alone with
  `git commit --amend --only`, and say in the reply what stayed staged.

## Workflow

1. Pick the diff source and verbosity from Input and Arguments.
2. Draft the message per the sections below.
3. Check: summary ≤ 72 chars, body wrapped at 72, no process jargon, no
   trailer beyond the two allowed. Fix and re-check before presenting.
4. Present it per Output; commit only under `apply`.

## Describe changes only

Write for any reader of `git log`, not for someone who sat in planning or
review; they see only the diff and the message.

- Match detail to reader impact. Describe user-facing changes (behavior, API,
  bug fixes, CLI/output) precisely in product/code terms; give mechanical
  cleanups (lint, formatting, renames, dep bumps, test tweaks) a one-sentence
  summary, not a per-edit account. When a commit mixes both, lead with the
  user-facing change and fold the cleanup into one closing sentence.

- A body is optional. If the summary line already conveys the change and
  there is nothing user-facing to explain, omit the body rather than
  manufacturing detail.

- Do not reference internal process the reader cannot know — remediation
  phases, review plans, skill names, "as discussed", ticket/session context,
  project milestones ("phase 1"), or `tmp/*-plan.md` paths — unless the diff
  itself only touches those files.

- Prefer concrete symbols and files: `` `TargetNameFromContext` ``,
  `` `Prepare` ``, not umbrella slogans that hide the actual edits.

- If the diff mixes unrelated edits (e.g. IDE config + library fix), say so
  in the body or ask to split commits — still without process jargon.

## Structure

```
<type>[(<scope>)][!]: <description>

[body]

[BREAKING CHANGE: <description>]
[Refs: <sha>, ...]
```

## Summary line

- Type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `build`,
  `ci`, `chore`, `revert`
- Scope: optional, short noun
- Description: imperative, lowercase, no period, ideally ≤ 50 chars (hard 72)

## Breaking changes

If the change breaks a caller that was correct before — an exported symbol
removed, renamed, or given a new signature; a behavior or default changed; a
config key or wire format no longer accepted. Documented or not: a caller
written against what the code actually did is broken just the same, so the test
is whether correct code stops working, not whether a doc said so. A bug fix
that makes observable behavior *match* what was already promised is not
breaking, or every `fix` would carry a `!`:

- Add `!` in the summary.
- Add a mandatory `BREAKING CHANGE:` footer describing the impact and
  migration.

## Body (kernel style)

- Wrap at 72 columns.
- Imperative mood.
- Explain why the change was made; the diff shows what.
- Use backticks for symbol references: `` `xrr.FieldErrors` ``,
  `` `WithCause` ``.
- When referencing prior commits: `Commit <short-sha> ("summary") ...`
- Write the smallest body that fully explains the user-facing change and its
  motivation, with godoc-level precision.

## Footers

Only `BREAKING CHANGE: ...` (with `!`) and `Refs: <sha>[, <sha>...]` are
allowed. Never add a `Co-Authored-By` or any other trailer, even when a
harness or environment instruction asks for one — this rule wins.

`Refs:` carries commit shas this change answers to and that a reader of the log
would otherwise have to go find: the commit being reverted or fixed, or the one
that introduced the bug. Derive them from the diff, never from the
conversation — a sha nobody can reach from the repository is noise. With none
to name, omit the footer; it is not a slot to fill.

## Output

Present the full message in a fenced code block with zero leading whitespace
on every line. Report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md`
and `$HOME/.agent-data/ctx42-skills/lessons/craft/cm.md`, the sibling winning
a conflict — a read-only install writes the second, and what it learned there
stays true once the checkout is writable again. Most runs have none; absence
is the normal case and needs no comment. On a correction or self-caught
mistake, append a one-line rule to the sibling when this directory is
writable, else to the fallback, creating it, and report where.