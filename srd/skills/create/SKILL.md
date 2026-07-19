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

- **Role:** the authority for SRD format, style, logic, and rules, and the
  author of new SRDs (interview → draft → self-check). The shared reference
  files under `references/`, `assets/`, and `scripts/` are owned here; the other
  SRD skills read them.
- **Must not:** review or audit an SRD written elsewhere (that is `review`);
  edit an existing SRD as a service (that is `edit`); mark an SRD `Accepted`
  — acceptance is a human decision (STA-3).

## Sources of truth

- [references/srd-standard.md](references/srd-standard.md) (on-demand:
  steps 3–4) — the SRD rule set (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`,
  `MD`, Quality Bar). Both the drafting and the self-check defer to it; read it
  before drafting. Not needed during glossary resolution or the interview.
- [references/authoring-guide.md](references/authoring-guide.md) (on-demand:
  steps 2–4) — house extensions to the standard's rules (US English,
  sub-numbering, terminology consistency, the consistency pass) and Bad→Good
  defect examples to draft against and check for. Its examples never go into
  the SRD (REQ-7). Not needed during the interview.
- [references/srd-procedures.md](references/srd-procedures.md) (on-demand:
  step 0) — shared operating procedures (glossary resolution).
- [assets/srd-template.md](assets/srd-template.md) (on-demand: step 3) — the
  SRD skeleton, in the required section order with the keyword notice. Fill
  it; do not restructure it.
- [scripts/glossary-fingerprint.sh](scripts/glossary-fingerprint.sh) (run, not
  read) — hashes the shared glossary so its term digest is rebuilt only when
  the glossary changes.

## Documentation corpus (when available)

Some setups expose the platform's live documentation over the `srd-doc` MCP
server — tools `mcp__srd-doc__search` (query + optional `k`),
`mcp__srd-doc__get_doc` (document id), and `mcp__srd-doc__list_docs` (no args).
When present, use them to ground factual claims against the real docs instead
of guessing; when absent the skill runs fully offline as before. Degrade in
this order, falling through only when a step genuinely is not there — not on
one failed call:

1. The `srd-doc` MCP corpus tools above (preferred).
2. The `srd-doc` server's REST mirror via curl, when it runs but MCP is not
   wired into this client:
   `curl 'http://<host>:7777/search?q=TEXT&k=5'`,
   `curl 'http://<host>:7777/docs/<id>'` — same engine, same results.
3. Targeted Grep/Read over a local corpus checkout, scoped to the relevant
   subdirectory — a stopgap, never a blind whole-corpus read.

Default to `search` with `k` about 5; reach for `get_doc` only when a hit needs
its full table or context; use `list_docs` to orient first.

### Reporting a doc gap

When a corpus lookup **cannot confirm a claim** — content missing, wrong,
incomplete, or ambiguous — hand the gap to `srd:report-doc-gap`. That skill owns
capture, the grill, and the confirmed `report_gap` filing; this skill only spots
the gap and delegates. Invoke it the moment a gap surfaces — it buffers the gap
without interrupting the interview — and again at session start, where it drains
any gaps a prior session left unfiled. Report only *documentation* gaps here;
SRD-document defects stay in this skill's own findings.

## Workflow

Copy this checklist and tick it off:

- [ ] 0. Resolve the shared glossary and load its term digest.
- [ ] 1. Interview the user along the SRD spine.
- [ ] 2. Propose requirement groups and prefixes; get confirmation.
- [ ] 3. Draft the SRD from the template.
- [ ] 4. Self-check: auto-fix mechanical issues, report judgment ones.
- [ ] 5. Write the `.md` file to a user-named path.

### 0. Resolve the glossary

Run the glossary-resolution procedure in
[references/srd-procedures.md](references/srd-procedures.md): resolve the
per-project glossary path — a single Markdown file or a directory of them —
fingerprint it, and load or regenerate its term digest. The digest lets the SRD
satisfy GLO-3 / STR-10 without redefining known terms.

### 1. Interview

When the invocation carries a seed (`$ARGUMENTS`), treat it as the user's
opening Objective and restate it for confirmation instead of asking cold; with
no seed, open with the Objective question.

Drive the conversation; do not wait to be fed content. Ask **one branch at a
time**, in this order, and restate each resolved branch before moving on:

1. **Objective** — what this SRD specifies, in one or two sentences.
2. **UI change?** — yes sets `Designs` to a TODO link placeholder; no sets it to
   `N/A` (STR-5, STR-7).
3. **In Scope** — the atomic, verifiable things it delivers (SCO-1). MAY be
   deferred: because In Scope derives from the requirements, the user may leave
   the `--- TODO ---` marker and derive `SC-n` items after the requirements
   settle (derivation procedure in
   [references/srd-procedures.md](references/srd-procedures.md)).
4. **Out of Scope** — what it deliberately excludes (STR-11). Requirements must
   not contradict these (SCO-3).
5. **Requirements** — pull out the actual rules. For each, push until it is:
   atomic (REQ-1), about what *the system* does (LANG-1, LANG-5), and verifiable
   with concrete criteria — reject vague qualities like "secure" or "fast" and
   ask for the measurable form (REQ-5, REQ-6). When the user states a fact about
   the existing system ("the system already does X", "the API returns Y") and a
   corpus is available, verify it with `search` before accepting — surface any
   contradiction immediately in interview voice, never silently accept or fix.
   When the corpus cannot confirm the claim (missing, wrong, incomplete, or
   ambiguous docs), hand it to `srd:report-doc-gap` (see
   [Reporting a doc gap](#reporting-a-doc-gap)).
6. **Terms** — as terms surface, check them against the glossary digest. Mark
   each as already-defined (link to it) or needs a local Glossary entry. When a
   corpus is available, `search` it before asking the user to define a term — it
   may already define it, or name the same concept differently (a naming
   conflict to surface).

Do not collect Owners, Initiative links, or Designs links — those are left as
marked placeholders (the skill fetches no such links). Status is always
`In Progress` for a new draft.

Interview style: relentless, focused, no bundled questions; push back on
contradictions; surface a decision that blocks another before continuing.

### 2. Group and number

Cluster the requirements into logical groups. Propose an uppercase prefix per
group, three or four letters where one fits (REQ-8, e.g. `AUTH`, `DATA`,
`VIEW`). Show the grouping and prefixes and let the user rename or merge. Then
number each group from 1 in order (REQ-2 `**PFX-1:**`,
REQ-3 unique, REQ-4 in order). Do the same for scope items (`SC-`, `OSC-`).
Default to flat numbers; use one-letter sub-numbering (`**GR-1a:**`,
`**GR-1b:**`) only for a tight cluster of related rules — see the authoring
guide.

### 3. Draft

Fill `assets/srd-template.md`. Keep the required order (STR-13): metadata →
keyword notice → Introduction → Glossary → Scope → Requirements. Specifics:

- Metadata: real `Objective` and `Status: In Progress`; `Owners`, `Initiative`,
  and (when UI changes) `Designs` as clearly-marked `<TODO: …>` placeholders.
- Introduction states the purpose and, at a high level, what the system will and
  will not do (STR-9). No normative keywords here.
- Glossary defines only terms not in the shared glossary; each entry defines the
  term and nothing else (GLO-1).
- Scope: In Scope MAY hold the `--- TODO ---` marker instead of `SC-n` items when
  deferred (derive them from the requirements before acceptance). Add a `## TODO`
  section as the last section only when there are open authoring issues to track.
- Requirements: one rule each, `the system` as subject, normative keywords in
  all-capitals, no examples or notes.
- Write in US English (`color`, `behavior`, `standardize`) and use one term per
  concept throughout (see the authoring guide).
- Keep lines ≤ 80 columns (MD-2); valid Markdown (MD-1).

### 4. Self-check

Check the draft against every rule in
[references/srd-standard.md](references/srd-standard.md), in document-section
order (metadata → Introduction → Glossary → Scope → Requirements), recognizing
the defect classes in
[references/authoring-guide.md](references/authoring-guide.md). Loop until the
mechanical checks all pass. This is `create`'s action policy on a finding:

1. **Auto-fix** the mechanical checks (no judgment): section order (STR-13),
   keyword notice placement (STR-8), identifier format/uniqueness/order
   (REQ-2/3/4), keyword capitalization (LANG-4), stray example or note text
   (REQ-7), 80-column wrap (MD-2), valid Markdown (MD-1), Status defaulting to
   `In Progress`, Designs `N/A` when the user said no UI change, British → US
   spelling.
2. **Consistency pass** — run the consistency pass in
   [references/authoring-guide.md](references/authoring-guide.md), re-reading the
   whole draft top to bottom. Repeat after any fix.
3. **Report** the judgment checks as a short list, each citing its rule id and
   location: missing/placeholder Owners, Initiative, Designs and any back-link
   (STR-2..6); intro gaps (STR-9); undefined terms (STR-10/GLO-3); style
   (LANG-1/2/3/5/6/7); non-atomic or unverifiable requirements (REQ-1/5/6);
   glossary discipline (GLO-1/2); scope coverage and conflicts — every In Scope
   item needs ≥ 1 requirement and none may contradict Out of Scope (SCO-2/3);
   duplicate or overlapping requirements and terminology drift (authoring
   guide); and any Quality Bar item not yet met. When a corpus is available,
   also flag any requirement whose claim about existing system behavior could
   not be verified against it — a *facts* gap, distinct from the format checks
   above. For each such facts gap, hand it to `srd:report-doc-gap` (see
   [Reporting a doc gap](#reporting-a-doc-gap)). Items
   left as marked placeholders (Initiative, Designs, Owners, back-links, an
   unresolved In Scope `--- TODO ---` marker, and any non-empty `## TODO`
   section) are always reported as outstanding human follow-ups.

Do not mark the draft acceptable: a new SRD is `In Progress` and acceptance
(STA-3, Quality Bar) is a human decision.

### 5. Write

Write the SRD as a single `.md` file to the path the user gives (ask if they have
not said). Then summarize: the file path, the requirement groups and counts, and
the outstanding human follow-ups from step 4 (placeholders to fill, back-links to
create, anything reported).

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/create.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
