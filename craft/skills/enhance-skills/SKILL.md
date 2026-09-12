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

## Usage

```
/enhance-skills          harvest this conversation's lessons into the skills used (default)
/enhance-skills <skill>  retrofit the ## Self-learning block into that skill's SKILL.md
```

Turn corrections into durable skill improvements. `$ARGUMENTS` naming a skill
(name or path) selects Retrofit; otherwise pick the mode from the request:

- Harvest (default): "enhance the skills I used", "record what you learned",
  "don't make that mistake again". Scan this conversation and write lessons.
- Retrofit: "add self-learning to `<skill>`". Harvest also runs it on any used
  skill whose in-place `SKILL.md` lacks the `## Self-learning` block.

Each skill appends its own lessons mid-run through that block; Harvest is the
sweep that back-fills what the inline mechanism missed, so expect some of what
you mine to be on file already.

## Lessons store

Lessons never live inline in a `SKILL.md` body: the always-loaded surface stays
lean, and re-authoring a skill cannot clobber what it has learned. Each skill's
lessons live in one of two places; resolve per skill from the base dir the host
reports, and use the same resolution for reading and writing:

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
   caught its own mistake, while that skill was driving. A lesson is a rule
   that would have changed what the agent did. Four things look like lessons
   and are not:

   - A rule the skill's body already states — read the `SKILL.md` before
     proposing. It was missed, not missing, and a line repeating it costs
     every future run context while changing nothing. A rule that keeps
     getting missed needs rewording in `SKILL.md`: a skill edit, not a lesson.
   - A fact about this project or this task: a name, a path, a version, a
     number. It outlives nothing, and the project's own instructions are its
     home.
   - A correction that landed while no skill was driving. It belongs to the
     agent's standing instructions and has no skill to own it.
   - Praise, a restated requirement, or the skill working as designed.

   One correction yields one rule. When two come out of one correction, the
   second is usually the first restated — keep the one that names the
   behaviour to change. A conversation that went well yields none, which is
   the common case and needs no apology.

3. Resolve stores: for each used skill, its `SKILL.md` path and its
   [lessons store](#lessons-store). Ask when the path is unknown or ambiguous.

4. Propose: per skill, the resolved target file, the one-line rules to add, and
   the merge offer when a stranded external file exists. Name in one line each
   correction you mined and did not file, and why — the user asked for their
   corrections to be recorded, so a silent drop is the one outcome they cannot
   overrule. Wait for confirmation before writing.

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

Copy the block below with its line breaks, so every skill in the tree carries
it byte for byte. `$HOME` stays literal — it is read when the skill runs, not
now:

```
## Self-learning

Obey this skill's lessons when it has any: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md` when this
directory is read-only. Most runs have none; absence is the normal case and
needs no comment. On a correction or self-caught mistake, append a one-line
rule to whichever path is writable, creating it, and report where.
```

## Lesson format

A lessons file is a flat list of imperative rules, one per bullet, newest last:

```
# Lessons

Rules learned for the `<skill>` skill. Read before running; obey each line.

- <imperative rule, stated so it generalizes past this task>
```

- One rule per bullet, one sentence, imperative — the bar of a style rule. A
  rule that needs a clause per case is two rules, or none.
- Wrap at ~80 columns; indent continuation lines two spaces.
- Concrete and general: "Derive the commit type from the diff, not the branch
  name" — not "the user wanted fix not feat here".
- No dates, ticket ids, or task-specific nouns; a lesson outlives its task.
- Dedup: fold a near-duplicate into the existing rule; never add a twin.
- Supersede, don't stack: when a new rule overrules one on file, rewrite that
  line in place and show the before and after in the proposal. Two rules that
  disagree leave the next run to guess which one the user meant.
- Create the file with the header above on the first lesson; append after.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Per touched skill: the file written and the
rules added, or the block installed. Always name the resolved path so the user
knows whether a lesson shipped (sibling `LESSONS.md`) or stayed local
(`.agent-data`); never fabricate a write you could not perform.

## Self-learning

Obey this skill's lessons when it has any: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/enhance-skills.md` when this
directory is read-only. Most runs have none; absence is the normal case and
needs no comment. On a correction or self-caught mistake, append a one-line
rule to whichever path is writable, creating it, and report where.
