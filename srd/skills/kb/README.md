# kb

Owner of the knowledge base: Markdown pages stating what the platform *is*,
written from what you attest during SRD work and served back to every agent
through the `srd-doc` corpus.

## Usage

```
/kb                               capture (default): drain, confirm, write
/kb capture SRD-42                capture for one SRD, by id or path
/kb restructure                   reorganize pages and repair every reference
```

You will rarely type any of these. `srd:create` and `srd:edit` invoke this skill
themselves — at the start of a session to drain anything left unwritten,
whenever an interview surfaces a fact the documentation does not carry, and
when they finish, to write what you confirmed. `srd:system-check learn` uses it
to bank what a non-SRD conversation taught, and `srd:backlog` hands it every
answered, moot, or reclassified open question.

## When to use it

Reach for it directly only to reorganize the knowledge base, or to work a
session's captures when no SRD skill is driving.

Everything else happens as a byproduct. Authoring an SRD stays one interview
with one question queue and no knowledge-base track running beside it.

## What it will not do

It does not commit — the agent writes the working tree, you commit. It does not
write outside the knowledge-base root, file documentation gaps
(`srd:report-doc-gap` owns those), edit SRDs, publish to Confluence, or record a
fact you have not confirmed.

## First run

It asks once for the knowledge-base directory and remembers it in
`$HOME/.agent-data/ctx42-skills/srd/kb-root`. The directory must not be managed
by a Confluence sync — a sync pull would clobber agent writes and the page would
silently revert — and should sit in a git repository so a bad write is
recoverable.

## Evaluations

### 1. Appends instead of fragmenting

**Request:** During an SRD interview the user confirms that correlation uses a
per-material propagation speed. A KB page on correlation already exists.

**Expect:**

- Searches the corpus before writing, and finds the existing page.
- Adds or updates a `##` section on that page rather than creating a second
  correlation page.
- Does not split the existing page to make room.
- Reports a pointer to what was written, not the page's contents.

### 2. Writes only what was attested

**Request:** The user explains how leak instances accumulate evidence, and the
agent infers a retention period that the user never stated.

**Expect:**

- The attested behavior is written to the page body.
- The inferred retention period does **not** appear in the body.
- It appears as an open question, mirrored into `_open-questions.md`.
- The section carrying undocumented content opens with its attestation line.

### 3. Stays inside the interview

**Request:** The SRD concerns hydrophone sensor types. Valve maintenance
intervals would round out the asset model but nothing in this SRD touches
valves.

**Expect:**

- Asks nothing about valves.
- May ask what values a sensor-type field takes, because the interview already
  opened that subject.
- On "skip that for now", routes the question to `_open-questions.md` marked
  deferred and moves on without re-asking.

### 4. Refuses a sync-managed root

**Request:** On first run the user offers a directory that the repo's
`.cfsync.yaml` maps to a Confluence space.

**Expect:**

- Refuses the path and says why: a sync pull would clobber every agent write.
- Asks for a different directory rather than proceeding.
- Does not write a page anywhere in the meantime.

### 5. Drains at start, writes at the end

**Request:** `srd:create` starts on SRD-42; a prior session left two candidates
buffered for it. The interview then confirms a third fact in a branch
restatement.

**Expect:**

- On the caller's start, names the two buffered candidates and offers to work
  them; says nothing when the buffer is empty.
- Buffers the third fact silently on discovery, with no corpus call and no
  question to the user.
- Writes nothing until `srd:create` reaches its write step, then writes the
  confirmed facts and empties the buffer.
- Asks no "bank this?" question at any point.

### 6. Restructure repairs every reference

**Request:** `/kb restructure` moving a `##` section from `_inbox.md` into a
new page while a gap record cites the inbox section's `doc_id`.

**Expect:**

- Shows the proposed moves and waits for confirmation before touching a file.
- Moves the section with its attestation line, provenance rows, and open
  questions.
- Re-derives anchors and repairs KB page links, `_open-questions.md` rows, and
  the gap store's `doc_id`.
- States that references from SRDs cannot be repaired and names the old ids.

### 7. Terse output

**Request:** A capture run writes two sections across two pages.

**Expect:**

- No preamble, no narration of the search or the file writes.
- The two pages and section counts stated once.
- No closing summary restating the sections, and no page contents echoed back.
