# create

Authors a brand-new **Software Requirement Document (SRD)** that conforms to the
**SRD standard**. The agent interviews you
along the fixed SRD spine, drafts the document, self-checks it against the
standard, and writes it to a Markdown file.

It is an **author** skill: it creates new SRDs. It does not review or audit an
SRD written elsewhere.

## When to Use

- You need a new SRD and want it to meet the house standard the first time.
- You have an idea or a feature in mind but the requirements are not pinned down.
- You want every requirement to be atomic, verifiable, and correctly numbered,
  with a clean glossary and scope.

## How It Works

1. **Resolves the shared glossary** — a single Markdown file or a directory of
   them, remembered per project. It fingerprints the docs and loads a cached term
   digest, regenerating the digest only when the glossary changed, so known terms
   are linked, not redefined.
2. **Interviews you** one branch at a time: objective → UI change → in/out of
   scope → the actual requirements → terms. It pushes back on vague or
   non-atomic requirements.
3. **Proposes requirement groups and prefixes** (e.g. `AUTH`, `DATA`); you
   confirm or rename, then it numbers them.
4. **Drafts** the SRD in the required order with the RFC 2119 / 8174 keyword
   notice. Owners, Initiative, and Designs links are left as marked `TODO`
   placeholders — the skill stays offline.
5. **Self-checks** the draft: auto-fixes mechanical issues (numbering, section
   order, keyword capitalization, 80-column wrap, stray examples) and reports
   what needs your judgment (links, verifiability, scope coverage, Quality Bar).
6. **Writes** the `.md` file to a path you name and lists the outstanding
   follow-ups.

The rule set lives in `references/srd-standard.md` (each rule is a checkable
statement with an id); house extensions (US English, sub-numbering,
defect examples) in `references/authoring-guide.md`; shared operating procedures
(glossary resolution) in `references/srd-procedures.md`; the skeleton in
`assets/srd-template.md`; the glossary fingerprint in
`scripts/glossary-fingerprint.sh`.
The `edit` and `review` skills read these same files — `create` owns
them.

## Usage

```
/create
```

Then describe what the system or feature must do. The agent takes over the
questioning.

## What to Expect

- A new `In Progress` SRD as a single Markdown file at the path you choose.
- Marked placeholders for anything that needs an external system (ticketing
  initiative, approved design, owners) plus a back-link reminder.
- A short report of what still needs a human decision before the SRD can be
  accepted. The skill never marks an SRD `Accepted` — that is a human call.

## Evaluations

### 1. Author from a vague idea

**Request:** `/create` then "We need an SRD for a password reset feature."

**Expected behavior:**
- Resolves the per-project glossary (file or directory) and loads its term digest
  before drafting.
- Interviews one branch at a time (objective, UI change, in/out of scope, the
  rules), refusing to draft straight from the one-line idea.
- Rewrites a vague requirement ("resets must be secure") into a verifiable one
  ("the system MUST require a reset token that expires after 15 minutes") per
  REQ-6, and keeps each requirement atomic (REQ-1).
- Produces the sections in the required order with the keyword notice, Status
  `In Progress`, and TODO placeholders for Owners/Initiative/Designs.

### 2. Reuse the shared glossary

**Request:** During the interview the user uses a term already defined in the
glossary (e.g. "Audit Log") and a brand-new term.

**Expected behavior:**
- Recognizes the known term from the glossary digest and does not add a
  local Glossary entry for it; links or refers to the shared glossary instead
  (GLO-3 / STR-10).
- Adds a local Glossary entry only for the genuinely new term, defining it and
  nothing else — no behavior or rules in the entry (GLO-1).

### 3. Self-check catches violations

**Request:** The draft contains a two-rule requirement, a lowercase "must", an
`In Scope` item with no matching requirement, and an `Example:` line.

**Expected behavior:**
- Auto-fixes the mechanical issues: capitalizes the normative keyword (LANG-4)
  and strips the `Example:` annotation (REQ-7).
- Reports the judgment issues citing rule ids: the non-atomic requirement should
  be split (REQ-1) and the uncovered `In Scope` item needs a requirement
  (SCO-2).
- Does not declare the SRD acceptable or set its Status to `Accepted`.

### 4. No UI change sets Designs to N/A

**Request:** The user says the feature is backend-only, no UI change.

**Expected behavior:**
- Sets the `Designs` metadata field to `N/A` rather than a placeholder link
  (STR-7), and does not ask for a design-tool link.
- Still leaves Owners and Initiative as TODO placeholders.

### 5. House extensions: US English, consistency, sub-numbering

**Request:** The draft contains "the colour MUST standardise…", two requirements
that say the same thing in different words, and a tight cluster of three related
rules under one group.

**Expected behavior:**
- Rewrites British spellings to US English ("color", "standardize").
- During the consistency pass, flags the duplicate/overlapping requirements to
  merge, and any term used inconsistently.
- Uses one-letter sub-numbering (`GR-1a`, `GR-1b`, `GR-1c`) for the tight cluster
  while keeping flat numbers elsewhere.

### 6. Terse output

**Request:** `/create` reaching the write step.

**Expected behavior:**
- No preamble or step narration during drafting and self-check; the report opens
  with the payload.
- After writing, gives a short pointer — the file path, the requirement groups
  and counts, and the outstanding human follow-ups — without re-pasting the
  drafted SRD the user can already see.
