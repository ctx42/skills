# backlog

One sitting for everything the knowledge base and the documentation still owe.

## Usage

```
/backlog              all three lists, cheap wins first (default)
/backlog deferred     questions you know the answer to; closed by asking
/backlog unknowns     things nobody has pinned down; triage, not answering
/backlog gaps         reported holes in the user manual; drafts the page
```

## When to use it

When you sit down to clear what SRD work has piled up — not during SRD work
itself. The SRD skills fill these lists as a byproduct: `srd:kb` keeps the
deferred questions and unknowns in the knowledge base's `_open-questions.md`,
and `srd:report-doc-gap` files the gaps to the `srd-doc` gap store. This skill
is where you empty them.

## The three lists are different work

`deferred` closes in seconds: you know the answer, the interview just ran out of
room. `unknowns` cannot be closed by asking at all — someone has to decide or go
find out, so the sitting triages them instead. `gaps` is a writing task against
the user manual, for end users, and says nothing about what the system is.

Keeping them apart is the point. An unknown filed as a documentation gap sits
forever in a backlog whose only tool is authorship.

## What it will not do

It never writes knowledge-base files itself — `srd:kb` owns those, and every
write, row move, or row edit is delegated to it. It never publishes to
Confluence: it drafts the page, you publish it, and it records the URL against
every gap in the cluster. It does not file new gaps (`srd:report-doc-gap` does
that during SRD work), and it never closes an unknown with a guess.

## Degrading

The two knowledge-base lists and the gap list depend on different backends and
fail independently. With no gap store configured you can still work deferred
questions and unknowns; with no knowledge base you can still work gaps.

## Evaluations

### 1. Opens with counts, not with work

**Request:** `/backlog` with 3 deferred, 2 unknowns, and 5 open gaps.

**Expect:**

- States the three counts and stops, letting the user choose a list.
- Leads with `deferred` as the cheap wins.
- Does not start grilling or drafting before the user picks.
- No preamble; counts stated once.

### 2. Will not close an unknown with a guess

**Request:** `/backlog unknowns` where one row asks whether a per-sensor-type
propagation speed is needed, and nothing has been decided.

**Expect:**

- Does not answer it from inference or from corpus reading.
- Confirms it is still open and moves on, or closes it only if the user reports
  a decision was taken.
- Leaves the row in `## Open`; bumps no hit count.

### 3. Reclassifies rather than skipping

**Request:** `/backlog deferred` and the user answers "actually nobody knows
that yet".

**Expect:**

- Has `srd:kb` change the row's kind from `deferred` to `unknown` in place and
  says so; writes nothing under the KB root itself.
- Does not treat it as a skip or leave it mislabeled.
- Does not file it as a documentation gap.

### 4. Clusters gaps and drafts outside the corpus

**Request:** `/backlog gaps` with three open gaps, two of them the same missing
fact.

**Expect:**

- Clusters the two duplicates and surfaces the cluster size as priority.
- Checks the corpus before drafting, separating absent content from
  present-but-unranked.
- Writes the draft outside every corpus source, including the KB root.
- Resolves every gap in the cluster once given the published URL.

### 5. Degrades without a gap store

**Request:** `/backlog` against a server that exposes neither `list_gaps` nor
`GET /gaps`, with 2 deferred and 1 unknown in `_open-questions.md`.

**Expect:**

- Says once that the gap store is not enabled and counts the two KB lists.
- Works `deferred` and `unknowns` normally.
- Does not invent a store or retry the failed probe.

### 6. Terse output

**Request:** A sitting that closes two deferred questions and one gap cluster.

**Expect:**

- No narration of the list calls or the row moves.
- What closed, stated once.
- No closing summary repeating the rows, and no drafted page echoed back.
