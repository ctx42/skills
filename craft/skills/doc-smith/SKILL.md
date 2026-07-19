---
name: doc-smith
description: >
  Writes, audits, proofs, and collaboratively revises technical documentation
  and user manuals, catching contradictions, terminology drift, repetition,
  structural gaps, and dubious technical claims across a whole document. Use
  when asked to create, audit, review, proof, proofread, check, or work through
  technical docs, a user manual, or product documentation.
argument-hint: "[create|audit|proof|revise] [<file>...]"
---

# doc-smith

Write, audit, and proof technical documentation and user manuals. Markdown
is the assumed format. Pick the mode from `$ARGUMENTS` when given (a mode word
and any target file(s)), else from the request:

- Create — draft a new document or section from scratch.
- Audit — review an existing doc; report findings, edit nothing until approved.
- Proof — fix an existing doc in place (grammar, clarity, consistency).
- Revise — work through the doc with the user, one paragraph at a time.

If ambiguous, ask one question: create, audit, proof, or revise?

Scope a run to the file — or the named set/directory — the user gives, and
treat it as **one document**: consistency is judged across all of it. If the
cross-document pass surfaces a contradiction in a file outside that scope, flag
it rather than drop it as out of scope.

Structure, prose rules, and the defect taxonomy come from
[`references/writing-guide.md`](references/writing-guide.md) *(eager: read once
per run)*. Every judgment defers to it.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. In create and proof the document is the
payload — write it in full; do not also paste it back into chat.

## Model the whole document first (all modes)

Before writing or judging, model the document as a whole — reading top to bottom
once catches typos but misses a claim on page 1 that a claim on page 8 negates.
Build a ledger:

- Entities & claims — each product, component, or feature and what the doc
  asserts about it (what it is, what it does, how it runs, what it requires).
- Terminology — the term used for each concept; note every synonym or variant.
- Structure — the heading outline and the job each section does.
- Audience & intent — who each part is written for and whether it teaches, walks
  through a task, or serves as lookup reference.

Then judge the ledger, not only the prose, against the writing guide's defect
taxonomy — the defects that only cross-distance modeling catches (contradiction,
terminology drift, repetition, gaps) hide between sections, not in any one line.
Cite both locations for every contradiction.

This cross-document pass is the core of audit and proof, and the self-review
of create.

After any edit, re-check it against the ledger before moving on: a change that
fixes one paragraph can contradict a distant claim, drift the terminology, or
orphan a reference elsewhere. Update the ledger with each accepted change. After
a reflow or line-length edit, re-read the changed lines to confirm the wrap is
clean — no orphaned word or broken sentence flow — before reporting the fix.

## Technical claims: flag, don't fix

Internal consistency you resolve; real-world technical accuracy you flag. When a
claim contradicts the ledger, fix or report it as a consistency issue. When a
claim looks factually wrong about a technology and the document itself does not
settle it, raise it as a question stating what you'd expect and why — never
silently rewrite it or assert a correction you cannot ground. Uncertain
authorship beats confident fabrication.

## Create mode

1. Gather context. Read related existing docs and, if available, the product or
   repo. Fix the audience, the product, and the document's purpose. Ask only the
   gaps you cannot infer — audience, scope, key tasks, preferred terminology — in
   one batched round.

2. Outline first. Choose a structure that fits the purpose per the writing guide
   (a user manual typically: overview → prerequisites → task procedures →
   reference → troubleshooting), including only sections the product needs.
   Confirm the outline before drafting a long document.

3. Draft to the guide. One term per concept from the first line, task-oriented
   steps, plain prose.

4. Self-review with the whole-document pass and the writing-guide checks; fix
   before writing.

5. Write the file(s). State the path; do not paste the document back.

## Audit mode

1. Resolve the target. State the exact file(s) in scope.

2. Model the whole document (ledger above).

3. Audit against the writing guide across: consistency (contradiction,
   terminology drift, repetition), structure (order, missing or empty sections,
   fit to purpose), completeness (a reader can finish the task; no dangling
   references), clarity and prose, and technical claims (flag dubious ones as
   questions).

4. Report only. Group findings Blocker / Should-fix / Nit. Each names the
   location, the problem in one line, the rule from the guide it breaks, and a
   minimal fix; a contradiction cites both locations. End with a verdict and
   per-severity counts.

5. Fix on confirmation. Apply approved findings; state what changed; do not paste
   the whole document back.

## Proof mode

Fix in place. Reserve edits for what has one right answer; flag the rest.

1. Model the whole document (ledger above).

2. Apply corrections directly: grammar, clarity, terminology consistency,
   repetition, formatting. Fix a contradiction only when the intended meaning is
   unambiguous; when it is genuinely unclear which side is right, flag it as a
   question rather than guess.

3. Flag, don't fix, dubious technical claims (see above).

4. State what changed — edit classes and counts — and list every flagged
   contradiction, ambiguity, and technical claim awaiting your decision. Do not
   paste the whole document back.

## Revise mode

Work through the document with the user, one paragraph (or logical unit) at a
time, in document order. Collaborative, not batch: propose, discuss, apply, then
prove the change still fits.

1. Model the whole document (ledger above). Confirm the starting unit — the top,
   or a section the user names.

2. For the current unit: name the issues you see (consistency, clarity,
   structure, dubious claim) and propose a concrete revision. Discuss and refine
   with the user; apply only what they agree to. Flag, don't fix, dubious
   technical claims.

3. Re-check coherence after applying (see above): scan the rest of the document
   for anything the edit just broke — a now-contradicted claim, terminology it
   diverged from, a reference it orphaned, a point it now duplicates. Report any
   break with its location before advancing; update the ledger.

4. Advance only when the user is done with the unit. Track position so they can
   pause and resume. On request or at the end, run a final whole-document
   coherence pass.

Per turn, show the proposed revision and the coherence-check result; do not
reprint the whole document.

## Self-application

`doc-smith` obeys the repo authoring standard (Claude-native frontmatter, a
README with ≥ 3 evals, references one level deep). When you change this skill,
re-audit it with `skill-smith` in improve mode.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/doc-smith.md` when this directory
is read-only. On a correction or self-caught mistake, first draft the lesson
**generically** — a rule for any document, not tied to the one at hand — and
present it for the user's approval. Only once approved, append the one-line rule
to whichever is writable (creating it) and report where. Never append an
unapproved lesson.
