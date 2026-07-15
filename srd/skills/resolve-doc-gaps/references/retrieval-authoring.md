# Authoring a page for retrieval

The doc-gap draft is published into a corpus served by `srd-doc`: **BM25
keyword search over section chunks**, no semantic matching. A page is found
only by the words it contains and ranked by where those words sit. These rules
mirror the server's own `docs/authoring.md`; apply them to every draft so the
new page indexes and ranks well once synced.

## Headings

- Break sections with `#` or `##`, not `###`+ — only level-1 and level-2
  headings start a new chunk; deeper headings just extend the heading path.
- Make every `#`/`##` heading keyword-rich — headings index into a boosted
  field, so a term in a heading outranks the same term in the body. No vague
  `Overview`.
- Split a section over ~800 tokens into focused sub-`##` sections, one topic
  each.

## Title and names

- Give the page a descriptive title — it indexes into the boosted title field
  for every chunk.
- Name the file/page for its topic; `_`, `-`, and `/` split into searchable
  terms.
- Declare synonyms once in front-matter `aliases` (they index as extra title
  terms), not sprinkled through prose. Do not hand-write plural/tense variants
  — the index stems English.

## Facts

- State each capability as an explicit sentence — an agent verifies a claim by
  searching for its words. Write the exact `target_claim` from the gap as a
  plain declarative sentence.
- Prefer one canonical term per concept; scattered names split matches.
- Keep glossary-style definitions one per `##` heading.

## Links and tables

- Put the canonical URL first in the body — a citation uses the first
  `atlassian.net` link, else the first `http(s)` URL.
- Give tables real column headers and a one-line caption sentence; bare pipe
  cells tokenize poorly.

## Absent vs unfindable

A gap's `search_terms` plus a live `search`/`get_doc` check tell you which fix
the page needs:

- **Genuinely absent** — nothing relevant exists. Write new prose.
- **Present but unranked** — the fact is there but the search terms miss it.
  The fix is structural: rename the section heading to carry the query words,
  add `aliases`, and restate the fact as an explicit sentence. Draft the edit
  to the existing page, not a duplicate.
