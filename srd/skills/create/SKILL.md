---
name: create
description: >
  Authors a new Software Requirement Document (SRD) to the SRD standard. Use
  when asked to create, write, draft, or start an SRD, a software
  requirements document, or a spec.
argument-hint: "[<what the SRD should specify>]"
license: MIT
---

# create

Author a brand-new SRD by interviewing the user, drafting against the SRD
standard, and self-checking the draft before saving it.

## Boundaries

`create` is the authority for SRD format, style, logic, and rules, and the
author of new SRDs (interview → draft → self-check). It owns the shared files
under `references/`, `assets/`, and `scripts/`; the other SRD skills read them.
It never reviews or audits an SRD written elsewhere (that is `review`), never
edits an existing SRD as a service (that is `edit`), and never marks an SRD
`ACCEPTED`: acceptance is a human decision (STA-3).

## Sources of truth

- [references/doc-corpus.md](references/doc-corpus.md) (eager) — how to reach
  the platform documentation corpus, how its sources rank, and where an
  unconfirmed or undocumented fact goes (`srd:report-doc-gap`, `srd:kb`).
- [references/srd-standard.md](references/srd-standard.md) (on-demand: steps
  3–4) — the SRD rule set (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, Quality
  Bar). Read it before drafting; not needed for the glossary or the interview.
- [references/authoring-guide.md](references/authoring-guide.md) (on-demand:
  steps 2–4) — house extensions (US English, sub-numbering, one term per
  concept, the consistency pass) and Bad→Good defect examples to draft against
  and check for. Its examples never go into the SRD (REQ-7).
- [references/errata.md](references/errata.md) (not read here) — the bulk-fix
  errata class `review` and `edit` apply; kept here because `create` owns the
  shared references.
- [references/srd-procedures.md](references/srd-procedures.md) (on-demand:
  step 0) — shared procedures: glossary resolution, In Scope derivation.
- [assets/srd-template.md](assets/srd-template.md) (on-demand: step 3) — the
  SRD skeleton in the required section order with the keyword notice. Fill it;
  do not restructure it.
- [scripts/glossary-fingerprint.sh](scripts/glossary-fingerprint.sh) (run, not
  read) — hashes the Company Glossary so its term digest is rebuilt only when
  the glossary changes.

## Documentation corpus

When a corpus is reachable, ground every claim about the existing system in it
instead of guessing; absent one, run offline. `create` consults it at two
points: in the interview, when the user states a fact about the existing system
or uses a term no glossary defines, and in the self-check, for every
requirement that asserts existing behavior. A lookup that cannot confirm the
claim goes to `srd:report-doc-gap`; a fact the corpus lacks but the user
confirms goes to `srd:kb`. Both drain at step 0, buffer silently in between,
and run again at step 5, where `srd:kb` writes its confirmed facts and
`srd:report-doc-gap` offers to work the buffered gaps. A platform fact is confirmed
through the branch restatement in step 1, never through a separate prompt.

## Workflow

Copy this checklist and tick it off:

- [ ] 0. Drain the delegate buffers; resolve the Company Glossary and load its
      term digest.
- [ ] 1. Interview the user along the SRD spine.
- [ ] 2. Propose requirement groups and prefixes; get confirmation.
- [ ] 3. Draft the SRD from the template.
- [ ] 4. Self-check: auto-fix mechanical issues, collect judgment ones.
- [ ] 5. Write the `.md` file to a user-named path; run the delegates'
      finish step; report once.

### 0. Start

Invoke `srd:report-doc-gap` and `srd:kb` to drain what a prior session left
buffered for this SRD. Then run the glossary-resolution procedure in
[references/srd-procedures.md](references/srd-procedures.md): resolve the
per-project glossary path (a single Markdown file or a directory of them),
fingerprint it, and load or regenerate its term digest. The digest lets the SRD
satisfy GLO-3 / STR-10 without redefining known terms.

### 1. Interview

When the invocation carries a seed (`$ARGUMENTS`), treat it as the user's
opening Objective and restate it for confirmation instead of asking cold; with
no seed, open with the Objective question.

Drive the conversation; do not wait to be fed content. Ask one branch at a
time, in this order, and restate each resolved branch before moving on, folding
any platform facts that branch surfaced into the restatement in natural prose,
so confirming it confirms both the SRD and the knowledge base:

1. Objective: what this SRD specifies, in one or two sentences.
2. UI change? Yes sets `Designs` to a TODO link placeholder; no sets it to
   `N/A` (STR-5, STR-7).
3. In Scope: a high-level overview of each change it requests (SCO-1). MAY be
   deferred: because In Scope derives from the requirements, the user may leave
   the `--- TODO ---` marker and derive `SC-n` items after the requirements
   settle (derivation procedure in
   [references/srd-procedures.md](references/srd-procedures.md)).
4. Out of Scope: what it deliberately excludes (STR-11). Requirements must not
   contradict these (SCO-3).
5. Requirements: pull out the actual rules. For each, push until it is atomic
   (REQ-1), about what *the system* does (LANG-1, LANG-5), and verifiable with
   concrete criteria: reject vague qualities like "secure" or "fast" and ask
   for the measurable form (REQ-5, REQ-6). When the user states a fact about
   the existing system ("the system already does X", "the API returns Y"),
   `search` the corpus before accepting it; surface any contradiction at once
   in interview voice, never silently accept or fix. Route the other outcomes
   per [Documentation corpus](#documentation-corpus).
6. Terms: as terms surface, check them against the glossary digest and mark
   each as already defined (link to it) or needing a local Glossary entry.
   `search` the corpus before asking the user to define a term: it may already
   define it, or name the same concept differently (a naming conflict to
   surface). A definition the user supplies because no glossary carries it
   goes to `srd:kb`.

Do not collect Owners, Initiative links, or Designs links; those are left as
marked placeholders (the skill fetches no such links). Status is always
`IN PROGRESS` for a new draft.

Interview style: relentless, focused, no bundled questions; push back on
contradictions; surface a decision that blocks another before continuing.

### 2. Group and number

Cluster the requirements into logical groups. Propose an uppercase prefix per
group, three or four letters where one fits (REQ-8, e.g. `AUTH`, `DATA`,
`VIEW`). Show the grouping and prefixes and let the user rename or merge. Then
number each group from 1 in order (REQ-2 `**PFX-1:**`, REQ-3 unique, REQ-4 in
order). Do the same for scope items (`SC-`, `OSC-`). Default to flat numbers;
use one-letter sub-numbering (`**GR-1a:**`, `**GR-1b:**`) only for a tight
cluster of related rules (authoring guide).

### 3. Draft

Fill `assets/srd-template.md` in its section order (STR-13), writing against
the standard and the authoring guide. Decisions specific to a new draft:

- Metadata: a real `Objective`; `Status` `IN PROGRESS`; `Owners`, `Initiative`,
  and (when the UI changes) `Designs` as clearly marked `<TODO: …>`
  placeholders; `Designs` `N/A` otherwise.
- In Scope MAY keep the `--- TODO ---` marker instead of `SC-n` items when
  deferred; derive them from the requirements before acceptance.
- Add a `## TODO` section as the last section only when open authoring issues
  need tracking.
- Local Glossary entries only for terms the Company Glossary digest lacks.

### 4. Self-check

Check the draft against every rule in
[references/srd-standard.md](references/srd-standard.md), in document-section
order (metadata → Introduction → Glossary → Scope → Requirements), recognizing
the defect classes in
[references/authoring-guide.md](references/authoring-guide.md). Loop until the
mechanical checks all pass. This is `create`'s action policy on a finding:

1. Auto-fix the mechanical checks (no judgment): section order (STR-13),
   keyword notice placement (STR-8), identifier format/uniqueness/order
   (REQ-2/3/4), keyword capitalization (LANG-4), stray example or note text
   (REQ-7), valid Markdown, Status defaulting to `IN PROGRESS`, Designs `N/A`
   when the user said no UI change, British → US spelling.
2. Consistency pass: run the pass in
   [references/authoring-guide.md](references/authoring-guide.md), re-reading
   the whole draft top to bottom. Repeat after any fix.
3. Collect the judgment checks for the step-5 report, each with its rule id and
   location: missing/placeholder Owners, Initiative, Designs (STR-2/3/5/7; the
   back-links STR-4/6 are external and not reported); intro gaps (STR-9);
   undefined terms (STR-10/GLO-3); style (LANG-1/2/3/5/6/7); non-atomic or
   unverifiable requirements (REQ-1/5/6); glossary discipline (GLO-1/2); scope
   coverage and conflicts, every In Scope item needing ≥ 1 requirement and none
   contradicting Out of Scope (SCO-2/3); duplicate or overlapping requirements
   and terminology drift (authoring guide); any Quality Bar item not yet met.
   When a corpus is available, also flag any requirement whose claim about
   existing system behavior it could not confirm, a facts gap distinct from the
   format checks, and route it per [Documentation corpus](#documentation-corpus).
   Marked placeholders (Initiative, Designs, Owners, an unresolved In Scope
   `--- TODO ---` marker, any non-empty `## TODO` section) are always
   outstanding human follow-ups.

Do not mark the draft acceptable: a new SRD is `IN PROGRESS` and acceptance
(STA-3, Quality Bar) is a human decision.

### 5. Write

Write the SRD as a single `.md` file to the path the user gives (ask if they
have not said). Invoke `srd:kb` to write the facts the interview confirmed and
`srd:report-doc-gap` to offer the gaps buffered this session. Then report
once: the file path, the requirement groups with their counts, and the judgment
findings and human follow-ups collected in step 4.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/create.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
