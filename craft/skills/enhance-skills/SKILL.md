---
name: enhance-skills
description: >
  Records lessons learned during a conversation into the skills that were used,
  so the same mistake never repeats, and retrofits the self-learning mechanism
  into skills that lack it. Harvest mode scans the current conversation for
  corrections and self-caught mistakes, then appends one-line rules to each used
  skill's lessons store (a sibling LESSONS.md in a source checkout, else a
  durable file under $HOME/.agent-data); retrofit mode installs the
  `## Self-learning` block into any SKILL.md missing it. Use when asked to
  enhance the skills used in this conversation, capture a correction so it does
  not happen again, record lessons learned, or make skills self-improving.
license: MIT
---

# enhance-skills

Turn corrections into durable skill improvements. Pick the mode from the request:

- **Harvest** (default) — "enhance the skills I used", "record what you learned",
  "don't make that mistake again". Scan this conversation and write lessons.
- **Retrofit** — "add self-learning to `<skill>`", or automatically when Harvest
  meets a skill whose `SKILL.md` has no `## Self-learning` block.

## Self-learning

Read this skill's lessons first and obey them: the sibling `LESSONS.md`, plus —
when this skill's directory is not writable (an installed copy) —
`$HOME/.agent-data/ctx42-skills/lessons/craft/enhance-skills.md`. When the user
corrects you, or you catch your own mistake, append the fix as a one-line rule to
whichever is writable (the sibling in a source checkout, else the `.agent-data`
file, creating it), then report where — so it never recurs.

## Lessons store

Every skill's lessons resolve to one of two places; resolve per skill, and use
the same resolution for both reading and writing:

- **In-place** — the skill's own directory is writable (a source checkout or a
  `--plugin-dir` working copy): the sibling `LESSONS.md`. Lessons committed here
  ship to everyone.
- **External** — the skill runs from a read-only or update-clobbered install
  (any path under `.../plugins/cache/`):
  `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`. `$HOME`-rooted
  so it stays visible and survives plugin updates on Linux, macOS, and Windows.

Resolve the skill's on-disk directory from the base directory the host reports
when the skill is invoked. Read **both** files when both exist — shipped lessons
plus local ones — and obey the union. Write only to the writable one: the sibling
in a checkout, else the external file (create parent dirs). Never write into
`.../plugins/cache/` even if the OS reports it writable; a plugin update wipes it.

## Harvest

1. **List skills used.** Collect every skill actually invoked in this
   conversation (a `/<group>:<skill>` call or Skill tool use). Ignore skills only
   mentioned, never run.
2. **Mine each for lessons.** For each used skill, find where the user corrected
   the agent, or the agent caught its own mistake, *while that skill was driving*.
   A lesson is a concrete rule that would prevent a recurrence — not a one-off
   fact about this task. Skip praise, restated requirements, and task-specific
   detail.
3. **Resolve stores.** For each used skill, resolve its `SKILL.md` path and its
   [lessons store](#lessons-store). If the path is unknown or ambiguous, ask.
4. **Propose.** Present, per skill, the resolved target file and the one-line
   rules you intend to add. Wait for confirmation before writing.
5. **Write.** On approval, for each skill: retrofit the `## Self-learning` block
   if the `SKILL.md` is in-place and lacks it, then append each new rule to the
   resolved store (see [Lesson format](#lesson-format)), deduplicating against
   lines already there.
6. **Report.** Per skill: the file written and each rule added. Nothing else.

## Retrofit

Install the `## Self-learning` block as the first `## ` section of the target
`SKILL.md` — immediately before its current first `## ` heading (append if the
file has none). Skip if the block already exists. Fill `<plugin>` and `<skill>`
from the target's path. Do not create any lessons file; the store appears lazily
on the first lesson. Retrofit edits `SKILL.md`, so it needs an in-place checkout —
on a read-only install, report that and stop.

Block to insert (verbatim, with `<plugin>/<skill>` resolved to the real names):

    ## Self-learning

    Read this skill's lessons first and obey them: the sibling `LESSONS.md`,
    plus — when this skill's directory is not writable (an installed copy) —
    `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`. When the user
    corrects you, or you catch your own mistake, append the fix as a one-line
    rule to whichever is writable (the sibling in a source checkout, else the
    `.agent-data` file, creating it), then report where — so it never recurs.

## Lesson format

A lessons file is a flat list of one-line imperative rules, newest appended last:

    # Lessons

    Rules learned for the `<skill>` skill. Read before running; obey each line.

    - <one-line imperative rule, stated so it generalizes past this task>

- One rule per line, imperative, terse — the bar of a style rule.
- Concrete and general: "Derive the commit type from the diff, not the branch
  name" — not "the user wanted fix not feat here".
- No dates, ticket ids, or task-specific nouns. A lesson outlives its task.
- Dedup: fold a near-duplicate into the existing line; never add a twin.
- Create the file with the `# Lessons` header on the first lesson; append after.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Per touched skill, list the file written and the
rules added (or the block installed). Always name the resolved path so the user
knows whether a lesson shipped (sibling `LESSONS.md`) or stayed local
(`.agent-data`); never fabricate a write you could not perform.
