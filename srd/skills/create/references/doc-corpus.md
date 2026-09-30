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

   The same server carries the gap store, on the same host and port:
   `mcp__srd-doc__report_gap`, `mcp__srd-doc__list_gaps`,
   `mcp__srd-doc__resolve_gap`, mirrored as `GET /gaps`, `POST /gaps`, and
   `POST /gaps/{id}/resolve`. `srd:report-doc-gap` and `srd:backlog` own what
   may be called and when — this file is only where the address lives, so that
   a skill needing the gap endpoint before its first corpus lookup still has
   one place to read it.

   `<host>:<port>` is `localhost:7777` unless `SRD_DOC_HOST` and `SRD_DOC_PORT`
   say otherwise — both overridable, since a second instance on one machine
   cannot share the port — probe it
   before concluding there is no corpus. Missing MCP tools are not evidence the
   server is down; they are evidence this client has no MCP wiring, which is
   the exact case this step exists for. Reporting "no corpus" without a
   `curl 'http://localhost:7777/docs'` is the common way to miss a corpus that
   is running.
3. Scoped Grep/Read over a local corpus checkout, limited to the relevant
   subdirectory. A stopgap, never a blind whole-corpus read.

Default to `search` with `k` about 5; `get_doc` only when a hit needs its full
table or context; `list_docs` to orient. Every backend is read-only: it queries
the docs, never edits the SRD.

A source pointer is a document id: the string `get_doc` accepts, which is not
the path the file has in a checkout. Ids are namespaced by source — `ifp-doc/`,
`user-doc/`, `kb/` — so one page is `docs/infraport/formats/x.md` on disk and
`ifp-doc/formats/x.md` in the corpus. Record the id. Checking a path-shaped
citation against `list_docs` finds no match for any of them and reports a whole
page of live sources as stale; that is a defect in the comparison, not a stale
citation. Match on the trailing path first, and call a citation stale only when
no id ends in it.

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
starts, where they surface what a prior session left unfiled or unwritten. A
buffer file exists only while records are pending, so a calling skill probes
for one (`../scripts/probe-buffers.sh`) and invokes a delegate only when it has
something to drain: an absent buffer drains to nothing, and loading a skill to
learn that is the largest avoidable cost at session start. When the calling
skill finishes, `srd:kb` writes its confirmed facts and `srd:report-doc-gap`
offers to work the gaps buffered this session. `review` invokes only
`srd:report-doc-gap`: a read-only review confirms no platform fact with the
user. The user must never experience a second track beside the skill's own
work: no
knowledge-base phase, no separate questions, no "bank this?" prompt.
Confirmation of a platform fact rides on the calling skill's own confirmation
step, and `srd:kb` may ask only to deepen a subject that step already opened,
never to open a new one.

A buffer is keyed by the SRD's path. The SRD template carries no id field and
no skill assigns one, so nothing in this project is id-keyed: pass the probe
the path and nothing else, and never invent an id to key by. The script's
optional `SRD_ID` is for a caller that already holds an id from somewhere else
— a ticketing system, another repository — and wants both keys probed.
