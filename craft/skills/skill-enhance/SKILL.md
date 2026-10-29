---
name: skill-enhance
description: >
  Records lessons learned during a conversation into the skills that were
  used, so the same mistake never repeats, and retrofits the self-learning
  mechanism into skills that lack it. Use when asked to enhance the skills
  used in this conversation, record lessons learned, capture a correction so
  it does not repeat, or make skills self-improving.
argument-hint: "[all | <skill> | retrofit <skill>]"
license: MIT
---

# skill-enhance

## Usage

```
/craft:skill-enhance [all]              harvest this conversation's lessons into every skill used (default)
/craft:skill-enhance <skill>            harvest only that skill's lessons
/craft:skill-enhance retrofit <skill>   add the ## Self-learning block to that skill's SKILL.md; no harvest
```

Turn corrections into durable skill improvements. No argument or `all` harvests
every skill used. A skill (name or path) narrows Harvest to it: mine only the
corrections that landed while it drove, route what they yield as usual, and
leave every other correction unmined, routed kinds included. A named skill that
never ran yields no lessons; say so in one line, and still retrofit it when it
lacks the block. `retrofit <skill>` runs Retrofit alone. Without an argument,
pick the mode from the request:

- Harvest (default): "enhance the skills I used", "record what you learned",
  "don't make that mistake again". Scan this conversation and write lessons.
- Retrofit: "add self-learning to `<skill>`" is Retrofit alone, no harvest.
  Harvest also runs it on each skill it covers whose in-place `SKILL.md` lacks
  the `## Self-learning` block, a named skill included.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on. Harvest's
proposal waits for a yes, so dropping a word widens nothing.

Each skill appends its own lessons mid-run through that block; Harvest is the
sweep that back-fills what the inline mechanism missed, so expect some of what
you mine to be on file already.

## Lessons store

Lessons never live inline in a `SKILL.md` body: the always-loaded surface stays
lean, and re-authoring a skill cannot clobber what it has learned. Each skill's
lessons live in one of two places; resolve per skill from the directory its
`SKILL.md` sits in, and use the same resolution for reading and writing:

- In-place: directory writable (source checkout or `--plugin-dir` copy) —
  sibling `LESSONS.md`. Committed there, lessons ship to everyone.
- External: read-only or update-clobbered install (under `.../plugins/cache/`)
  — `~/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md`, rooted outside
  the checkout to survive plugin updates. `$AGENT_DATA_DIR` replaces
  `~/.agent-data` when you are told it is set, so a sandbox or an eval can
  redirect the store.

Read both files with the file-read tool, never a shell (the permission check
refuses `${…}` and prompts for reads outside the working directory), passing `~`
as is (the file tools expand it), and obey the union, the sibling winning a
conflict; write only to the writable one, creating parent dirs. Never write
under `.../plugins/cache/` even if the OS says it is writable — a plugin update
wipes it. When the store is a writable sibling `LESSONS.md` and the external
file also exists, offer to merge the external lessons into `LESSONS.md` (dedup
per [Lesson format](#lesson-format)) and delete the external file; lessons
collected on a read-only install otherwise stay stranded there. The offer is
part of the Harvest proposal (step 4) for the skills in scope; reading this
skill's own lessons never triggers it, and this run's own invocation does not
put skill-enhance in scope.


## Harvest

1. List skills used: every skill actually invoked in this conversation (a
   `/<group>:<skill>` call or Skill tool use). Ignore skills only mentioned.

2. Mine each for lessons: where the user corrected the agent, or the agent
   caught its own mistake, while that skill was driving. A lesson is a rule
   that would have changed what the agent did. Four things look like lessons
   and are not:

   - A rule the skill already carries — read its `SKILL.md` before proposing,
     and the reference files it loads for the work in question, since a rule
     stated in a reference governs the run just as firmly as one in the body.
     It was missed, not missing, and a line repeating it costs every future run
     context while changing nothing. Point at the line (`SKILL.md:28`) and
     offer rewording it there — a skill edit, not a lesson — on the first miss
     too: a missed rule was not clear enough to its reader. A rule that lives
     in project data the skill loads at run time (a project's standard, its
     config) is no skill's to reword or restate: name where it lives and drop
     it.
   - A fact about this project or this task: a name, a path, a version, a
     number. It outlives nothing, and the project's own instructions are its
     home.
   - A correction that landed while no skill was driving and routes nowhere
     (below). It belongs to the agent's standing instructions.
   - Praise, a restated requirement, or the skill working as designed.

   Two kinds route to the skill that owns them, whichever skill was driving,
   or none (a run narrowed to a named skill routes only what landed while it
   drove) — a lesson about how a skill ran stays a lesson:

   - A convention for Go or frontend (`.vue`/`.ts`) code the user asked for —
     naming, layout, a construct to use or avoid — is a style rule: route it
     to `go:review learn` or `web:review learn`.
   - A durable fact about the platform the user stated or confirmed is
     knowledge: route it to `srd:questions learn`.

   One correction yields one rule. When two come out of one correction, the
   second is usually the first restated — keep the one that names the
   behaviour to change. A conversation that went well yields none, which is
   the common case and needs no apology.

3. Resolve stores: for each used skill, its `SKILL.md` path and its
   [lessons store](#lessons-store). Ask when the path is unknown or ambiguous.

4. Propose: per skill, the resolved target file, the one-line rules to add, the
   retrofit of the block into each `SKILL.md` that lacks it, and the merge offer
   when a stranded external file exists; then each routed correction under its
   destination. Name in one line each correction you mined and did not file, and
   why — the user asked for their corrections to be recorded, so a silent drop
   is the one outcome they cannot overrule. Wait for confirmation before
   writing.

5. Write: on approval, per skill, retrofit the block if the in-place `SKILL.md`
   lacks it, then append each new rule to the store per
   [Lesson format](#lesson-format), deduplicating against lines already there;
   merge the external file if accepted. Then invoke each destination with
   `learn` through the Skill tool; its own candidate list and confirmation
   gate its writes. A destination missing from your skill list leaves its
   corrections unfiled: name them and the plugin to install.

6. Report per [Output](#output).

## Retrofit

Append the `## Self-learning` block at the end of the target `SKILL.md`, as its
last `## ` section — the job owns the top of the body, the constant block sits
last. Skip when the block already exists. Fill `<plugin>` and `<skill>` from
the target's path. Do not create a lessons file; the store appears on the first
lesson. Retrofit edits `SKILL.md`, so it needs an in-place checkout — on a
read-only install, report that and stop the retrofit of that skill; its
lessons still go to the store, and the other skills still run.

Copy the block below word for word, then substitute `<plugin>`/`<skill>`,
write `<SKILL_DIR>` as a dollar sign, an opening brace, `CLAUDE_SKILL_DIR`, and
a closing brace (spelled out here because the loader would expand it), and
re-wrap the paragraph to 80 columns. Not byte for byte: the substituted path
changes the line's length, so where the wrap falls differs per skill and the
tree already carries five wrappings of the same words. The words are the
constant; the wrapping follows the repo's own rule. That variable and `~` stay
literal — they resolve when the skill runs, not now:

```
## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `<SKILL_DIR>/LESSONS.md` and the fallback
`~/.agent-data/ctx42-skills/lessons/<plugin>/<skill>.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it. ```

## Lesson format

A lessons file is a flat list of imperative rules, one per bullet, newest last:

```
# Lessons

Rules learned for the `<skill>` skill. Read before running; obey each line.

- <imperative rule, stated so it generalizes past this task>
```

- One rule per bullet, one sentence, imperative — the bar of a style rule. A
  rule that needs a clause per case is two rules, or none; a rewrite that
  supersedes one keeps that bar too — no `;`-joined "X when …; Y only when …".
- Wrap at ~80 columns; indent continuation lines two spaces.
- Concrete and general: "Derive the commit type from the diff, not the branch
  name" — not "the user wanted fix not feat here".
- No dates, ticket ids, or task-specific nouns; a lesson outlives its task.
- Dedup: fold a near-duplicate into the existing rule; never add a twin.
- Supersede, don't stack: when a new rule overrules one on file, rewrite that
  line in place and show the before and after in the proposal. Two rules that
  disagree leave the next run to guess which one the user meant.
- A rule that overrules the body is a skill edit, not a lesson: file nothing,
  name the line it contradicts, and hand it to the user. A lessons file cannot
  win an argument with the `SKILL.md` above it — both are read every run, and
  which one prevails is undefined. Narrowing is not overruling: a ban on
  something the body merely permits ("never reach for `chore`" where `chore`
  is an allowed type) leaves the body true, and is a lesson.
- Create the file with the header above on the first lesson; append after.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Per touched skill: the file written and the
rules added, or the block installed — on the write turn the rules were on
screen in the proposal the user just approved, so name the path and how many
rules landed, not the rules again. Always name the resolved path so the user
knows whether a lesson shipped (sibling `LESSONS.md`) or stayed local
(`.agent-data`); never fabricate a write you could not perform.

A run that files nothing is a line or two and stops there: what was mined and
that nothing qualified ("No lessons: `craft:cm` drew no corrections."). Do not
account for the retrofit check, name the store path a lesson would have taken,
or explain what did not happen — the only resolved path worth naming is one
something was written to. An empty run has the least to report, and is where the
report most often grows instead. When every mined correction was dropped, the report is one line per
correction with its reason, as Propose names them, and nothing else.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/skill-enhance.md` (pass `~`
as is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR`
replaces `~/.agent-data` only when you are told it is set). The sibling wins a
conflict; the fallback, which a read-only install writes, still counts once the
checkout is writable; this block never moves or merges lessons. A missing file
needs no comment. On a correction or self-caught mistake, append a one-line rule
— general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
