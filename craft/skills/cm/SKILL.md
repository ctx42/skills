---
name: cm
description: >
  Writes and amends git commit messages using Conventional Commits with a Linux
  kernel-style body, held to a high standard of clarity, structure, and
  precision (aligned with excellent godoc quality). Use when writing or amending
  a commit message.
license: MIT
---

# Commit Message Formatting

## Invocation

- With commit hash: generate from that commit's diff.
- Otherwise: generate from current staged/unstaged diff.

Always derive the message from the diff only.

## Arguments

Detect from the user's words; they combine (e.g. `micro apply`). Default (none
given): full-length message, presented without committing.

Verbosity — mutually exclusive, default full length:

- `micro` → summary line **only**, no body. Add `!` + `BREAKING CHANGE:` footer
  only when the change is breaking.
- `minimal` → summary line plus **one** short paragraph explaining the single
  most important *why*. `Refs:` only if a breaking change applies.

Commit control:

- `apply` → commit the generated message directly via heredoc without asking —
  `git commit`, or `git commit --amend` for a hash invocation.

## Describe changes only

Write for any reader of `git log`, not for someone who sat in planning or
review. They only see the diff and the message.

- State **what** changed and **why** in product/code terms (bugs fixed,
  behavior, API, tests).
- Match detail to reader impact. Describe user-facing changes (behavior, API,
  bug fixes, CLI/output) precisely; give mechanical cleanups (lint, formatting,
  renames, dep bumps, test tweaks) a one-sentence summary, not a per-edit
  account. When a commit mixes both, lead with the user-facing change and fold
  the cleanup into one closing sentence.
- A body is optional. If the summary line already conveys the change and
  there is nothing user-facing to explain, omit the body entirely rather
  than manufacturing detail.
- Do **not** reference internal process the reader cannot know — remediation
  phases, review plans, skill names, "as discussed", ticket/session context,
  project milestones ("phase 1"), or `tmp/*-plan.md` paths — unless the diff
  itself only touches those files.
- Prefer concrete symbols and files: `` `TargetNameFromContext` ``,
  `` `Prepare` ``, not umbrella slogans that hide the actual edits.

If the diff mixes unrelated edits (e.g. IDE config + library fix), say so in
the body or ask to split commits—still without process jargon.

## Structure

```
<type>[(<scope>)][!]: <description>

[body]

[BREAKING CHANGE: <description>]
[Refs: <sha>, ...]
```

## Summary Line

- Type: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `build`,
  `ci`, `chore`, `revert`
- Scope: optional, short noun
- Description: imperative, lowercase, no period, ideally ≤ 50 chars (hard 72)

## Breaking Changes

If the change affects exported symbols or observable behavior for callers:

- Add `!` in the summary.
- Add mandatory `BREAKING CHANGE:` footer describing the impact and migration.

## Body (Kernel Style)

- Wrap at 72 columns.
- Imperative mood.
- Explain **why** the change was made (the diff shows what).
- Use backticks for symbol references: `` `xrr.FieldErrors` ``,
  `` `WithCause` ``.
- When referencing prior commits: `Commit <short-sha> ("summary") ...`

**High clarity standard**: Write bodies with godoc-level precision — the
smallest body that fully explains the user-facing change and its motivation.
Never enumerate mechanical edits line by line when one sentence covers them.

## Footers

Only two allowed:

- `BREAKING CHANGE: ...` (when `!` is used)
- `Refs: <sha>[, <sha>...]`

Omit all other trailers.

Never add an AI `Co-Authored-By` trailer (e.g.
`Co-Authored-By: <model> <noreply@...>`).

## Output

Present the full message in a fenced code block with **zero leading whitespace**
on every line.

The message is the deliverable. Run `git commit` / `git commit --amend` (via
heredoc) only when the invocation asks to commit or amend — the `apply`
argument, or wording like "and amend it". Otherwise never propose committing;
the user decides when.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/cm.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
