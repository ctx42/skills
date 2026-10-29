---
name: create
description: >
  Authors a new Software Requirement Document (SRD) to the SRD standard: the
  requirements, scope, and glossary that define what a feature or initiative
  must do before it is built. Use when asked to create, write, draft, or start
  an SRD or a software requirements document.
argument-hint: "[<what the SRD should specify>]"
license: MIT
---

# create

## Usage

```
/srd:create                           author a new SRD by interview (default)
/srd:create <what it should specify>  seed the opening purpose, then interview
```

Author a brand-new SRD by interviewing the user, drafting against the SRD
standard, and self-checking the draft before saving it.

## Boundaries

`create` is the authority for SRD format, style, logic, and rules, and the
author of new SRDs (interview → draft → self-check). It owns the shared files
under `references/` and `assets/`; the other SRD skills read them.
It never reviews or audits an SRD written elsewhere (that is `review`), never
edits an existing SRD as a service (that is `edit`), and never sets an SRD to
the standard's approval status: approval is a human decision.

## Sources of truth

- [references/project-config.md](references/project-config.md) (eager: before
  anything) — the gate every run passes first, and the project paths, the
  standard, and the server it names.
- [references/doc-corpus.md](references/doc-corpus.md) (on-demand: the first
  corpus lookup, in the interview or the self-check) — how to reach the
  platform documentation corpus, how its sources rank, how a corpus-backed
  question cites its source, and where an unconfirmed or undocumented fact
  goes (`srd:report-doc-gap`, `srd:kb`).
- The SRD standard (on-demand: steps 3–4) — every rule this skill applies:
  the metadata fields, status values, sections and their order, notice,
  identifier format, wording rules, and approval checks. Fetched live through
  the server per [references/project-config.md](references/project-config.md)
  before drafting; not needed for the glossary or the interview. Act only on
  what it states, and cite a rule by the identifier it writes; the rule
  descriptions below name no standard's ids.
- [references/authoring-guide.md](references/authoring-guide.md) (on-demand:
  steps 2–4) — house extensions (US English, sub-numbering, one term per
  concept, the consistency pass) and Bad→Good defect examples to draft against
  and check for. Its examples never go into the SRD.
- [references/errata.md](references/errata.md) (not read here) — the bulk-fix
  errata class `review` and `edit` apply; kept here because `create` owns the
  shared references.
- [references/srd-procedures.md](references/srd-procedures.md) (on-demand: the
  first term the interview surfaces) — shared procedures: shared-glossary
  resolution, in-scope derivation.
- [assets/srd-template.md](assets/srd-template.md) (on-demand: step 3) — how
  to build the SRD skeleton from the standard, and the default keyword notice.
  Build from it; never reorder what the standard orders.

## Documentation corpus

Ground every claim about the existing system in the corpus instead of guessing.
`create` consults it at two points: in the interview, when the user states a
fact about the existing system or uses a term no glossary defines, and in the
self-check, for every requirement that asserts existing behavior. A lookup that
cannot confirm the claim goes to `srd:report-doc-gap` on discovery, confirmed
by the user or not; a fact the corpus lacks but the user confirms goes to
`srd:kb` as well, which writes it to the inbox at once. A user who does not
know an answer: [Who would know](references/doc-corpus.md#who-would-know).
Gaps are captured as server-side drafts on discovery and offered at step 5.
When the first gap surfaces and no SRD path is agreed yet, capture the draft at
once with `srd_ref` empty — never wait for the path — and fold a proposed path
(its own folder under `initiatives`) into that branch's restatement; once it is
confirmed, hand it to `srd:report-doc-gap`, which sets the `srd_ref` of every
draft captured without one — a draft left without a path is invisible to every
later draft check. A platform fact is confirmed through the branch restatement
in step 1, never through a separate prompt, and reaches `srd:kb` only once that
restatement is confirmed — the user's answer inside the branch is not the
confirmation.

Corpus content enters the draft only through the interview: each fact a lookup
supplies, rewords, or confirms is put to the user with its source line ([Citing
a source](references/doc-corpus.md#citing-a-source)) before it can be drafted. A
self-check lookup whose result would add to, reword, or contradict the text goes
back as one more interview question (step 4), never only reported; one that
found nothing leaves an unconfirmed claim (reported). The step-5 report lists
every corpus-sourced statement in the file with its source line.

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
nothing to check. The step-5 report says in one clause what the check found,
because a check that never ran otherwise looks identical to one that found
nothing. The opening turn says nothing of the gate or the check: it is the
first interview question.

Resolve the glossary when the first term surfaces (branch 6 at the latest, and
always before drafting; a seed's term surfaces with the user's first answer),
not here: [references/srd-procedures.md](references/srd-procedures.md). The
term set lets the SRD meet the standard's term-definition rules without
redefining terms the shared glossary defines, so it must be loaded before any
term is checked against it, never after.

### 1. Interview

When the invocation carries a seed, treat it as the user's opening purpose:
restate it and ask the next branch in the same turn, so the answer confirms or
corrects the restatement, instead of asking cold; with no seed, open with the
purpose question.

Drive the conversation; do not wait to be fed content. Ask one branch at a
time, in this order, and restate each resolved branch before moving on, folding
any platform facts that branch surfaced into the restatement in natural prose,
so confirming it confirms both the SRD and the knowledge base:

1. Purpose: what this SRD specifies, in one or two sentences; it fills the
   summary field the standard's metadata requires, if any.
2. UI change? Yes leaves the standard's design-link field a marked TODO
   placeholder; no gives it the value the standard sets for no UI change.
3. In scope: a high-level overview of each change it delivers (the standard's
   in-scope list). MAY be deferred: because it derives from the requirements,
   the user may leave the `--- TODO ---` marker and derive its items after the
   requirements settle (derivation procedure in
   [references/srd-procedures.md](references/srd-procedures.md)).
4. Out of scope: what it deliberately excludes (the standard's out-of-scope
   list). Requirements must not contradict these.
5. Requirements: pull out the actual rules. For each, push until it is atomic,
   about what *the system* does, and verifiable with concrete criteria: reject
   vague qualities like "secure" or "fast" and ask for the measurable form.
   When the user states a fact about
   the existing system ("the system already does X", "the API returns Y"),
   `search` the corpus before accepting it; surface any contradiction at once
   in interview voice, never silently accept or fix — a KB section's included,
   which no `rank` settles: the fact the user confirms goes to `srd:kb`,
   which rewrites the section at once. Route the other outcomes
   per [Documentation corpus](#documentation-corpus).
6. Terms: resolve the glossary now if no term has yet forced it (step 0), then
   check each term that surfaces against its term set and mark it as already
   defined (link to it) or needing a local terms entry.
   `search` the corpus before asking the user to define a term: it may already
   define it, or name the same concept differently (a naming conflict to
   surface). What the corpus returns is meaning, not coverage — only the
   shared glossary satisfies the standard's definition rule, so a term the
   corpus defines and `glossary_terms` lacks still needs a local entry
   ([references/srd-procedures.md](references/srd-procedures.md)). A definition
   the user supplies because no glossary carries it goes to `srd:kb` when it
   names a platform concept — one that exists whether or not this SRD ships;
   one this SRD introduces gets its local entry only.

Do not collect the metadata fields that name people or link outside the SRD
(owners or reviewers, a tracking link, a design link); each stays a marked
placeholder (the skill fetches no such links). The status field always holds
the standard's initial status, the value it gives a document still being
written.

Interview style: relentless, focused, no bundled questions; push back on
contradictions; surface a decision that blocks another before continuing.

### 2. Group and number

Cluster the requirements into logical groups. Propose a group code per group
that the standard's identifier rule allows (e.g. `AUTH`, `DATA`, `VIEW`). Show
the grouping and codes and let the user rename or merge. Then number each group
from 1 in order, unique, in the identifier format the standard sets; number
scope items the same way when the standard gives them identifiers. Default to
flat numbers; use one-letter sub-numbering (`ABC-1a`, `ABC-1b`) only for a
tight cluster of related rules (authoring guide) and only where the standard's
numbering rule allows it.

### 3. Draft

Build the skeleton per `assets/srd-template.md`, in the section order the
standard sets, writing against the standard and the authoring guide. Decisions
specific to a new draft:

- Metadata: every field the standard requires; the summary field from the
  purpose; the status field at its initial status; people fields, the
  tracking link, and (when the UI changes) the design link as clearly marked
  `<TODO: …>` placeholders; the design-link field at the standard's no-UI
  value otherwise.
- The in-scope list MAY keep the `--- TODO ---` marker instead of items when
  deferred; derive them from the requirements before approval.
- Add a `## TODO` section as the last section only when open authoring issues
  need tracking.
- Local terms entries only for terms `glossary_terms` lacks.

### 4. Self-check

Check the draft against every rule in the standard fetched through the server,
in the order the standard says to check, else its section order, recognizing
the defect classes in
[references/authoring-guide.md](references/authoring-guide.md). Loop until the
mechanical checks all pass. This is `create`'s action policy on a finding:

1. Auto-fix the mechanical checks (no judgment): section order, keyword-notice
   text and placement, identifier format/uniqueness/order, keyword
   capitalization, example or note text where the standard forbids it, valid
   Markdown, requirement-group dividers (authoring guide), the status field at
   its initial status, the design-link field at its no-UI value when the user
   said no UI change, British → US spelling. These apply even
   where the user declined a rewording in the interview: a refusal there is
   about meaning, and a keyword's case or a stray example carries none.
2. Consistency pass: run the pass in
   [references/authoring-guide.md](references/authoring-guide.md), re-reading
   the whole draft top to bottom. Repeat after any fix.
3. Collect the judgment checks, each with the identifier of the rule it
   breaks, as the standard writes it, and its location — the blockers among
   them go to step 4, everything else to the step-5 report: missing or
   placeholder people and link fields (back-links the standard requires live
   outside the SRD and are not reported); intro gaps; undefined terms; wording
   style; non-atomic or unverifiable requirements; terms-section discipline
   (definitions only, no behavior); scope coverage and conflicts, every
   in-scope item needing ≥ 1 requirement and none contradicting the
   out-of-scope list; duplicate or overlapping requirements and terminology
   drift (authoring guide); any approval check the standard lists not yet met.
   Also flag any requirement whose claim about existing system behavior went
   unconfirmed — a facts gap distinct from the format checks. It routes per
   [Documentation corpus](#documentation-corpus) and is flagged, never assumed
   true.
   Marked placeholders (people and link fields, an unresolved in-scope
   `--- TODO ---` marker, any non-empty `## TODO` section) are always
   outstanding human follow-ups.
4. Settle the blockers before writing: a non-atomic requirement, an
   unverifiable one, an in-scope item no requirement covers (suspended, and so
   nothing to walk, while the in-scope `--- TODO ---` marker stands). Each
   goes back to the user as one more
   interview question — one at a time, the current text and the proposed fix
   shown, the same discipline as branch 5 — and the answer is drafted in. An
   authoring skill does not knowingly write a defect it has already named; the
   author is still in the room, which is what separates this from an editor
   working a finished document. "Leave it" is a legitimate answer: it goes to
   the step-5 report as an accepted gap, not as something the self-check
   missed, and to no `## TODO` entry. Everything else from step 3 —
   placeholders, style, intro gaps, terminology drift, an unconfirmed platform
   claim (the lookup found nothing) — is reported, never walked.

Do not mark the draft acceptable: a new SRD holds the standard's initial
status, and approval, with the standard's approval checks, is a human
decision.

### 5. Write

Write only once step 4 has settled every blocker. Write the SRD as a single
`.md` file to the path agreed at the first gap, or the one the user gives; when
neither exists, propose one in its own folder under `initiatives` and ask. When
this session captured drafts, invoke `srd:report-doc-gap` to offer them. Then
report once: the file path, the requirement groups with their counts (counts
only — the requirement text is in the file, never quoted back), the judgment
findings and human follow-ups collected in step 4, any blocker the
user chose to leave standing, and the corpus-sourced statements with their
source lines.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

Every count in the report — glossary terms reused, requirements written, TODOs
left, findings the self-check raised — is read off the finished artifact, never
carried from the work that produced it. A run told the user "12 terms" over a
glossary defining 10; nobody re-derives that number, so nobody catches it.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/create.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
