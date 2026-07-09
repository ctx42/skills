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

## Self-learning

Read this skill's lessons first and obey them: the sibling `LESSONS.md`, plus —
when this skill's directory is not writable (an installed copy) —
`$HOME/.agent-data/ctx42-skills/lessons/craft/cm.md`. When the user corrects
you, or you catch your own mistake, append the fix as a one-line rule to
whichever is writable (the sibling in a source checkout, else the `.agent-data`
file, creating it), then report where — so it never recurs.

## Invocation

- With commit hash: generate from that commit's diff.
- Otherwise: generate from current staged/unstaged diff.

Always derive the message from the diff only.

## Describe changes only

Write for any reader of `git log`, not for someone who sat in planning or
review. They only see the diff and the message.

- State **what** changed and **why** in product/code terms (bugs fixed,
  behavior, API, tests).
- Match detail to reader impact. Spend words on what changes for a user of
  the software—behavior, API, bug fixes, CLI/output—and describe those
  precisely. Internal or mechanical cleanups with no user-visible effect
  (lint/style fixes, formatting, renames, dependency bumps, test-only
  tweaks) get a one-sentence summary, not a per-edit account. When a commit
  mixes both, lead with the user-facing change and fold the cleanup into a
  single closing sentence.
- A body is optional. If the summary line already conveys the change and
  there is nothing user-facing to explain, omit the body entirely rather
  than manufacturing detail.
- Do **not** reference internal process the reader cannot know: remediation
  phases, review plans, skill names, "as discussed", ticket/session context,
  or paths like `tmp/*-plan.md` unless the diff itself only touches those
  files.
- Do **not** label work with project-local milestones ("phase 1", "follow-up
  from the review") when the diff is normal library/CLI fixes.
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

**High clarity standard**: Write bodies with the same precision and structure
expected in excellent Go godoc—direct, specific, reader-friendly. Precision
means saying the right thing concisely, not cataloguing every edit: prefer the
smallest body that fully explains the user-facing change and its motivation.
Do not enumerate mechanical changes line by line when one sentence covers them.

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

Then ask: "Commit with this message?" (or "Amend?").

Use `git commit` or `git commit --amend` via heredoc.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.
