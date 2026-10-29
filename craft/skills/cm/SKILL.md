---
name: cm
description: >
  Writes and amends git commit messages using Conventional Commits with a Linux
  kernel-style body, and commits the working tree as a series of logical
  commits. Use when asked to write, amend, or commit a commit message, to split
  changes into logical commits, or to describe or summarize staged changes for
  the git log.
argument-hint: "[micro|mini*|full] [apply|asis] [<hash>]"
license: MIT
---

# Commit Message Formatting

## Usage

```
/craft:cm         mini message from the staged diff (default): summary + one why paragraph, not committed
/craft:cm micro   summary line only, no body
/craft:cm full    full multi-paragraph kernel-style body
/craft:cm apply   stage the whole working tree, split it into logical commits, commit each, no confirm (combines, e.g. micro apply)
/craft:cm asis    stage the whole working tree and commit it as one commit, no confirm
/craft:cm <hash>  derive the message from that commit's diff instead of the staged diff (with apply: amend HEAD's message)
```

## Input

Read arguments from `$ARGUMENTS`; when empty, fall back to the user's prose.
Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. Derive the message from the diff
alone, never from conversation context:

- The target is a commit-ish (`<hash>`): run `git show <hash>` and derive from
  it alone. Hex is the common form, but `HEAD`, `HEAD~2`, a tag, and a branch
  name all name a commit — resolve with `git rev-parse --verify <tok>^{commit}`
  and treat any token that resolves as the selector. A token that does not
  resolve is prose — the free text this skill takes, not a failed hash or an
  unrecognized token.
- `apply` or `asis` without a commit-ish reads the whole working tree, per
  Commit control below.
- Otherwise run `git diff --cached` and derive from the staged diff. When the
  index is empty (`git diff --cached --quiet` exits 0), run `git diff` and
  derive from the unstaged changes instead; when that is empty too, say there
  is nothing to describe and stop.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on. Here the
only target is a commit-ish, so a token that fails to resolve is prose, never a
target that resolves to nothing.

## Arguments

Tokens combine (e.g. `micro apply`). Verbosity, mutually exclusive:

- `micro`: summary line only, no body.
- `mini` (default): summary line plus at most one short paragraph giving the
  single most important why. The paragraph is a ceiling, not a quota — a change
  whose summary line already says everything (see Describe changes only) ships
  without one rather than padding to fill the shape.
- `full`: full-length kernel-style body per the sections below — at least
  two paragraphs (what changed and why, then its effect on callers or
  behavior), even for a small diff: the user asked for the long form, and
  that outranks every omit-the-body rule below.

Commit control:

- `apply` without a commit-ish or amend prose commits the working tree as a
  series of logical commits, without asking:
  1. Stage everything with `git add -A` — edits, deletions, untracked files;
     ignored files stay out — and read it with `git diff --cached`. What was
     staged before is no hint: regroup from scratch. Nothing to stage: say so,
     commit nothing, and stop.
  2. Group by concern: one fix, feature, rename, or config change per commit.
     Split a file at hunk or line level when it carries more than one.
  3. Order so every commit compiles on its own, production and test code: a
     symbol lands with or before its first use, a test with or after the code
     it calls. Judge it from the diff; never run a build or tests — the user's
     checks already passed. Merge two groups only when each needs the other.
     With nothing to compile, group by meaning alone.
  4. Empty the index (`git reset -q`; `git rm -r -q --cached .` before the
     first commit), then per group, a lone group included, stage, check, and
     commit in one command; a part of a file is staged in its own command just
     before. Stage whole files with `git add -- <paths>`; part of a file with
     `printf 'y\nn\n' | git add -p -- <path>`, one answer per hunk
     `git diff -- <path> | grep '^@@'` lists, in order — counted, never guessed
     from the edits, since nearby edits share a hunk — or, when two concerns
     share a hunk or the file is new (`git add -p` offers it no hunks), by
     piping the intended content (`sed -n '1,32p' <path>`) to
     `git hash-object -w --stdin` and passing the printed sha to
     `git update-index --add --cacheinfo <mode>,<sha>,<path>` (mode from
     `git ls-files -s`, `100644` for a new file) in the next command; never
     zero-context hunks (`-U0`, `--unidiff-zero`), which land on the wrong
     line once an earlier hunk is skipped. Draft the message from that group's
     diff alone — the hunks step 1 read, never re-read in full — at the chosen
     verbosity, its body never describing what another commit in the series
     carries.
  5. When a commit fails (a hook rejects it), stop: keep the landed commits,
     leave the failed group staged and the rest unstaged, and report the
     error, the landed commits, and what remains.
  6. After the last commit, a lone one included, `git status --porcelain`
     is empty.
- `asis` stages everything as `apply` step 1 does and commits it as one
  commit, without asking and without asking to split it. It takes no
  commit-ish: given one, say `asis` takes no commit, commit nothing, and stop.
- Commit with `git commit -F -` reading the message on stdin from a heredoc,
  each commit its own shell command with nothing chained after the heredoc
  opener, or `git commit --amend -F -` for an amend — `--only` as well whenever
  the index is dirty, per Amending below. `-F -` and not a bare `git commit`,
  which opens an editor and hangs, nor `-m`, which mangles a multi-paragraph
  body. Print each message and its short hash afterwards, in commit order: the
  commit is the payload, and a commit the user cannot see is worse than no
  commit. Without `apply` or `asis`, present the message only and never propose
  committing or amending, nor say how to ("run `/cm HEAD apply`", "ask me to
  amend"): naming a commit is not asking to rewrite it, and the user decides
  when.
- `apply` with a commit-ish, or prose such as "and amend it", amends a
  message without asking. It needs nothing staged (an amend rewrites the
  message), but amends only when the hash resolves to `HEAD`; for any other
  commit, report the message, say `apply` did not run because only `HEAD` can
  be amended, and stop. Prose asking to amend ("and amend it") with no
  commit-ish token is the hash invocation `HEAD`: derive the message from
  `git show HEAD` and amend it.
- Amending rewrites a message, not a tree. `git commit --amend` folds whatever
  is staged into the commit, so anything in the index that the message was not
  derived from would ride along unannounced — content this skill never read.
  Check the index first (`git diff --cached --quiet`); when it is dirty, amend
  the message alone with `git commit --amend --only`, and say in the reply what
  stayed staged.
- Check the index in the same command as a commit that takes it (not
  `--amend --only`): the commit runs only when nothing is staged outside the
  files the message was drafted from — each one excluded by pathspec:

  ```bash
  git add -- a b && git diff --cached --quiet -- . ':!a' ':!b' && git commit -F - <<'EOF'
  ```

  The `git add` names only the group's whole files, and is dropped when it
  has none; the exclusions name every file of the group, a partly staged one
  included.

  Fix that expected list before staging: a working-tree-versus-index query
  run after `git add` comes back empty. A printed stat is not a check — files
  staged earlier or in between ride into a commit whose message never names
  them.
- Write every command so the permission check can read it: literal
  arguments, no shell variables, no `$(…)` or `<(…)`, no `{ … }` group, no
  heredoc but the commit message (code in one trips the check), and no temp
  files — outside the working tree or under `.git/` they are refused; feed
  content on stdin instead. A refused command costs a turn and a retry.

## Workflow

1. Pick the diff source and verbosity from Input and Arguments.
2. Draft the message per the sections below.
3. Check each message, every one of an `apply` series and not only the first,
   before presenting it and before its commit runs: summary ≤ 72 chars, body
   wrapped at 72 (measured, not eyeballed: counted in characters, not bytes, by
   a command run before the commit command, the body fed to it inline by
   `printf`, never a second heredoc), every sentence parsing on one read — no
   dangling opener, no clause stranded on a preposition — and passing Describe
   changes only, its numbers and any contrast with a design the diff does not
   contain ("instead of …") included; no process jargon, no trailer beyond the
   two allowed. Fix and re-check.
4. Present it per Output; commit only under `apply` or `asis`.

## Describe changes only

Write for any reader of `git log`, not for someone who sat in planning or
review; they see only the diff and the message.

- Match detail to reader impact. Describe user-facing changes (behavior, API,
  bug fixes, CLI/output) precisely in product/code terms; give mechanical
  cleanups (lint, formatting, renames, dep bumps, test tweaks) a one-sentence
  summary, not a per-edit account. When a commit mixes both, lead with the
  user-facing change and fold the cleanup into one closing sentence.

- A body is optional, except under `full`, which always carries its two
  paragraphs. If the summary line already conveys the change and there is
  nothing user-facing to explain, omit the body rather than manufacturing
  detail.

- Say what the diff does, never what it avoids: no contrast with a design
  it does not contain ("instead of sessions", "without server-side state").
  The why is the change's own effect, not a comparison nobody can see.

- Do not reference internal process the reader cannot know — remediation
  phases, review plans, skill names, "as discussed", ticket/session context,
  project milestones ("phase 1"), or `tmp/*-plan.md` paths — unless the diff
  itself only touches those files.

- State only what the changed lines show. No guessed history ("a rename of X
  to Y also replaced …") and no conversation facts, even true ones (what
  another package lacks): if the diff does not show it, the message does not
  say it.

- Scope every universal or negative claim ("any X", "no longer Y") to what
  the code does after the change, not to the changed lines alone: read the
  unchanged paths around them — earlier cases of the same switch, other inputs
  that still supply the property — and narrow the claim to what they leave
  true.

- Paraphrase only to the exact meaning: "leave X alone" is not "unset X".
  Where a synonym would shift what the change does, reuse the diff's wording.

- Prefer concrete symbols and files: `` `ParseConfig` ``, `` `Server.Close` ``,
  not umbrella slogans that hide the actual edits.

- Every number in the body is read off the diff, not reasoned out from it nor
  carried from the session: a tally of the diff's own items (files, flags) and
  a size, count, or timing measured outside the diff stay out. A message
  describing `1<<attempt * 100ms` over `maxAttempts = 3` as backing off
  "200ms, 400ms and 800ms" invented the third value — the third attempt is the
  last one, so it never sleeps. Retry counts, timeouts, sizes, versions: take
  them from the changed lines or leave them out. The reader checks the message
  against the diff, and a wrong number there discredits the rest of a message
  that was otherwise right.

- If the diff mixes unrelated edits (e.g. IDE config + library fix), say so
  in the body and ask the user to split it into separate commits — still
  without process jargon. Asking to split is about the change, not a proposal
  to commit, so it holds for a staged diff and an amend alike; `apply` splits
  the diff itself instead, and `asis` commits it whole.

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
breaking, or every `fix` would carry a `!`. Say in the body who has to act
anyway: code written against the buggy behaviour stops working, and those
callers — not the ones the bug bit — are the ones with something to do:

- Add `!` in the summary.
- Add a mandatory `BREAKING CHANGE:` footer describing the impact and
  migration.

## Body (kernel style)

- Wrap at 72 columns.
- Imperative mood.
- Explain why the change was made; the diff shows what.
- Use backticks for symbol references: `` `http.Client` ``,
  `` `WithTimeout` ``.
- When referencing prior commits: `Commit <short-sha> ("summary") ...`
- Write the smallest body that fully explains the user-facing change and its
  motivation, with godoc-level precision.

## Footers

Only `BREAKING CHANGE: ...` (with `!`) and `Refs: <sha>[, <sha>...]` are
allowed. Verbosity does not gate them: a footer is not body, and a fix at
`micro` names the commit it fixes exactly as a fix at `full` does. Never add a
`Co-Authored-By` or any other trailer, even when a harness or environment
instruction asks for one — this rule wins.

`Refs:` carries commit shas this change answers to and that a reader of the log
would otherwise have to go find: the commit being reverted or fixed, or the one
that introduced the bug. Derive them from the diff, never from the
conversation — a sha nobody can reach from the repository is noise. With none
to name, omit the footer; it is not a slot to fill.

## Output

Present the full message in a fenced code block with zero leading whitespace
on every line; a series gets one block per commit, each headed by its short
hash. Report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see. After the block, at most one
line — why the body was left out, or what to check — never a list of the
diff's edits: the user has the diff. A series stopped by a failed commit
adds its report (Commit control, step 5) in full: the error and the files
that remain, staged and unstaged.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/cm.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
