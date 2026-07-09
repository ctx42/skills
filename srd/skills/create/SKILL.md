---
name: create
description: >
  Authors a new Software Requirement Document (SRD) by interviewing the user,
  then drafts it to the SRD standard and self-checks the draft. Use when
  asked to create, write, draft, or start an SRD or a software requirements
  document or spec. Walks the fixed SRD structure one branch at a time, proposes
  requirement groups, reuses the shared glossary, and validates the result
  against the standard's rules before writing the file.
license: MIT
---

# create

Author a brand-new SRD by interviewing the user, drafting against the SRD
standard, and self-checking the draft before saving it. This skill does not
review or audit SRDs written elsewhere.

## Self-learning

Read this skill's lessons first and obey them: the sibling `LESSONS.md`, plus —
when this skill's directory is not writable (an installed copy) —
`$HOME/.agent-data/ctx42-skills/lessons/srd/create.md`. When the user corrects
you, or you catch your own mistake, append the fix as a one-line rule to
whichever is writable (the sibling in a source checkout, else the `.agent-data`
file, creating it), then report where — so it never recurs.

## Boundaries

- **Role:** the authority for SRD format, style, logic, and rules, and the
  author of new SRDs (interview → draft → self-check). The shared reference
  files under `references/`, `assets/`, and `scripts/` are owned here; the other
  SRD skills read them.
- **Must not:** review or audit an SRD written elsewhere (that is `review`);
  edit an existing SRD as a service (that is `edit`); mark an SRD `Accepted`
  — acceptance is a human decision (STA-3).

## Sources of truth

- [references/srd-standard.md](references/srd-standard.md) — the SRD rule set
  (`STR`, `STA`, `LANG`, `REQ`, `GLO`, `SCO`, `MD`, Quality Bar). Both the
  drafting and the self-check defer to it. Read it before drafting.
- [references/authoring-guide.md](references/authoring-guide.md) — house
  extensions to the standard's rules (US English, sub-numbering, terminology
  consistency, the consistency pass) and Bad→Good defect examples to draft
  against and check for. Its examples never go into the SRD (REQ-7).
- [references/srd-checklist.md](references/srd-checklist.md) — the action-neutral
  verification checklist, every check tied to a rule id. The self-check runs it.
- [references/srd-procedures.md](references/srd-procedures.md) — shared operating
  procedures (glossary resolution).
- [assets/srd-template.md](assets/srd-template.md) — the SRD skeleton, in the
  required section order with the keyword notice. Fill it; do not restructure it.
- [scripts/glossary-terms.sh](scripts/glossary-terms.sh) — lists terms already
  defined in the shared glossary, so they are linked, not redefined.

Two hard constraints, every run: the SRD MUST contain **no** `Example`/`Don't`/
`Do` annotations (REQ-7), and a normative keyword (MUST, SHALL, …) MUST appear
**only** inside `Requirements`, in all-capitals (LANG-3, LANG-4).

## Workflow

Copy this checklist and tick it off:

- [ ] 0. Resolve the shared glossary path (file or directory) and load its terms.
- [ ] 1. Interview the user along the SRD spine.
- [ ] 2. Propose requirement groups and prefixes; get confirmation.
- [ ] 3. Draft the SRD from the template.
- [ ] 4. Self-check: auto-fix mechanical issues, report judgment ones.
- [ ] 5. Write the `.md` file to a user-named path.

### 0. Resolve the glossary

Run the glossary-resolution procedure in
[references/srd-procedures.md](references/srd-procedures.md): confirm the glossary
path — a single Markdown file or a directory of them — load its terms with the
extractor, and save the path to memory. The loaded term set lets the SRD satisfy
GLO-3 / STR-10 without redefining known terms.

### 1. Interview

Drive the conversation; do not wait to be fed content. Ask **one branch at a
time**, in this order, and restate each resolved branch before moving on:

1. **Objective** — what this SRD specifies, in one or two sentences.
2. **UI change?** — yes sets `Designs` to a TODO link placeholder; no sets it to
   `N/A` (STR-5, STR-7).
3. **In Scope** — the atomic, verifiable things it delivers (SCO-1).
4. **Out of Scope** — what it deliberately excludes (STR-11). Requirements must
   not contradict these (SCO-3).
5. **Requirements** — pull out the actual rules. For each, push until it is:
   atomic (REQ-1), about what *the system* does (LANG-1, LANG-5), and verifiable
   with concrete criteria — reject vague qualities like "secure" or "fast" and
   ask for the measurable form (REQ-5, REQ-6).
6. **Terms** — as terms surface, check them against the loaded glossary set. Mark
   each as already-defined (link to it) or needs a local Glossary entry.

Do not collect Owners, Initiative links, or Designs links — those are left as
marked placeholders (this skill stays offline). Status is always `In Progress`
for a new draft.

Interview style: relentless, focused, no bundled questions; push back on
contradictions; surface a decision that blocks another before continuing.

### 2. Group and number

Cluster the requirements into logical groups. Propose an uppercase prefix per
group, three or four letters where one fits (REQ-8, e.g. `AUTH`, `DATA`,
`VIEW`). Show the grouping and prefixes and let the
user rename or merge. Then number each group from 1 in order (REQ-2 `**PFX-1:**`,
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
- Requirements: one rule each, `the system` as subject, normative keywords in
  all-capitals, no examples or notes.
- Write in US English (`color`, `behavior`, `standardize`) and use one term per
  concept throughout (see the authoring guide).
- Keep lines ≤ 80 columns (MD-2); valid Markdown (MD-1).

### 4. Self-check

Run every check in [references/srd-checklist.md](references/srd-checklist.md)
against the draft, recognizing the defect classes in
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
   guide); and any Quality Bar item not yet met. Items left as marked
   placeholders (Initiative, Designs, Owners, back-links) are always reported as
   outstanding human follow-ups.

Do not mark the draft acceptable: a new SRD is `In Progress` and acceptance
(STA-3, Quality Bar) is a human decision.

### 5. Write

Write the SRD as a single `.md` file to the path the user gives (ask if they have
not said). Then summarize: the file path, the requirement groups and counts, and
the outstanding human follow-ups from step 4 (placeholders to fill, back-links to
create, anything reported).

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.
