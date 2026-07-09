# enhance-skills

Turns corrections into durable skill improvements. When a skill misbehaves and
you correct it, `enhance-skills` records the fix as a one-line rule in that
skill's sibling `LESSONS.md`, so the next run reads it and the mistake does not
repeat. It also retrofits the `## Self-learning` block into skills that lack it.

Every skill in this marketplace carries a `## Self-learning` block that appends
lessons on its own during a run; `enhance-skills` is the batch engine that sweeps
a whole conversation after the fact and back-fills what the inline mechanism
missed.

## When to use

- "Enhance the skills I used in this conversation."
- "Record that correction so it doesn't happen again."
- "Add self-learning to `<skill>`."

## Modes

- **Harvest** (default) — scans the current conversation for corrections and
  self-caught mistakes, then appends one-line rules to each used skill's
  `LESSONS.md` (after showing them for confirmation).
- **Retrofit** — installs the `## Self-learning` block into a `SKILL.md` that
  lacks it.

## How lessons live

Lessons never sit inline in the body — the always-loaded surface stays lean and
re-authoring a skill does not clobber accumulated lessons. Each skill resolves
its store to one of two places:

- **In-place** — running from a writable source checkout: the sibling
  `LESSONS.md` next to `SKILL.md`. Committed here, lessons ship to everyone.
- **External** — running from a read-only or update-clobbered install
  (`~/.claude/plugins/cache/…`): `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`.
  `$HOME`-rooted so it is visible and survives plugin updates on Linux, macOS,
  and Windows.

Reading unions both when both exist (shipped lessons plus local ones); writing
goes only to the writable one. The store is created lazily, on the first lesson.
The cache is never written even when the OS reports it writable — a plugin update
wipes it.

## Evaluations

### 1. Harvest a correction into the right skill

**Request:** After using `/golang:review` and correcting it ("flag this, it's a
real bug"), the user runs `/craft:enhance-skills`.

**Expected:**
- Identifies `review` as a used skill; ignores skills only mentioned.
- Proposes a one-line, general rule (not a task-specific restatement) and shows
  the resolved target file before writing.
- On confirmation, creates the store with a `# Lessons` header and appends the
  rule; does not touch `SKILL.md` content.

### 2. Retrofit a skill missing the block

**Request:** "Add self-learning to `craft/skills/foo`," a skill with no
`## Self-learning` block.

**Expected:**
- Inserts the canonical block verbatim as the first `## ` section of `SKILL.md`.
- Does not create `LESSONS.md` (lazy).
- Is a no-op on a skill that already has the block.

### 3. Read-only install falls back to the external store

**Request:** Harvest while the used skill runs from `~/.claude/plugins/cache/…`.

**Expected:**
- Resolves the store to `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`,
  not the cache.
- Creates parent dirs and writes the rule there; names the path in the report.
- Does not write into the cache even if the OS reports it writable.

### 4. Terse output

**Request:** Harvest lessons for two skills.

**Expected:**
- No preamble, no narration of scanning steps.
- Per skill: the file touched and each rule added, once.
- No closing summary that restates the rules already listed or dumps the full
  `LESSONS.md`.
