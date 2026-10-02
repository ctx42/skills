# SRD Shared Procedures

Operating procedures shared by the SRD skills. These are not rules (the SRD
standard, read through the server per [project-config.md](project-config.md))
and not drafting aids ([authoring-guide.md](authoring-guide.md)) — they are
steps a skill runs. `create` and `edit` cite this file instead of restating the
steps.

## Resolve the Company Glossary

The Company Glossary lets an SRD satisfy GLO-3 / STR-10 without redefining terms
defined elsewhere. It is the `glossary` location in `project-config.md`, and its
known-term set is exactly what `mcp__<mcp-server>__glossary_terms` returns.

1. Call `glossary_terms` (no filter) before the first term is checked against
   it, and hold the returned `terms` for the session; a later single-term
   lookup may pass a substring filter. The server keeps it current: never cache
   it across sessions, fingerprint it, or digest it.
2. A term in the set (match `term`, `name`, or `abbreviation`) needs no local
   entry; link it on first use to `<doc_id>#<anchor>`, written relative to the
   SRD's own file (GLO-4/5).
3. A term not in the set needs a local Glossary entry, even when another corpus
   document explains it: `search` returns meaning, not coverage. Say so once
   ("`X` is explained in `<doc_id>`, which is not the Company Glossary;
   defining it locally").
4. An empty `terms` list is a valid answer: every term is defined locally. A
   failed call stops the run like a gate failure.

## Derive In Scope from requirements

In Scope items are the deliverables the requirements implement (SCO-2), so they
are best written after the requirements settle. Run this when `### In Scope`
holds the `--- TODO ---` marker (see the authoring guide's house additions) and
the user signals the requirements are complete or asks to fill In Scope:

1. Read every requirement group and cluster them by the distinct capability each
   delivers.
2. Draft one candidate item per capability — a high-level overview of one
   change (SCO-1), each covered by ≥ 1 requirement (SCO-2), none contradicting
   Out of Scope (SCO-3). Phrase each as a deliverable, not a restated
   requirement. Give no candidate an `SC-n`: step 3 may drop or merge any of
   them, and an `SC-n` shown before that has to be taken back. A positional
   label to point at one by — "the third", "candidate 3" — carries no id and is
   fine.
3. Show the candidate list once, then take them through the calling skill's
   confirm-each loop one at a time: approving keeps a candidate, `E` carries a
   reword — and a merge or a split, which arrive as amended text — and a skip
   drops it. No `SC-n` is assigned yet, so a drop costs no renumbering.
4. Replace the `--- TODO ---` marker with the confirmed `SC-n` items, numbered
   from 1 in order. Re-run the In-Scope-coverage check now that the marker is
   gone.
