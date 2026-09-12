---
name: enhance-skills
description: >
  Records lessons learned during a conversation into the skills that were
  used, so the same mistake never repeats, and retrofits the self-learning
  mechanism into skills that lack it. Use when asked to enhance the skills
  used in this conversation, record lessons learned, capture a correction so
  it does not repeat, or make skills self-improving.
argument-hint: "[<skill> to retrofit]"
license: MIT
---

# enhance-skills

Turn corrections into durable skill improvements. `$ARGUMENTS` naming a skill
(name or path) selects Retrofit; otherwise pick the mode from the request:

- Harvest (default): "enhance the skills I used", "record what you learned",
  "don't make that mistake again". Scan this conversation and write lessons.
- Retrofit: "add self-learning to `<skill>`". Harvest also runs it on any used
  skill whose in-place `SKILL.md` lacks the `## Self-learning` block.

## Lessons store

Each skill's lessons live in one of two places; resolve per skill from the base
dir the host reports, and use the same resolution for reading and writing:

- In-place: directory writable (source checkout or `--plugin-dir` copy) —
  sibling `LESSONS.md`. Committed there, lessons ship to everyone.
- External: read-only or update-clobbered install (under `.../plugins/cache/`)
  — `$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`,
  `$HOME`-rooted to survive plugin updates.

Read both files when both exist and obey the union; write only to the writable
one, creating parent dirs. Never write under `.../plugins/cache/` even if the OS
says it is writable — a plugin update wipes it. When the store is a writable
sibling `LESSONS.md` and the external file also exists, offer to merge the
external lessons into `LESSONS.md` (dedup per [Lesson format](#lesson-format))
and delete the external file; lessons collected on a read-only install
otherwise stay stranded there.

## Harvest

1. List skills used: every skill actually invoked in this conversation (a
   `/<group>:<skill>` call or Skill tool use). Ignore skills only mentioned.
2. Mine each for lessons: where the user corrected the agent, or the agent
   caught its own mistake, while that skill was driving. A lesson is a concrete
   rule that would prevent a recurrence — not a one-off fact about this task.
   Skip praise, restated requirements, and task-specific detail.
3. Resolve stores: for each used skill, its `SKILL.md` path and its
   [lessons store](#lessons-store). Ask when the path is unknown or ambiguous.
4. Propose: per skill, the resolved target file, the one-line rules to add, and
   the merge offer when a stranded external file exists. Wait for confirmation
   before writing.
5. Write: on approval, per skill, retrofit the block if the in-place `SKILL.md`
   lacks it, then append each new rule to the store per
   [Lesson format](#lesson-format), deduplicating against lines already there;
   merge the external file if accepted.
6. Report per [Output](#output).

## Retrofit

Append the `## Self-learning` block at the end of the target `SKILL.md`, as its
last `## ` section — the job owns the top of the body, the constant block sits
last. Skip when the block already exists. Fill `<plugin>` and `<skill>` from
the target's path. Do not create a lessons file; the store appears on the first
lesson. Retrofit edits `SKILL.md`, so it needs an in-place checkout — on a
read-only install, report that and stop.

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
- Wrap at ~80 columns; indent continuation lines two spaces.
- Concrete and general: "Derive the commit type from the diff, not the branch
  name" — not "the user wanted fix not feat here".
- No dates, ticket ids, or task-specific nouns; a lesson outlives its task.
- Dedup: fold a near-duplicate into the existing rule; never add a twin.
- Create the file with the header above on the first lesson; append after.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Per touched skill: the file written and the
rules added, or the block installed. Always name the resolved path so the user
knows whether a lesson shipped (sibling `LESSONS.md`) or stayed local
(`.agent-data`); never fabricate a write you could not perform.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/enhance-skills.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
