---
name: system-check
description: >
  Reviews a Software Requirement Document (SRD) as the engineer who must build
  it. Delegates standard, logic, and consistency checks to review,
  then adds a system-knowledge layer — confronting the SRD against a curated
  memory of the target platform to surface contradictions with documented API
  rules, services, or glossary, terms undefined in the system, and gaps that
  block implementation. Presents everything as one author-facing question list,
  walked one question at a time, and grows its memory from the answers. Use when
  asked to review an SRD for build-readiness, ask implementation questions about
  an SRD, or check what SRD questions remain open.
license: MIT
---

# system-check

Review an SRD from the seat of the engineer who has to build it. The question
that drives every check: *can I implement and test this exactly as written,
without coming back to guess?*

This skill is a **thin orchestration layer**. It does not re-run the standard
checks — it delegates those to `review` — and it never rewrites prose. Its
own value is the **system-knowledge layer**: judging the SRD against what is
already known about the target platform, as captured in `memory.md`.

## Boundaries

- **Role:** implementation-readiness reviewer. Produce questions for the SRD
  author; never rewrite the document.
- **Owns:** `<srd>.questions.md` (the question list) and `memory.md` (the system
  knowledge base). No other skill writes these.
- **Must not:** write or edit `<srd>.review.md` (owned by `review`); edit the
  SRD; re-implement or restate the SRD standard checks.
- **Depends on:** `review`, which itself reads `../create/references/*`.
  This skill does **not** read the SRD standard directly — it gets standard
  findings through `review`. If `review` is missing at run time, stop and
  tell the user.

## Support files

- **`memory.md`** — the target platform's system knowledge base. Read it first
  every run. Atomic one-fact-per-line, grouped by topic, each line carrying the
  source it came from. It is **user data, not shipped content** — resolve its
  location per [Where memory.md lives](#where-memorymd-lives) below, not by
  assuming this skill's directory. See [Memory](#memory).
- **`memory.template.md`** (this skill's directory) — the empty scaffold used to
  seed a fresh `memory.md`. Read-only; never write facts here.

### Where memory.md lives

`memory.md` holds machine-specific, growing user data, so it must not live in
this skill's directory, which the host replaces on every plugin update. It lives
in one fixed, tool-agnostic location on the machine, shared by every tool
(Claude, Grok) and every project — one platform memory, update-safe everywhere.

**Resolve the path once per run** with a shell command, then use it for every
read and write below (the plugin data variables are not portable — Claude
substitutes `${CLAUDE_PLUGIN_DATA}` but Grok does not — so resolve from `$HOME`
instead):

```bash
MEM_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/ctx42-srd"
mkdir -p "$MEM_DIR"
MEM="$MEM_DIR/memory.md"   # the memory.md every step below reads and writes
```

**First run and migration** (do once; confirm the file change with the user):

- `$MEM` exists → use it.
- `$MEM` does not exist, but an old `memory.md` with facts sits in this skill's
  directory (a pre-move checkout, or dev use) → offer to move that file to
  `$MEM`, then use it.
- Neither exists → seed `$MEM` from `memory.template.md` in this skill's
  directory.

## Invocation

Detect the mode from the user's words.

- `/system-check path/to/srd.md` → **review** (default): the full flow below.
  Re-running on an SRD that already has a `<srd>.questions.md` resumes the open
  questions (see [Re-run](#re-run-after-an-edit)).
- `/system-check memory` → **memory**: curate `memory.md` only, no SRD. See
  [Memory mode](#memory-mode).

## review (default)

1. **Validate memory.** Read `memory.md`. It may be **empty** — a fresh checkout
   with no facts yet. That is fine: skip the system-knowledge layer for now, lean
   on the review layer alone, and start growing memory from the answers. If it
   has facts, check the space root declared in its header: when it is set and
   resolves, use it for live-doc lookups; when it is unset (a placeholder) or
   does not resolve, ask the user for it once — and if they have no space docs,
   proceed without the live-doc layer rather than stopping.
2. **Get the review without clobbering it.**
   - `<srd>.review.md` exists → read it as-is. Do **not** run `review` —
     never risk overwriting the author's file.
   - absent → run `review path/to/srd.md` once to create it, then read it.
3. **Build the merged question set:**
   - **From the review** — reframe each relevant finding as a colleague-voice
     question. Drop its severity tag and rule id (keep the severity only to order
     the walk, step 5).
   - **System confrontation** — the layer only this skill does. Confront the SRD
     against `memory.md` and the live space docs it points to. If memory is empty
     and no space root is configured, **skip this layer**: the review reduces to
     the `review` findings, and you begin populating memory from the answers.
     Raise a question
     when the SRD: contradicts a documented API rule, service behavior, or
     glossary term; redefines or conflicts with another SRD; uses a term
     undefined in the system; or cannot be built without knowing something the
     system does not pin down ("can't build X without knowing Y").
   - Before raising any "is this defined / documented?" question, **look it up
     first** — in `memory.md`, then in the space docs its source pointers
     reference. Only ask if it genuinely is not there or what you found is
     partial — then say what you found and what it fails to cover. A competent
     engineer does not ask what they could have looked up.
   - **Memory health** — when a fact you consult cites a path that no longer
     resolves under the space root, raise it as a question too (e.g. "`memory`
     points to `Services/Foo.md` — renamed or removed?") and offer to fix the
     pointer.
4. **Write `<srd>.questions.md`** next to the SRD (open questions only). Format
   per [Questions file](#questions-file).
5. **Walk one question at a time** (see [Walk](#walk)), ordered: was-blocker
   first, then system-confrontation and was-major questions, then was-minor last.
   No severity tags or rule ids ever appear — priority is felt through order.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. A short pointer ("wrote `<srd>.questions.md`,
N open questions") is enough — do not re-list the questions you just wrote.

## walk

Go through the questions file **one item at a time**. Never batch. For each
question, the interaction ends in one of:

- **Answer** — the user answers. Remove the resolved item from the questions
  file, and offer to save the reusable fact to `memory.md` (see [Memory](#memory)).
- **More context** — the user explains. If it is a durable system fact, offer to
  save it. The question may stay open, get refined, or resolve.
- **Collaborate** — together add, split, or refine questions in the file.

Every interaction may update the questions file and/or `memory.md`. Confirm each
file change as you make it, one at a time. The questions file shrinks toward
empty as the SRD becomes clear; the user can stop anytime and resume later.

**Stay on the current question until the user says to move on.** Do not advance
on your own — the user may want several edits to the same item first. When no
questions remain, the SRD is build-ready from the implementer's view.

## Re-run after an SRD edit

Re-running `/system-check path/to/srd.md` when `<srd>.questions.md` already
exists is **resume mode**:

1. Refresh the review layer non-destructively: run `review path/to/srd.md
   check` — it strikes resolved findings, keeps open ones, appends defects the
   edit introduced, and bumps `Updated:`. It never rewrites the file.
2. Re-check each open question against the current SRD; drop the ones the edit
   answered and tell the user which.
3. Re-run system confrontation on the new text for fresh contradictions or gaps.
4. Walk the refreshed open set.

## memory mode

`/system-check memory` curates `memory.md` only — no SRD involved:

1. Check the header space root. If it is unset or does not resolve, ask the user
   for it; if they have no space docs, leave it as a placeholder and skip the
   pointer checks below (an empty memory has nothing to validate yet).
2. Validate every source pointer resolves under the root. Report each broken
   one and offer a fix (corrected path, or `[unwritten]` if the doc is gone).
3. Flag duplicate or overlapping facts; offer to merge.
4. Offer to regroup facts whose topic heading no longer fits.

One change at a time; confirm each edit. Make no change silently.

## Questions file

```
# SRD Questions — <Document Title>

Source: `path/to/srd.md`

Open questions only. Resolved items are removed; durable facts go to memory.md.

**Q1** <problem in a sentence, then the one thing to decide — colleague voice>

**Q2** <...>
```

- **One focused ask per question.** If a requirement raises two concerns, write
  two questions.
- **Problem only.** Say what is missing, ambiguous, or contradictory. Do not
  propose the fix or write before/after rewrites.
- **Collaborative voice.** "What do we want to…", "should we…", "where should
  this live…" — frame decisions as shared, not as an interrogation.
- **Ask directly.** No meta phrasing ("what did the author intend").
- **Reference the SRD's requirement ids inline** (GR-4, SEC-9…) so the question
  is actionable; keep the sentence human.
- **No tags.** No severity, no rule ids, no `[type]` brackets — those guide your
  analysis and the walk order, never the file.
- Questions are not list items: each begins with its bold `Qn` id, separated by
  one blank line. Lines stay within 80 columns.
- **Sequential ids** in walk order (`Q1`, `Q2`, …), stable across re-runs — when
  one is removed, do not renumber the survivors.

Good:

  **Q3** SEC-1c says to enforce timeouts but gives no numbers and no place they
  live. What values are we going with, and where do they sit? QA can't test it.

Bad:

  - [testability] §SEC-1c — "enforce timeout policies" is not measurable.

## Memory

`memory.md` is the durable system knowledge base — a curated, growing list of
atomic one-line facts that lets the implementer confront the SRD without
re-reading the whole platform. Maintaining it is a first-class job of this skill.
It lives in one fixed per-machine location, not this skill's directory (see
[Where memory.md lives](#where-memorymd-lives)); a fresh machine seeds it from
`memory.template.md`.

Format:

- A **header line declares the space root** — the local path every source
  pointer is relative to. It is machine-specific and set by each user; the
  seeded file carries it as a placeholder, and the skill runs without the
  live-doc layer until it is set.
- **One fact per line, grouped under a topic heading.** Each line states the
  fact succinctly and ends with the source in brackets: `[Services/Some
  Service.md]` for a documented fact, `[unwritten]` for tribal knowledge that
  lives in no doc. Use `[same]` to repeat the previous line's source.

Writing rules:

- Write to memory only on the user's explicit instruction ("remember …") or
  after the user accepts a "want me to remember this?" offer. During the walk,
  proactively offer when an answer is a durable, reusable system fact.
- Before writing, **show the exact line and the target topic heading**, and get
  confirmation. Never write to memory silently.
- Keep entries to one dense sentence; add a source pointer (the doc that proves
  it, or `[unwritten]`).
- Phrase as a general, durable system fact. Do **not** reference the SRD or
  feature ticket that surfaced it — memory describes the system, not the review.
- Do not cite a reference as proof a term is undefined unless that reference is
  known complete (some glossaries are partial — see the note in `memory.md`).

## Guardrails

- Never edit the SRD or `<srd>.review.md`. You write only `<srd>.questions.md`
  and `memory.md`.
- One change at a time; confirm each file edit.
- Keep both companion files within 80 columns.
