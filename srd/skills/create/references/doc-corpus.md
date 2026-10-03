# Documentation Corpus

How the SRD skills ground claims about the existing platform in its live
documentation, and where what a lookup teaches goes. Shared by `create`,
`review`, `edit`, and `system-check`: each skill says *when* it consults the
corpus, this file says *how*. The gate in [project-config.md](project-config.md)
guarantees the server answers before any skill starts. An assertion about
existing system behavior that no lookup confirms stays unconfirmed and is
flagged as such; silently accepting a platform claim is the one outcome this
file rules out.

## Contents

- Tools
- Trust
- Where a lookup's outcome goes

## Tools

All corpus and gap-store calls go to `mcp__<mcp-server>__<tool>`, with
`<mcp-server>` from `project-config.md`:

- Read: `search` (query, optional `k`), `get_doc` (document id), `list_docs`
  (no args), `glossary_terms` (optional substring filter).
- Gaps: `report_gap` (optional `draft: true`), `update_gap`, `submit_gap`,
  `discard_gap`, `list_gaps` (filters `status`, `srd_ref`), `mark_gap_kb`,
  `resolve_gap`. `srd:report-doc-gap` and `srd:backlog` own which may be called
  and when.

Default to `search` with `k` about 5; `get_doc` only when a hit needs its full
table or context; `list_docs` to orient. A call that errors is reported, never
retried or worked around. The read tools query the docs, never edit the SRD.

A source pointer is a document id: its path from the project root, the string
`get_doc` accepts (`confluence/example/formats/x.md`). Record the id, not an
absolute checkout path. To check a citation written as a checkout path, strip
the prefix down to the id; a citation is stale only when no `list_docs` id ends
in the rest — comparing raw strings condemns every live source on the page.

## Trust

Sources do not rank by trust; the index ranks by term placement. When two
sources disagree, that is a finding, not a tie-break: surface it to the user.
The knowledge base leads on how the system behaves, the glossary on what a term
means; a user manual is consulted because it is the only source on a topic,
never because it outranks anything.

## Where a lookup's outcome goes

A lookup that confirms the claim needs nothing more. The other outcomes each
have an owner; the calling skill only spots them and delegates:

- The corpus cannot confirm the claim (content missing, wrong, incomplete, or
  ambiguous): a documentation gap. Hand it to `srd:report-doc-gap`, which
  captures it as a server-side draft and owns the grill and the filing. A
  defect in the SRD itself is never a doc gap; it stays in the calling skill's
  own findings.
- The corpus is silent but the user confirms the fact: tribal knowledge. Hand
  it to `srd:kb` once confirmed; it writes it to `<kb>/_inbox.md` at once. A
  term the user defines because no glossary carries it is the same case.
- One fact may be both: `srd:kb` states it now, `srd:report-doc-gap` records
  that the docs should eventually carry it. Send it to both.

**Draft check at start.** A calling skill with an SRD calls `list_gaps` with
`status: draft` and `srd_ref` the SRD's path from the project root, and invokes
`srd:report-doc-gap` only when that returns a record — an empty list is the
usual case and needs no skill loaded. The calling skill's report says, in one
clause, that the check ran and what it found. With no SRD path yet there is
nothing to check.

When the calling skill finishes, it invokes `srd:report-doc-gap` to offer the
drafts captured this session, only when there are any. `review` hands nothing
to `srd:kb`: a read-only review confirms no platform fact with the user.

The user must never experience a second track beside the skill's own work: no
knowledge-base phase, no separate questions, no "bank this?" prompt.
Confirmation of a platform fact rides on the calling skill's own confirmation
step, and `srd:kb` may ask only to deepen a subject that step already opened,
never to open a new one. Nothing in this flow keys by an SRD id: SRDs carry
none, so pass the path and never invent one.
