# doc-smith

Write, audit, proof, and revise technical documentation and user manuals. One
skill, four modes, chosen from how you ask:

- Create — draft a new document or section. It fixes the audience and purpose,
  asks only the gaps it can't infer, and drafts to a distilled technical-writing
  standard.
- Audit — name an existing doc and it models the whole document, then reports
  findings by severity, editing nothing until you approve.
- Proof — fixes an existing doc in place (grammar, clarity, consistency),
  flagging what it can't safely decide.
- Revise — works through the doc with you one paragraph at a time, and after each
  change re-checks that it still fits the rest of the document.

Its edge is reading the **whole document as one model** before judging: it builds
a ledger of entities, claims, and terminology, so it catches a contradiction
between distant sections — "X is a web platform" early, "X runs in a web browser"
later — that line-by-line proofreading misses. Internal consistency it fixes;
real-world technical accuracy it flags as a question rather than guessing.

The rules it lives by come from
[references/writing-guide.md](references/writing-guide.md): audience and purpose,
content shapes, user-manual structure, prose and procedure rules, and the defect
taxonomy audit reports against.

## Usage

```
/doc-smith create a user manual for the admin console   # create mode
/doc-smith audit docs/manual.md                         # report findings
/doc-smith proof docs/guide.md                          # fix in place
/doc-smith work through docs/guide.md with me           # revise, paragraph by paragraph
/doc-smith check these three files as one manual        # named set
```

You don't need a mode keyword — it infers create vs audit vs proof vs revise
from the request ("proofread" works too). Point it at a file or a named set
and it treats them as one document.

## Evaluations

### 1. Catch a cross-document contradiction

**Request:** `/doc-smith audit docs/manual.md` — the doc says "Acme is a hosted
web platform" in the intro and "Acme runs entirely in your web browser" three
sections later, and repeats the browser claim twice more.

**Expected behavior:**
- Models the whole document before judging; does not report only local typos.
- Reports the contradiction as a Blocker, citing **both** locations, not one.
- Flags the repeated browser claim as redundant.
- Groups findings Blocker / Should-fix / Nit and edits nothing before approval.

### 2. Flag a dubious technical claim instead of rewriting it

**Request:** `/doc-smith proof docs/api-guide.md` — clean prose except one
line claiming "REST APIs are stateful by design."

**Expected behavior:**
- Fixes grammar, terminology, and clarity directly in the file.
- Does **not** silently rewrite the dubious claim; raises it as a question
  stating what it would expect and why.
- Lists the flagged claim among items awaiting the user's decision.
- Invents no replacement fact it cannot ground.

### 3. Terse output

**Request:** `/doc-smith audit docs/manual.md`, then apply the fixes.

**Expected behavior:**
- The report opens with the findings — no "I'll now review…" preamble, no
  step narration.
- Each finding is stated once; no closing summary re-lists findings already
  shown.
- After applying fixes, states the edit classes and the file path; does not paste
  the whole document back into chat.

### 4. Create a user manual, grounded, asking only gaps

**Request:** `/doc-smith create a user manual for the billing dashboard`

**Expected behavior:**
- Fixes the audience, product, and purpose; asks only the gaps it can't infer
  (audience, key tasks, terminology) in one batched round.
- Uses one term per concept from the first line and a task-oriented structure
  (overview → prerequisites → tasks → reference → troubleshooting), omitting
  empty sections.
- Self-reviews with the whole-document pass before writing.
- Writes the file, states the path, and does not paste the manual back.

### 5. Terminology drift and a dangling reference across a set

**Request:** `/doc-smith audit docs/install.md docs/config.md docs/usage.md as
one manual`

**Expected behavior:**
- Treats the three files as one document and checks consistency across all of
  them.
- Flags a concept named "workspace" in one file and "project" in another as
  terminology drift.
- Flags a reference to a "Backup" section that no file contains as a completeness
  gap.

### 6. Revise paragraph by paragraph, keeping the whole coherent

**Request:** `/doc-smith work through docs/guide.md with me` — while revising an
early paragraph, the user renames "workspace" to "project".

**Expected behavior:**
- Moves in document order, one paragraph at a time; proposes a revision, applies
  only what the user agrees to, and does not batch-edit the whole file.
- After applying the rename, re-checks the rest of the document and flags the
  later paragraphs still saying "workspace" as now-inconsistent — before moving
  on.
- Reports each turn tersely: the proposed change and the coherence-check result,
  not a reprint of the whole document.

### 7. Normalize spelling and formatting to convention

**Request:** `/doc-smith proof docs/guide.md` — the doc mixes "colour" and
"color", and has a misaligned Markdown table.

**Expected behavior:**
- Normalizes to one spelling variety (US by default); if the doc is consistently
  British, keeps British and flags the mix rather than converting wholesale.
- Aligns the table columns and reflows to the doc's own established wrap width,
  not an imposed house default.
- Reports the variety mix as a spelling-variety defect.
- States edit classes and counts; does not paste the whole document back.

## Relationship to other skills

- `readme-smith` — owns project front-page READMEs; `doc-smith` owns broader
  technical docs and user manuals.
- `grill-me` — use it first when a new document's scope is fuzzy; create mode
  asks gaps but doesn't run a full planning interview.
- `skill-smith` — authors this skill and audits it against the repo standard.
