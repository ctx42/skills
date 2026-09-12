# system-check

Reviews a **Software Requirement Document (SRD)** from the seat of the engineer
who has to build it: *can I implement and test this exactly as written, without
coming back to guess?*

## Usage

```
/system-check path/to/srd.md   review + walk (default): resumes open questions on re-run
/system-check learn            bank platform facts this session taught into the knowledge base
```

On a re-run after the SRD was edited, the skill runs `srd:review … check`
(non-destructive: strikes fixed, appends new), drops open questions the edit
answered, re-runs system confrontation, and walks the refreshed open set.

## When to Use

- You receive an SRD and need to know whether the team can build it as written.
- Before breaking an SRD into Epics and Tasks, to clear implementation unknowns.
- After the author edits the SRD, to see what questions are still open.
- To bank platform facts a session taught you, so the next agent can retrieve
  them.

## How It Works

It is a **thin orchestration layer**. The standard, logic, and consistency
checks are delegated to `srd:review`; this skill adds the **system-knowledge
layer** — confronting the SRD against the platform as the `srd-doc` corpus
records it — and presents the whole thing as one author-facing question list it
walks one question at a time. It produces questions, never rewrites.

- Delegation: for the standard checks the skill reuses `srd:review` instead of
  re-implementing them. It never writes `<srd>.review.md`:
  - if that file exists, it is read as-is (review is **not** run, so the
    author's file is never clobbered);
  - if absent, `srd:review` is run once to create it.
- Merge: review findings are reframed into colleague-voice questions and merged
  with the system-confrontation questions into `<srd>.questions.md`.
- Walk: questions are walked one at a time, ordered by underlying severity
  (was-blocker first, then system + was-major, then was-minor) — but no severity
  tags or rule ids ever appear in the file. Answering a question removes it; a
  durable platform fact in the answer is confirmed through the skill's own
  restatement of the resolution, never a separate prompt.
- Platform knowledge: the skill reads platform facts from the `srd-doc` corpus,
  whose knowledge-base source carries what earlier sessions banked, and stores
  nothing itself. Every confirmed fact goes to `srd:kb`, which owns the
  knowledge base.
- Learn: `learn` sweeps the current conversation for durable platform facts you
  stated, restates them once for confirmation, and hands them to `srd:kb`,
  which drops what the corpus already covers — no SRD needed.

## What to Expect

- A `<srd>.questions.md` next to the source holding open questions only, in
  colleague voice, each referencing the SRD's requirement ids.
- The questions file shrinks toward empty as answers come in; when nothing
  remains, the SRD is build-ready from the implementer's view.
- The skill never edits the SRD or `<srd>.review.md`, and never writes a
  knowledge-base file itself — every fact goes through `srd:kb`, confirmed as
  part of the walk.

## Evaluations

### 1. Build-readiness review surfaces a system contradiction

**Request:** `/system-check specs/labeling.md`, where `GR-4` mandates camelCase
JSON response fields, no `<srd>.review.md` exists, and the corpus carries a
documented API rule requiring snake_case response fields.

**Expected behavior:**
- Drains `srd:report-doc-gap` and `srd:kb` for this SRD first; with empty
  buffers, says nothing about them.
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

### 3. Looks it up before asking; banks the answer

**Request:** During a walk, the open question asks whether "Namespace" is a
defined term; the user answers and says "remember that sessions can't span
tenants."

**Expected behavior:**
- Searches the corpus and confirms "Namespace" is defined in the Glossary before
  raising it — does not ask what it could have looked up.
- Restates the resolution with the tenant fact folded in; on confirmation,
  removes the question from the questions file.
- Hands the fact to `srd:kb` rather than writing any file itself; no separate
  "bank this?" prompt appears.

### 4. Stale citation becomes a question

**Request:** A walk consults a knowledge-base page that cites a corpus document
id no longer present in `list_docs`.

**Expected behavior:**
- Raises the stale citation as a question alongside the others.
- Hands the repair to `srd:kb`, which owns knowledge-base files, rather than
  editing the page here.
- Does not silently drop the fact the stale page carried.

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
- Restates both candidates once as one list and takes the user's confirmation
  as the gate; does not restate the SRD in play.
- Hands the confirmed facts to `srd:kb`, whose coverage check drops the
  documented one and banks only the tribal one.
- Reports what was banked and what was dropped as already covered, once,
  without re-printing the page.
