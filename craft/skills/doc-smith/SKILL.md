---
name: doc-smith
description: >
  Writes new technical documentation and user manuals and reviews or fixes
  existing ones, catching contradictions, terminology drift, repetition,
  structural gaps, and dubious claims across the whole document. Use when
  asked to create, audit, review, proof, proofread, check, or work through
  technical docs, a user manual, or product documentation.
argument-hint: "[create|audit*|proof|revise] [<file>...]"
---

# doc-smith

Create, audit, proof, and revise technical documentation and user manuals;
Markdown is the assumed format. The mode is `$1` when it is a mode word, else
inferred from the request; when the request does not settle it, default to
audit (it edits nothing). The remaining arguments name the target file(s);
with no target and no clear intent, ask which mode.

- Create — draft a new document or section from scratch.
- Audit — report findings on an existing doc; edit nothing until approved.
- Proof — fix an existing doc in place; flag what has no single right answer.
- Revise — work through the doc with the user, one unit at a time.

Scope a run to the file — or the named set/directory — the user gives, and
treat it as **one document**: consistency is judged across all of it. Flag a
contradiction the pass surfaces in a file outside that scope rather than drop
it.

Structure, prose rules, and the defect taxonomy come from
[`references/writing-guide.md`](references/writing-guide.md) *(eager: read once
per run; every mode judges against all of it)*. Every judgment defers to it.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. A written or edited file is the payload: state
its path and what changed; never paste the document back into chat.

## Whole-document pass (all modes)

Model the document before writing or judging — a line-by-line read misses a
claim that a distant section negates. Build a ledger:

- Entities & claims — each product, component, or feature and what the doc
  asserts about it (what it is, does, runs on, requires).
- Terminology — the term used for each concept and every synonym or variant.
- Structure — the heading outline and the job each section does.
- Audience & intent — who each part is for and whether it teaches, walks
  through a task, or serves as lookup reference.

Judge the ledger, not only the prose, against the guide's defect taxonomy; cite
both locations for every contradiction.

Coherence check — after any edit, re-check it against the ledger before moving
on: one fix can contradict a distant claim, drift the terminology, orphan a
reference, or duplicate a point. Update the ledger with each accepted change.
After a reflow, re-read the changed lines to confirm the wrap is clean — no
orphaned word or broken sentence flow.

## Technical claims: flag, don't fix

Internal consistency you resolve; real-world technical accuracy you flag. A
claim that contradicts the ledger is a consistency finding. A claim that looks
factually wrong about a technology, and that the document does not settle, is
raised as a question stating what you'd expect and why — never silently
rewritten or "corrected" with a fact you cannot ground.

## Create mode

1. Gather context: related docs and, if available, the product or repo. Fix the
   audience, product, and purpose; ask only the gaps you cannot infer (audience,
   scope, key tasks, preferred terminology) in one batched round.

2. Outline a structure that fits the purpose per the guide, with only the
   sections the product needs. Confirm the outline before drafting a long
   document.

3. Draft to the guide.

4. Self-review with the whole-document pass; fix before writing.

5. Write the file(s) and state the path.

## Audit mode

1. Resolve the target; state the exact file(s) in scope.

2. Run the whole-document pass.

3. Audit against the guide's defect taxonomy; flag dubious technical claims as
   questions.

4. Report only. Number the findings (one numbered list, so each can be
   answered separately) and group them Blocker / Should-fix / Nit;
   each names the location, the problem in one line, the guide rule it breaks,
   and a minimal fix; a contradiction cites both locations. End with a verdict
   and per-severity counts.

5. Fix on confirmation: apply approved findings, run the coherence check, and
   state what changed.

## Proof mode

Fix in place. Reserve edits for what has one right answer; flag the rest.

1. Run the whole-document pass.

2. Apply corrections directly: grammar, clarity, terminology consistency,
   repetition, formatting. Fix a contradiction only when the intended meaning is
   unambiguous; otherwise flag it as a question. Flag dubious technical claims.

3. Run the coherence check.

4. State what changed — edit classes and counts — and list every flagged
   contradiction, ambiguity, and technical claim awaiting the user's decision.

## Revise mode

Work through the document with the user, one paragraph (or logical unit) at a
time, in document order.

1. Run the whole-document pass. Confirm the starting unit — the top, or a
   section the user names.

2. For the current unit, name the findings (consistency, clarity, structure,
   dubious claim) and propose a concrete revision. Refine with the user; apply
   only what they agree to. Flag dubious technical claims.

3. Run the coherence check on the rest of the document; report any break with
   its location before advancing.

4. Advance only when the user is done with the unit. Track position so they can
   pause and resume. On request or at the end, run a final whole-document pass.

Per turn, show the proposed revision and the coherence-check result only.

## Self-application

`doc-smith` obeys the repo authoring standard; when you change this skill,
re-audit it with `skill-smith` in improve mode.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/doc-smith.md` when this directory
is read-only. On a correction or self-caught mistake, first draft the lesson
**generically** — a rule for any document, not tied to the one at hand — and
present it for the user's approval. Only once approved, append the one-line rule
to whichever is writable (creating it) and report where. Never append an
unapproved lesson.
