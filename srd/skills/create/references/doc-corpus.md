# Documentation Corpus

How the SRD skills ground claims about the existing platform in its live
documentation, and where what a lookup teaches goes. Shared by `create`,
`review`, `edit`, and `system-check`: each skill says *when* it consults the
corpus, this file says *how*. Absent a corpus, every skill runs offline: skip
the lookups, never stop — but skipping the lookup does not confirm the claim.
An assertion about existing system behavior that no one checked stays
unconfirmed, and is flagged as such, offline exactly as it would be online. The
only thing the corpus's absence changes is who can settle it: with a corpus,
the lookup; without one, the user. Silently accepting a platform claim because
there was nothing to check it against is the one outcome this file rules out.

## Backends

Fall through in this order, only when a step genuinely is not there, never on
one failed call:

1. The `srd-doc` MCP tools: `mcp__srd-doc__search` (query, optional `k`),
   `mcp__srd-doc__get_doc` (document id), `mcp__srd-doc__list_docs` (no args).
2. The `srd-doc` REST mirror, when the server runs but MCP is not wired into
   this client: `curl 'http://<host>:7777/search?q=TEXT&k=5'` and
   `curl 'http://<host>:7777/docs/<id>'`. Same engine, same results.

   `<host>` is `localhost` unless `SRD_DOC_HOST` says otherwise — probe it
   before concluding there is no corpus. Missing MCP tools are not evidence the
   server is down; they are evidence this client has no MCP wiring, which is
   the exact case this step exists for. Reporting "no corpus" without a
   `curl 'http://localhost:7777/docs'` is the common way to miss a corpus that
   is running.
3. Scoped Grep/Read over a local corpus checkout, limited to the relevant
   subdirectory. A stopgap, never a blind whole-corpus read.

Default to `search` with `k` about 5; `get_doc` only when a hit needs its full
table or context; `list_docs` to orient. A source pointer is a document id.
Every backend is read-only: it queries the docs, never edits the SRD.

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
  ambiguous): a documentation gap. Hand it to `srd:report-doc-gap`, which owns
  capture, the grill, and the confirmed `report_gap` filing. A defect in the
  SRD itself is never a doc gap; it stays in the calling skill's own findings.
- The corpus is silent but the user confirms the fact: tribal knowledge. Hand
  it to `srd:kb`, which owns capture, the pages, and the writing. A term the
  user defines because no glossary carries it is the same case.
- One fact may be both: `srd:kb` states it now, `srd:report-doc-gap` records
  that the docs should eventually carry it. Send it to both.

Both delegates buffer silently on discovery and drain when the calling skill
starts, where they surface what a prior session left unfiled or unwritten. When
the calling skill finishes, `srd:kb` writes its confirmed facts and
`srd:report-doc-gap` offers to work the gaps buffered this session. `review`
invokes only `srd:report-doc-gap`: a read-only review confirms no platform fact
with the user. The user
must never experience a second track beside the skill's own work: no
knowledge-base phase, no separate questions, no "bank this?" prompt.
Confirmation of a platform fact rides on the calling skill's own confirmation
step, and `srd:kb` may ask only to deepen a subject that step already opened,
never to open a new one.
