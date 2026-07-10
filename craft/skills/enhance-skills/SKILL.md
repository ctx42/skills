---
name: enhance-skills
description: >
  Records lessons learned during a conversation into the skills that were
  used, so the same mistake never repeats, and retrofits the self-learning
  mechanism into skills that lack it. Use when asked to enhance the skills
  used in this conversation, record lessons learned, capture a correction so
  it does not repeat, or make skills self-improving.
license: MIT
---

# enhance-skills

Turn corrections into durable skill improvements. Pick the mode from the request:

- **Harvest** (default) — "enhance the skills I used", "record what you learned",
  "don't make that mistake again". Scan this conversation and write lessons.
- **Retrofit** — "add self-learning to `<skill>`", or automatically when Harvest
  meets a skill whose `SKILL.md` has no `## Self-learning` block.

## Lessons store

Every skill's lessons resolve to one of two places; resolve per skill and use
the same resolution for reading and writing:

- **In-place** — directory writable (source checkout or `--plugin-dir` copy):
  sibling `LESSONS.md`; committed here, lessons ship to everyone.
- **External** — read-only or update-clobbered install (under
  `.../plugins/cache/`):
  `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`, `$HOME`-rooted
  to survive plugin updates.

Resolve the directory from the base dir the host reports. Read **both** files
when both exist and obey the union; write only to the writable one (create
parent dirs). Never write under `.../plugins/cache/` even if the OS says it's
writable — a plugin update wipes it.

When the resolved store is a writable sibling `LESSONS.md` and the external
file also exists, offer to merge the external lessons into `LESSONS.md`
(dedup per Lesson format) and delete the external file — lessons collected on
a read-only install otherwise stay stranded there.

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

Install the `## Self-learning` block as the last `## ` section of the target
`SKILL.md` — append it at the end of the file, so the job owns the top of the
body and the constant block sits last. Skip if the block already exists. Fill
`<plugin>` and `<skill>` from the target's path. Do not create any lessons
file; the store appears lazily on the first lesson. Retrofit edits `SKILL.md`,
so it needs an in-place checkout — on a read-only install, report that and
stop.

Block to insert (verbatim, with `<plugin>/<skill>` resolved to the real names):

    ## Self-learning

    Read this skill's lessons and obey them: sibling `LESSONS.md`, else
    `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md` when this
    directory is read-only. On a correction or self-caught mistake, append a
    one-line rule to whichever is writable (creating it) and report where.

## Lesson format

A lessons file is a flat list of imperative rules, one per bullet, newest last:

    # Lessons

    Rules learned for the `<skill>` skill. Read before running; obey each line.

    - <imperative rule, stated so it generalizes past this task>

- One rule per bullet, imperative, terse — the bar of a style rule.
- Conform to the repo markdown style: wrap at ~80 columns, continuation lines
  indented two spaces.
- Concrete and general: "Derive the commit type from the diff, not the branch
  name" — not "the user wanted fix not feat here".
- No dates, ticket ids, or task-specific nouns. A lesson outlives its task.
- Dedup: fold a near-duplicate into the existing rule; never add a twin.
- Create the file with the `# Lessons` header on the first lesson; append after.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Per touched skill, list the file written and the
rules added (or the block installed). Always name the resolved path so the user
knows whether a lesson shipped (sibling `LESSONS.md`) or stayed local
(`.agent-data`); never fabricate a write you could not perform.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/enhance-skills.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
