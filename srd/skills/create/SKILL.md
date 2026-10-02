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

## Usage

```
/create                           author a new SRD by interview (default)
/create <what it should specify>  seed the opening Objective, then interview
```

Author a brand-new SRD by interviewing the user, drafting against the SRD
standard, and self-checking the draft before saving it.

## Boundaries

`create` is the authority for SRD format, style, logic, and rules, and the
author of new SRDs (interview → draft → self-check). It owns the shared files
under `references/` and `assets/`; the other SRD skills read them.
It never reviews or audits an SRD written elsewhere (that is `review`), never
edits an existing SRD as a service (that is `edit`), and never marks an SRD
`ACCEPTED`: acceptance is a human decision (STA-3).

## Sources of truth

- [references/project-config.md](references/project-config.md) (eager: before
  anything) — the gate every run passes first, and the project paths, the
  standard, and the server it names.
- [references/doc-corpus.md](references/doc-corpus.md) (on-demand: the first
  claim about the existing system, in the interview or the self-check) — how to
  reach the platform documentation corpus, how its sources rank, and where an
  unconfirmed or undocumented fact goes (`srd:report-doc-gap`, `srd:kb`).
- The SRD standard (on-demand: steps 3–4) — the rule set (`STR`, `STA`,
  `LANG`, `REQ`, `GLO`, `SCO`, Quality Bar), fetched live through the server
  per [references/project-config.md](references/project-config.md). Fetch it
  before drafting; not needed for the glossary or the interview.
- [references/authoring-guide.md](references/authoring-guide.md) (on-demand:
  steps 2–4) — house extensions (US English, sub-numbering, one term per
  concept, the consistency pass) and Bad→Good defect examples to draft against
  and check for. Its examples never go into the SRD (REQ-7).
- [references/errata.md](references/errata.md) (not read here) — the bulk-fix
  errata class `review` and `edit` apply; kept here because `create` owns the
  shared references.
- [references/srd-procedures.md](references/srd-procedures.md) (on-demand: the
  first term the interview surfaces) — shared procedures: glossary resolution,
  In Scope derivation.
- [assets/srd-template.md](assets/srd-template.md) (on-demand: step 3) — the
  SRD skeleton in the required section order with the keyword notice. Fill it;
  do not restructure it.

## Documentation corpus

Ground every claim about the existing system in the corpus instead of guessing.
`create` consults it at two points: in the interview, when the user states a
fact about the existing system or uses a term no glossary defines, and in the
self-check, for every requirement that asserts existing behavior. A lookup that
cannot confirm the claim goes to `srd:report-doc-gap`; a fact the corpus lacks
but the user confirms goes to `srd:kb`, which writes it to the inbox at once.
Gaps are captured as server-side drafts on discovery and offered at step 5.
When the first gap surfaces and no SRD path is agreed yet, fold a proposed path
(its own folder under `initiatives`) into that branch's restatement; once it is
confirmed, hand it to `srd:report-doc-gap`, which sets the draft's `srd_ref` —
a draft left without a path is invisible to every later draft check. A
platform fact is confirmed through the branch restatement in step 1, never
through a separate prompt, and reaches `srd:kb` only once that restatement is
confirmed — the user's answer inside the branch is not the confirmation.

## Workflow

Copy this checklist and tick it off:

- [ ] 0. Pass the gate; check for draft gaps only when an SRD path is named.
- [ ] 1. Interview the user along the SRD spine.
- [ ] 2. Propose requirement groups and prefixes; get confirmation.
- [ ] 3. Draft the SRD from the template.
- [ ] 4. Self-check: auto-fix mechanical issues, settle the blockers with the
      user, report the rest.
- [ ] 5. Write the `.md` file to the agreed path; offer the session's drafts;
      report once.

### 0. Start

Start cheap: the interview is what the user came for. Run the gate in
[references/project-config.md](references/project-config.md). When the user
named the SRD's path, run the draft check in
[references/doc-corpus.md](references/doc-corpus.md); with no path yet there is
nothing to check. The report says in one clause what the check found, because a
check that never ran otherwise looks identical to one that found nothing.

Resolve the glossary when the first term surfaces (branch 6 at the latest, and
always before drafting; a seed's term surfaces with the user's first answer),
not here: [references/srd-procedures.md](references/srd-procedures.md). The
term set lets the SRD satisfy GLO-3 / STR-10 without redefining known terms, so
it must be loaded before any term is checked against it, never after.

### 1. Interview

When the invocation carries a seed, treat it as the user's opening Objective:
restate it and ask the next branch in the same turn, so the answer confirms or
corrects the restatement, instead of asking cold; with no seed, open with the
Objective question.

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
6. Terms: resolve the glossary now if no term has yet forced it (step 0), then
   check each term that surfaces against its term set and mark it as already
   defined (link to it) or needing a local Glossary entry.
   `search` the corpus before asking the user to define a term: it may already
   define it, or name the same concept differently (a naming conflict to
   surface). What the corpus returns is meaning, not coverage — only the
   Company Glossary satisfies GLO-3, so a term the corpus defines and
   `glossary_terms` lacks still needs a local entry
   ([references/srd-procedures.md](references/srd-procedures.md)). A definition
   the user supplies because no glossary carries it goes to `srd:kb` when it
   names a platform concept; one specific to this SRD gets its local entry only.

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
- Local Glossary entries only for terms `glossary_terms` lacks.

### 4. Self-check

Check the draft against every rule in the standard fetched through the server,
in document-section order (metadata → Introduction → Glossary → Scope →
Requirements), recognizing the defect classes in
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
3. Collect the judgment checks, each with its rule id and location — the
   Quality-Bar blockers among them go to step 4, everything else to the step-5
   report: missing/placeholder Owners, Initiative, Designs (STR-2/3/5/7; the
   back-links STR-4/6 are external and not reported); intro gaps (STR-9);
   undefined terms (STR-10/GLO-3); style (LANG-1/2/3/5/6/7); non-atomic or
   unverifiable requirements (REQ-1/5/6); glossary discipline (GLO-1/2); scope
   coverage and conflicts, every In Scope item needing ≥ 1 requirement and none
   contradicting Out of Scope (SCO-2/3); duplicate or overlapping requirements
   and terminology drift (authoring guide); any Quality Bar item not yet met.
   Also flag any requirement whose claim about existing system behavior went
   unconfirmed — a facts gap distinct from the format checks. It routes per
   [Documentation corpus](#documentation-corpus) and is flagged, never assumed
   true.
   Marked placeholders (Initiative, Designs, Owners, an unresolved In Scope
   `--- TODO ---` marker, any non-empty `## TODO` section) are always
   outstanding human follow-ups.
4. Settle the Quality-Bar blockers before writing: a non-atomic requirement
   (REQ-1), an unverifiable one (REQ-5/6), an In Scope item no requirement
   covers (SCO-2 — suspended, and so nothing to walk, while the In Scope
   `--- TODO ---` marker stands). Each goes back to the user as one more
   interview question — one at a time, the current text and the proposed fix
   shown, the same discipline as branch 5 — and the answer is drafted in. An
   authoring skill does not knowingly write a defect it has already named; the
   author is still in the room, which is what separates this from an editor
   working a finished document. "Leave it" is a legitimate answer: it goes to
   the step-5 report as an accepted gap, not as something the self-check
   missed, and to no `## TODO` entry. Everything else from step 3 —
   placeholders, style, intro gaps, terminology drift, an unconfirmed platform
   claim — is reported, never walked.

Do not mark the draft acceptable: a new SRD is `IN PROGRESS` and acceptance
(STA-3, Quality Bar) is a human decision.

### 5. Write

Write the SRD as a single `.md` file to the path agreed at the first gap, or the
one the user gives; when neither exists, propose one in its own folder under
`initiatives` and ask. When this session captured drafts, invoke
`srd:report-doc-gap` to offer them. Then report once: the file path, the
requirement groups with their counts, the judgment findings and human follow-ups
collected in step 4, and any blocker the user chose to leave standing.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

Every count in the report — glossary terms reused, requirements written, TODOs
left, findings the self-check raised — is read off the finished artifact, never
carried from the work that produced it. A run told the user "12 terms" over a
glossary defining 10; nobody re-derives that number, so nobody catches it.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/create.md`, the
sibling winning a conflict — a read-only install writes the second, and what it
learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.