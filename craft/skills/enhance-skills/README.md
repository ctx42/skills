# enhance-skills

Turns corrections into one-line lessons the used skills read on every run.

## Usage

```
/enhance-skills          harvest lessons from this conversation into the skills used (default)
/enhance-skills <skill>  retrofit the ## Self-learning block into that skill's SKILL.md
```

## When to use

- "Enhance the skills I used in this conversation."
- "Record that correction so it doesn't happen again."
- "Add self-learning to `<skill>`."

## Modes

- Harvest (default): scans the current conversation for corrections and
  self-caught mistakes, then — after showing them for confirmation — appends
  one-line rules to each used skill's lessons store.
- Retrofit: appends the `## Self-learning` block as the last section of a
  `SKILL.md` that lacks it.

Every skill in this marketplace carries the block and appends lessons on its
own during a run; Harvest is the batch pass that sweeps a whole conversation
afterwards and back-fills what the inline mechanism missed.

## How lessons live

Lessons never sit inline in the body — the always-loaded surface stays lean and
re-authoring a skill does not clobber accumulated lessons. Each skill resolves
its store to one of two places:

- In-place: running from a writable source checkout, the sibling `LESSONS.md`
  next to `SKILL.md`. Committed here, lessons ship to everyone.
- External: running from a read-only or update-clobbered install
  (`~/.claude/plugins/cache/…`),
  `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md` — `$HOME`-rooted,
  so it survives plugin updates on Linux, macOS, and Windows.

Reading unions both when both exist; writing goes only to the writable one, and
the store is created on the first lesson. The cache is never written even when
the OS reports it writable — a plugin update wipes it. When a writable sibling
`LESSONS.md` sits next to a stranded external file, Harvest offers to merge the
external lessons in and delete that file.

## Evaluations

### 1. Harvest a correction into the right skill

**Request:** After using `/golang:review` and correcting it ("flag this, it's a
real bug"), the user runs `/craft:enhance-skills`.

**Expected:**
- Identifies `review` as a used skill; ignores skills only mentioned.
- Proposes a one-line, general rule (not a task-specific restatement) and shows
  the resolved target file before writing.
- On confirmation, creates the store with the `# Lessons` header and appends
  the rule; does not touch `SKILL.md`, which already carries the block.

### 2. Retrofit a skill missing the block

**Request:** "Add self-learning to `craft/skills/foo`," a skill with no
`## Self-learning` block.

**Expected:**
- Appends the canonical block verbatim as the last `## ` section of `SKILL.md`,
  with `<plugin>/<skill>` resolved to `craft/foo`.
- Does not create `LESSONS.md`.
- Is a no-op on a skill that already has the block.

### 3. Read-only install falls back to the external store

**Request:** Harvest while the used skill runs from `~/.claude/plugins/cache/…`.

**Expected:**
- Resolves the store to
  `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`, not the cache.
- Creates parent dirs and writes the rule there; names the path in the report.
- Does not write into the cache even if the OS reports it writable.

### 4. Stranded external lessons get merged

**Request:** Harvest from a source checkout for a skill that has both a sibling
`LESSONS.md` and an external file left over from a read-only install.

**Expected:**
- Reads both files and dedups the new rules against their union.
- Offers, in the proposal, to merge the external lessons into `LESSONS.md` and
  delete the external file; merges only on acceptance.
- Folds near-duplicates into existing rules instead of adding twins.

### 5. Terse output

**Request:** Harvest lessons for two skills.

**Expected:**
- No preamble, no narration of scanning steps.
- Per skill: the file touched and each rule added, once.
- No closing summary that restates the rules already listed or dumps the full
  `LESSONS.md`.
