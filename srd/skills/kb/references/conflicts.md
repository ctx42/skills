# Conflicts and stale citations

How a KB write settles a fact that disagrees with another source, and how a
stale citation is repaired. Read when a confirmed fact contradicts a platform
document, a KB section, or an SRD, and when a caller hands over a stale
citation.

## Authority

The shared corpus reference settles conflicting sources by the `rank` on each
result, never by folder. Consequences for KB writes:

- A conflict is a finding, never a silent tie-break. When an attested fact
  contradicts a platform document (not a KB section — see below), either the
  document is stale or the KB is wrong. Surface it; hand a stale document to
  `srd:report-doc-gap`. Before surfacing a UI observation as a conflict,
  check a second record with different data, or ask the user to: a field shown
  or hidden can depend on the record (an address present or absent). Once the
  conflict stands, a fact the user confirmed against the document is written
  without a further question, its attestation line opening
  ``> Contradicts `<identity>`.`` (the document's `id`) in place of
  `> Not in the platform docs.` — whether the conflict was known at
  confirmation or turned up after it, at write time: a fact written while a
  document says otherwise always carries the line.
- A KB section and an SRD never contradict, and no `rank` settles one that
  does: an SRD has none. A confirmed fact rewrites the section it contradicts
  at once (step C.1): the KB changes on confirmation, not when other SRDs
  agree.

## Stale citations

A caller may also hand over a stale citation: a KB page citing an identity no
`list_docs` `id` or `path` matches. Repair it in place (re-find the document by
`search` and cite its `id`, or drop the citation and mark the fact as attested
only) and report the page.
