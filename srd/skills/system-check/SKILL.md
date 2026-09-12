---
name: system-check
description: >
  Reviews a Software Requirement Document (SRD) as the engineer who must
  build it, surfacing the questions that block implementation. Use when
  asked to review an SRD for build-readiness, ask implementation questions
  about an SRD, check which SRD questions remain open, or bank durable
  platform facts the current session surfaced.
argument-hint: "<path to SRD> | learn"
license: MIT
---

# system-check

Review an SRD from the seat of the engineer who has to build it. The question
that drives every check: *can I implement and test this exactly as written,
without coming back to guess?*

This skill is a **thin orchestration layer**: it delegates the standard checks
to `srd:review` and adds the **system-knowledge layer** — judging the SRD
against the target platform as the `srd-doc` corpus records it.

## Boundaries

- Role: implementation-readiness reviewer. Produce questions for the SRD
  author; never rewrite the document.
- Owns: `<srd>.questions.md` (the question list). No other skill writes it.
- Must not: write or edit `<srd>.review.md` (owned by `srd:review`); edit the
  SRD; re-implement or restate the SRD standard checks; write a knowledge-base
  file (owned by `srd:kb`).
- Depends on: `srd:review`, which itself reads `../create/references/*`; this
  skill never reads the SRD standard directly. If `srd:review` is missing at
  run time, stop and tell the user.

## Support files

- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (eager) — how to reach the documentation corpus, how its sources rank, and
  where an unconfirmed or undocumented fact goes (`srd:report-doc-gap`,
  `srd:kb`).

## Documentation corpus

The system-knowledge layer confronts the SRD against the corpus, whose
knowledge-base source carries the platform facts earlier sessions banked. This
skill consults it in system confrontation and before any "is this defined or
documented?" question (step 3); a fact the walk confirms goes to `srd:kb` (see
[Platform knowledge](#platform-knowledge)). Both delegates drain at step 1,
buffer silently in between, and `srd:kb` writes when the walk ends.

## Invocation

`$1` is the SRD path, or a literal mode word. With no `$ARGUMENTS`, ask which SRD
to check; fall back to the user's prose for free-form input.

- `$1` = an SRD path → **review** (default): the full flow below. Re-running on
  an SRD that already has a `<srd>.questions.md` resumes the open questions (see
  [Re-run](#re-run-after-an-srd-edit)).
- `$1` = `learn` → **learn**: bank durable platform facts from the current
  session, no SRD. See [learn](#learn).

## review (default)

1. Start: invoke `srd:report-doc-gap` and `srd:kb` to drain what a prior
   session left buffered for this SRD, then resolve the corpus (see
   [Support files](#support-files)). With none reachable, skip the
   system-knowledge layer and run the review layer alone rather than stopping.
2. Get the review without clobbering it:
   - `<srd>.review.md` exists → read it as-is. Do **not** run `srd:review` —
     never risk overwriting the author's file.
   - absent → run `srd:review path/to/srd.md` once to create it, then read it.
3. Build the merged question set:
   - From the review: reframe each relevant finding as a colleague-voice
     question. Drop its severity tag and rule id (keep the severity only to
     order the walk, step 5).
   - System confrontation, the layer only this skill does: confront the SRD
     against the corpus. Raise a question when the SRD contradicts a documented
     API rule, service behavior, or glossary term; redefines or conflicts with
     another SRD; uses a term undefined in the system; or cannot be built
     without knowing something the system does not pin down ("can't build X
     without knowing Y").
   - Before raising any "is this defined or documented?" question, look it up
     first: `search` the corpus, then `get_doc` the promising hit. Ask only
     when it genuinely is not there or what you found is partial, and then say
     what you found and what it fails to cover; a competent engineer does not
     ask what they could have looked up. When the lookup shows the docs
     themselves at fault, also hand the gap to `srd:report-doc-gap`.
   - Stale citation: when a knowledge-base page cites a corpus id absent from
     `list_docs`, raise it as a question too and hand the repair to `srd:kb`.
4. Write `<srd>.questions.md` next to the SRD (open questions only), per
   [Questions file](#questions-file).
5. Walk one question at a time (see [Walk](#walk)), ordered: was-blocker
   first, then system-confrontation and was-major questions, then was-minor
   last. No severity tags or rule ids ever appear — priority is felt through
   order.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. A short pointer ("wrote `<srd>.questions.md`,
N open questions") is enough — do not re-list the questions you just wrote.

## Walk

Go through the questions file **one item at a time**. Never batch. For each
question, the interaction ends in one of:

- Answer: the user answers. Restate the resolution in a line, folding any
  durable platform fact it carries into the restatement, so confirming it
  confirms both. Then remove the item from the questions file and hand the
  fact to `srd:kb`, which captures it silently — never a separate "bank this?"
  prompt (see [Platform knowledge](#platform-knowledge)).
- More context: the user explains. Restate the same way; the question may stay
  open, get refined, or resolve.
- Collaborate: together add, split, or refine questions in the file.

Confirm each change to the questions file as you make it, one at a time. The
file shrinks toward empty as the SRD becomes clear; the user can stop anytime
and resume later.

**Stay on the current question until the user says to move on.** Do not advance
on your own — the user may want several edits to the same item first. When the
walk ends — no questions remain, or the user stops — let `srd:kb` write its
confirmed facts. With no questions left, the SRD is build-ready from the
implementer's view.

## Re-run after an SRD edit

Re-running `/system-check path/to/srd.md` when `<srd>.questions.md` already
exists is **resume mode**. Step 1 of review still runs; then:

1. Refresh the review layer non-destructively: run `srd:review path/to/srd.md
   check` — it strikes resolved findings, keeps open ones, appends defects the
   edit introduced, and bumps `Updated:`. It never rewrites the file.
2. Re-check each open question against the current SRD; drop the ones the edit
   answered and tell the user which.
3. Re-run system confrontation on the new text for fresh contradictions or gaps.
4. Walk the refreshed open set.

## learn

`/system-check learn` banks what the **current session** taught about the
platform — no SRD, no walk. Use it when a conversation that was not SRD work
(a debugging session, a design discussion, a call you are recounting) surfaced
durable facts, before they scroll away.

1. Scan this session for durable, reusable platform facts: general facts about
   the system the user stated or confirmed, not ones specific to an SRD,
   ticket, or review, and never something the agent inferred. Restatements of
   an SRD in play do not qualify.
2. Restate the candidates once, as one list; the user's confirmation is the
   gate, and a correction corrects the list.
3. Hand the confirmed facts to `srd:kb`; coverage checks against the corpus,
   dedup, and the writing are its job, not this skill's.

Report tersely: what was banked and what was dropped as already covered, once.

## Questions file

Open with YAML frontmatter carrying `cfsync-plugin: ignore-push` verbatim, so
the Confluence sync never pushes this generated artifact.

```
---
cfsync-plugin: ignore-push
---

# SRD Questions — <Document Title>

Source: `path/to/srd.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** <problem in a sentence, then the one thing to decide — colleague voice>

**Q2** <...>
```

- One focused ask per question: if a requirement raises two concerns, write
  two questions.
- Problem only: say what is missing, ambiguous, or contradictory. Do not
  propose the fix or write before/after rewrites.
- Collaborative voice: "What do we want to…", "should we…", "where should
  this live…" — frame decisions as shared, not as an interrogation.
- Ask directly: no meta phrasing ("what did the author intend").
- Reference the SRD's requirement ids inline (GR-4, SEC-9…) so the question
  is actionable; keep the sentence human.
- No tags: no severity, no rule ids, no `[type]` brackets — those guide your
  analysis and the walk order, never the file.
- Questions are not list items: each begins with its bold `Qn` id, separated by
  one blank line.
- Sequential ids in walk order (`Q1`, `Q2`, …), stable across re-runs — when
  one is removed, do not renumber the survivors.

Good:

  **Q3** SEC-1c says to enforce timeouts but gives no numbers and no place they
  live. What values are we going with, and where do they sit? QA can't test it.

Bad:

  - [testability] §SEC-1c — "enforce timeout policies" is not measurable.

## Platform knowledge

This skill reads platform knowledge and stores none: a durable, reusable
platform fact the walk or `learn` confirms goes to `srd:kb`, the knowledge
base's single owner, and confirmation rides on this skill's own restatement
(see [Walk](#walk)) — never on a prompt of its own.

Old pattern: a `memory.md` under `$HOME/.agent-data/ctx42-skills/srd/` is the
leftover of a retired per-machine store. Its tribal facts belong in the
knowledge base through `srd:kb`; its documented facts are served live by the
corpus.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/system-check.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
