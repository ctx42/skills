# Commit Message Formatting (cm)

Writes and amends git commit messages following Conventional Commits format with
high-quality, Linux kernel-style bodies.

## When to Use

- Before committing changes
- When amending the last commit
- To produce clear, professional commit history

## Usage

**From staged changes**
`/cm`

**From a specific commit**
`/cm <commit-hash>`

**Arguments** (combinable, e.g. `/cm micro apply`)
- `micro` — summary line only, no body.
- `mini` — summary line plus one short paragraph only.
- `apply` — commit the message directly, without asking to confirm.

The skill always derives the message from the actual diff. It produces:
- Proper type/scope/summary line (≤50 chars recommended)
- Kernel-style body explaining *why* the change was made
- `BREAKING CHANGE:` footer when appropriate
- `Refs:` trailer only

Messages are held to the same clarity standard as excellent godoc.

See `SKILL.md` for the full message structure and quality rules.

## Evaluations

### 1. Message from staged changes

**Request:** `/cm` with a staged diff that adds a JWT login endpoint.

**Expected behavior:**
- Derives the message only from the diff, not from conversation context.
- Summary line is `feat(...)`-style, imperative, lowercase, no period, ≤ 50
  chars recommended.
- Body wraps at 72 cols and explains *why*, referencing concrete symbols in
  backticks.
- Presents the full message in a zero-indent code block and stops — it does
  not run or propose `git commit` unless the invocation asked to commit.

### 2. Amend the previous commit

**Request:** `/cm <commit-hash> and amend it` for an existing commit whose
message is weak.

**Expected behavior:**
- Regenerates the message from that commit's diff.
- Amends via `git commit --amend` (not a new commit) through a heredoc,
  because the invocation asked for the amend; a bare `/cm <commit-hash>` would
  only present the message.

### 3. Breaking change

**Request:** `/cm` with a staged diff that removes an exported function.

**Expected behavior:**
- Adds `!` to the summary line.
- Includes a mandatory `BREAKING CHANGE:` footer describing impact and
  migration.
- Uses no trailers other than `BREAKING CHANGE:` and `Refs:`.

### 4. Terse output

**Request:** `/cm` with a staged diff.

**Expected behavior:**
- No preamble or narration ("Let me look at the diff…"); opens with the message.
- Presents the commit message once in a zero-indent code block and nothing
  else — no restating of the diff or the message the user can already see, no
  unprompted offer to commit.

### 5. Detail matched to impact

**Request:** `/cm` with a staged diff whose only effect is passing the linter
(e.g. a package comment, an identifier rename, a `#nosec` suppression) with no
user-visible behavior change.

**Expected behavior:**
- Summary line captures the change (`style: ...` / `chore: ...`).
- Summarizes the cleanup in a single sentence, or omits the body entirely — it
  does **not** enumerate each mechanical edit line by line.
- Reserves per-symbol detail for changes that affect a user of the software
  (behavior, API, bug fixes); a mixed commit leads with those and folds the
  cleanup into one closing sentence.

### 6. Verbosity arguments

**Request:** `/cm micro`, then `/cm mini`, on the same staged diff.

**Expected behavior:**
- `micro` emits the summary line only — no body, no footers (unless the change
  is breaking).
- `mini` emits the summary line plus a single short paragraph explaining the
  most important *why*, not a full multi-paragraph body.

### 7. Commit with `apply`

**Request:** `/cm apply` (or `/cm micro apply`) with a staged diff.

**Expected behavior:**
- Generates the message, then runs `git commit` via heredoc without asking for
  confirmation.
- Combines with a verbosity argument: `micro apply` commits a one-line message.
