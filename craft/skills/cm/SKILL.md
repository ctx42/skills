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

## Input

Read arguments from `$ARGUMENTS` (whitespace-separated tokens, any order); when
empty, fall back to the user's prose. Derive the message from the diff alone,
never from conversation context:

- A hex token (`<hash>`) selects a commit: run `git show <hash>` and ignore
  the injected diff below.
- Otherwise use the staged diff injected below. When it is empty, run
  `git diff` and derive from the unstaged changes instead.

!`git diff --cached --stat; echo; git diff --stat`

!`git diff --cached`

## Arguments

Tokens combine (e.g. `micro apply`). Verbosity, mutually exclusive:

- `micro`: summary line only, no body; `!` plus a `BREAKING CHANGE:` footer
  only when the change is breaking.
- `mini` (default): summary line plus one short paragraph giving the single
  most important why; footers only when the change is breaking.
- `full`: full-length multi-paragraph kernel-style body per the sections
  below.

Commit control:

- `apply`, or prose such as "and amend it": commit the generated message via
  heredoc without asking — `git commit`, or `git commit --amend` for a hash
  invocation. Otherwise present the message only and never propose
  committing; the user decides when.

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

If the change affects exported symbols or observable behavior for callers:

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

## Output

Present the full message in a fenced code block with zero leading whitespace
on every line. Report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/cm.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
