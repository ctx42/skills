# system-check

Reviews a **Software Requirement Document (SRD)** from the seat of the engineer
who has to build it. The driving question: *can I implement and test this
exactly as written, without coming back to guess?*

It is a **thin orchestration layer**. The standard, logic, and consistency
checks are delegated to `srd:review`; this skill adds the **system-knowledge
layer** — confronting the SRD against a curated memory of the target platform
— and presents the whole thing as one author-facing question list it walks one
question at a time. It produces questions, never rewrites.

## When to Use

- You receive an SRD and need to know whether the team can build it as written.
- Before breaking an SRD into Epics and Tasks, to clear implementation unknowns.
- After the author edits the SRD, to see what questions are still open.
- To keep a living record of platform facts learned across reviews.

## How It Works

- **Memory.** `memory.md` is a curated, growing list of atomic one-line facts
  about the platform, grouped by topic, each tagged with its source doc (or
  `[unwritten]`). A header line declares the absolute space root; pointers are
  relative to it. The skill validates the root every run and flags any pointer
  that no longer resolves. Maintaining memory is a first-class job — facts are
  added from answers during the walk, always with your confirmation. Memory is
  the **tribal layer**: it prefers what the docs do not carry, and
  `memory-clean` prunes back any fact the `srd-doc` corpus now covers.
- **Learn.** `learn` sweeps the current conversation for durable platform facts,
  keeps only those neither `memory.md` nor the corpus already covers, and banks
  each as `[unwritten]` on your confirmation — no SRD needed.
- **Delegation.** For the standard checks the skill reuses `srd:review` instead
  of re-implementing them. It never writes `<srd>.review.md`:
  - if that file exists, it is read as-is (review is **not** run, so the
    author's file is never clobbered);
  - if absent, `srd:review` is run once to create it.
- **Merge.** Review findings are reframed into colleague-voice questions and
  merged with the system-confrontation questions into `<srd>.questions.md`.
- **Walk.** Questions are walked one at a time, ordered by underlying severity
  (was-blocker first, then system + was-major, then was-minor) — but no severity
  tags or rule ids ever appear in the file. Answering a question removes it and
  offers to save any durable fact to memory.

## Usage

```
/system-check path/to/srd.md   review + walk (resumes open questions on re-run)
/system-check memory           curate memory.md structurally (validate, dedupe, regroup)
/system-check learn            bank durable system facts learned this session into memory
/system-check memory-clean     prune memory of facts the srd-doc corpus now covers
```

On a re-run after the SRD was edited, the skill runs `srd:review … check`
(non-destructive: strikes fixed, appends new), drops open questions the edit
answered, re-runs system confrontation, and walks the refreshed open set.

## What to Expect

- A `<srd>.questions.md` next to the source holding open questions only, in
  colleague voice, each referencing the SRD's requirement ids.
- The questions file shrinks toward empty as answers come in; when nothing
  remains, the SRD is build-ready from the implementer's view.
- The skill never edits the SRD or `<srd>.review.md`, and never writes to memory
  without showing the exact line and getting confirmation.

## Evaluations

### 1. Build-readiness review surfaces a system contradiction

**Request:** `/system-check specs/labeling.md`, where `GR-4` mandates camelCase
JSON response fields, no `<srd>.review.md` exists, and `memory.md` records a
documented API rule requiring snake_case response fields.

**Expected behavior:**
- Runs `srd:review specs/labeling.md` once to create `specs/labeling.review.md`,
  then reads it — makes no edit to the SRD.
- Writes `specs/labeling.questions.md` merging the review findings (reframed,
  untagged) with a system question noting `GR-4` contradicts that API rule.
- Walks one question at a time; does not advance until the user moves on.

### 2. Resume after an SRD edit

**Request:** `/system-check specs/labeling.md` re-run after the author edited
the SRD, with `specs/labeling.questions.md` and `specs/labeling.review.md`
already present.

**Expected behavior:**
- Runs `srd:review specs/labeling.md check` (strikes fixed findings, appends new
  ones, bumps `Updated:`) rather than overwriting the review file.
- Drops the open questions the edit answered, naming which, and re-runs system
  confrontation for new gaps.
- Walks only the refreshed open set.

### 3. Looks it up before asking; grows memory from the answer

**Request:** During a walk, the open question asks whether "Namespace" is a
defined term; the user answers and says "remember that sessions can't span
tenants."

**Expected behavior:**
- Confirms "Namespace" is defined in `memory.md` / the Glossary before raising
  it — does not ask what it could have looked up.
- Removes the resolved question from the questions file.
- Offers a single succinct memory line with a source pointer (or `[unwritten]`),
  shows the exact line and target topic heading, and writes only on confirmation.

### 4. Broken memory pointer becomes a question

**Request:** `/system-check memory` after `Services/Billing Service.md` was
renamed in the space.

**Expected behavior:**
- Validates the header space root, then every source pointer; reports the
  unresolved `Services/Billing Service.md` lines.
- Offers a fix per broken pointer (corrected path, or `[unwritten]`), one change
  at a time, writing nothing silently.

### 5. Terse output

**Request:** `/system-check specs/labeling.md` on a clean run.

**Expected behavior:**
- No preamble or step narration ("I'll now read…", "Let me run review").
- After writing the file, reports a one-line pointer (e.g. "wrote
  `specs/labeling.questions.md`, 6 open questions") without re-listing the
  questions already in the file.
- Opens the walk with the first question, not a summary of what it just did.

### 6. Learn banks only uncovered session facts

**Request:** `/system-check learn` after a conversation surfaced two platform
facts — one the `srd-doc` corpus already documents, one tribal (in no doc).

**Expected behavior:**
- Resolves the corpus, then drops the documented fact after a `search`/`get_doc`
  confirmation and keeps only the tribal one.
- Shows the surviving line and its target topic heading, writes it as
  `[unwritten]` only on confirmation, and does not restate the SRD in play.
- Reports what was banked and what was dropped as already-covered, without
  re-printing `memory.md`.

### 7. memory-clean prunes corpus-covered facts

**Request:** `/system-check memory-clean` when the corpus is present and one
`memory.md` line is now fully documented in an srd-doc page.

**Expected behavior:**
- Requires the corpus; would stop if none were reachable.
- Confirms coverage via `search`/`get_doc`, then offers to remove the covered
  line by default (repoint to the doc id as the escape hatch), one change at a
  time, nothing silent.
- Leaves partially-covered facts in place and reports removed/repointed/kept
  counts once.
