# SRD Shared Procedures

Operating procedures shared by the SRD skills. These are not rules (the SRD
standard, read through the server per `project-config.md`) and not drafting aids
(`authoring-guide.md`) — they are steps a skill runs. `create` and `edit` cite
this file instead of restating the steps.

## Resolve the shared glossary

The shared glossary (whatever name the standard gives it) lets an SRD meet the
standard's term-definition rules without redefining terms defined elsewhere. It
is the `glossary` location in `project-config.md`, and its known-term set is
exactly what `mcp__<mcp-server>__glossary_terms` returns.

1. Call `glossary_terms` (no filter) before the first term is checked against
   it, and hold the returned `terms` for the session; a later single-term
   lookup may pass a substring filter. The server keeps it current: never cache
   it across sessions, fingerprint it, or digest it.
2. A term in the set (match `term`, `name`, or `abbreviation`) whose `path`
   lies under the `glossary` location needs no local entry; link it on first
   use to `<path>#<anchor>` (the result's `anchor`: the term's heading slug),
   written relative to the SRD's own file, when the standard asks for glossary
   links: a link navigates, so it takes `path`, never `id`. The first use
   counts from the first section after the metadata on: a use in the metadata
   block (its summary field included) takes no link, and a finding asking for
   one there is invalid. A hit whose `path` lies elsewhere is not the shared
   glossary: treat the term as not in the set.
3. A term not in the set needs a local terms entry, even when another corpus
   document explains it: `search` returns meaning, not coverage. Say so once
   ("`X` is explained in `<path>`, which is not the shared glossary;
   defining it locally").
4. An empty `terms` list is a valid answer: every term is defined locally. A
   failed call stops the run like a gate failure.

## Derive the in-scope list from requirements

In-scope items are the deliverables the requirements implement, so they are
best written after the requirements settle. Run this when the in-scope list
holds the `--- TODO ---` marker (see the authoring guide's house additions) and
the user signals the requirements are complete or asks to fill it:

1. Read every requirement group and cluster them by the distinct capability each
   delivers.
2. Draft one candidate item per capability — a high-level overview of one
   change, each covered by ≥ 1 requirement, none contradicting the
   out-of-scope list. Phrase each as a deliverable, not a restated
   requirement. Give no candidate an identifier: step 3 may drop or merge any
   of them, and an identifier shown before that has to be taken back. A
   positional label to point at one by — "the third", "candidate 3" — carries
   no id and is fine.
3. Show the candidate list once, then take them through the calling skill's
   confirm-each loop one at a time: approving keeps a candidate, `E` carries a
   reword — and a merge or a split, which arrive as amended text — and a skip
   drops it. No identifier is assigned yet, so a drop costs no renumbering.
4. Replace the `--- TODO ---` marker with the confirmed items, in the form the
   standard sets for them (numbered from 1 in order when it gives them
   identifiers). Re-run the in-scope coverage check now that the marker is
   gone.
