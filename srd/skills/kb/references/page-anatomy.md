# KB page anatomy and open questions

How a KB page and the inbox are built — front matter, the attestation line,
the `## Provenance` row — and how a question SRD work leaves open is filed.
Read before every write to a KB page or the inbox, and when a question stays
open.

## Contents

- Page anatomy — front matter, body rules, the attestation line, `## Provenance`
- Open questions — `deferred` vs `unknown`, filing, the `> Open:` warning

## Page anatomy

One page per subject, many `##` sections per page. Only `#` and `##` start a new
chunk, so `##` is the unit that reaches an agent alone.

Front matter:

```yaml
---
title: Acoustic Leak Detection
aliases: [AUTOCO, automated cross-correlation]
attested: 2026-09-11
srd_ref: int384-hydrophone, autoco
last_verified: 2026-09-11
---
```

`srd_ref` accumulates: a page attested across several SRDs lists their SRD
references (folder names, per the gate reference) comma-separated,
earliest first, and a write appends rather than replaces.
`attested` stays the first date; `last_verified` moves.

`title` is always explicit — without it the indexer falls back to the file name.
`aliases` carry abbreviations and synonyms; they index at the title's boost on
every section of the page, so a search for the short form finds it. The
remaining keys are for humans and staleness sweeps; the indexer ignores them.

Body rules:

- The body states attested facts only. Anything the agent concluded but the
  user did not confirm never enters it — that is an open question, not a fact.
  This rule alone keeps a large KB trustworthy. After each write, re-read the
  page and delete every sentence no attested statement says, a consequence or
  generalization of the fact included; a sentence meant to be cut is cut only
  once the file no longer holds it.
- Mark tribal sections in place. A section carrying something the platform
  docs do not state opens with one line under its heading, so the mark travels
  inside the chunk:

  ```
  > Not in the platform docs. Attested int384-hydrophone interview
  > 2026-09-11 · `gap-0019`.
  ```

  The source (the SRD reference) and the date are required; a document the
  line cites is an inline-code identity (`` `1774485611#tag-names` ``), never
  a path the document only has today; the `· gap-NNNN` is there only when
  `srd:report-doc-gap` actually filed one and returned an id. Most captures
  have none — a fact can be missing from the docs without anyone reporting
  that as a gap — so omit the segment rather than inventing a number or
  holding the write until a gap exists. When a gap for the fact is filed
  later in the same session, add its id to the line then. Where there is no
  SRD in play (a bare capture, a `/backlog` sitting), name the session
  instead: `Attested session 2026-09-11`.

  A page-level provenance table cannot do this job: it is its own chunk, and an
  agent reading a fact never receives it.

- `## Provenance` closes the page as a human-facing roll-up — which areas
  rest on documents, which on a conversation. An index, not the mechanism.
  Every write adds or updates its row there, whether the write creates the
  page or appends a section to one: a roll-up nobody maintains indexes a page
  that has moved on. A citation repair updates the row of the fact it
  repairs; it adds none. A page with no `## Provenance` yet gets one on the
  first write that touches it. The inbox keeps one too, and a section filed
  out of it carries its row along. When it holds more than one table, address
  the target by its header row, never every `|` line after the heading.
- A page states no open question: what its subject leaves unanswered is a gap.
  See `## Open questions` below.

## Open questions

A question SRD work leaves open is a gap in the server's store, never a KB
write. Its `answer` says which kind: `deferred` — someone knows, the session
did not take it; closable in seconds. `unknown` — nobody has pinned it down; it
needs deciding or finding out.

A guess of your own that the user never confirmed is `deferred`, not `unknown`:
the user was there and could have settled it, and calling it an unknown puts
the agent's inference on the same footing as a fact nobody in the organization
has. State it as the question it answers ("does evidence expire, and after how
long?"), never as the inference wearing a question mark.

A user who does not know the answer: the *Who would know* section of the
shared `doc-corpus.md` reference.

File it through `srd:report-doc-gap` with `answer` set; it dedups with
`list_gaps` `query`, and a question already on file gets a hit
(`update_gap` `add_hit: true`), never a second record. Repeats are a priority
signal.

A KB page, the inbox included, keeps at most a point-of-use warning: one line
after the attestation line of the section the question concerns,
`> Open: gap-0042.`, naming the filed gap's id — never the question's wording,
which lives on the gap alone. Add it only once the gap is filed (a draft's id
can vanish); delete it when the section comes to state the answer.

`srd:backlog` works these gaps and hands each answer here like any caller.
