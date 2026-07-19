# SRD Shared Procedures

Operating procedures shared by the SRD skills. These are not rules
([srd-standard.md](srd-standard.md)) and not drafting aids
([authoring-guide.md](authoring-guide.md)) — they are steps a skill runs.
`create` and `edit` cite this file instead of restating the steps.

## Resolve the shared glossary

The shared glossary lets an SRD satisfy GLO-3 / STR-10 without redefining terms
defined elsewhere. Each project has its own glossary — a single Markdown file or
a directory of Markdown documents. Its path, a content hash, and a
model-synthesized **digest** of its terms are remembered per project (see
[Glossary memory](#glossary-memory)), so the digest is rebuilt only when the
glossary actually changes. Run this before drafting or editing:

1. Read the glossary memory for this project.
2. No record (first run) → ask the user for the glossary path and save it.
3. Path does not resolve → tell the user; ask for a corrected path, or proceed
   with an empty set (every term must then be defined locally). A remembered path
   that resolves is used **silently** — never confirmed every run; the user
   overrides it only by asking.
4. Fingerprint the docs: `create/scripts/glossary-fingerprint.sh <path>` prints
   one content hash covering every `*.md` under the path.
5. Compare the hash with the one in memory:
   - Match → use the cached digest as-is.
   - Differ, or no digest yet → read the glossary docs, synthesize a fresh digest
     (each term with a short gloss, grouped, with any notes), and save the digest,
     the new hash, and today's date. Tell the user in one line that the glossary
     changed and the digest was regenerated.
6. Use the digest as the known-term set: as terms surface while drafting or
   editing, link the ones the digest defines and add local Glossary entries only
   for the rest.

### Glossary memory

Keep one record per project in the standard per-project memory. It holds: the
glossary path (file or directory); the last content hash from
`glossary-fingerprint.sh`; the date the digest was last regenerated; and the
digest body. Nothing about the glossary lives in the skill directory or in
`$HOME/.agent-data` — only in project memory, so each project resolves to its own
glossary automatically.

## Derive In Scope from requirements

In Scope items are the deliverables the requirements implement (SCO-2), so they
are best written after the requirements settle. Run this when `### In Scope`
holds the `--- TODO ---` marker (see the authoring guide's house additions) and
the user signals the requirements are complete or asks to fill In Scope:

1. Read every requirement group and cluster them by the distinct capability each
   delivers.
2. Draft one candidate `SC-n` item per capability — atomic and verifiable
   (SCO-1), each covered by ≥ 1 requirement (SCO-2), none contradicting Out of
   Scope (SCO-3). Phrase each as a deliverable, not a restated requirement.
3. Present the candidates and let the user edit them point by point through the
   calling skill's confirm-each loop: keep, reword, merge, split, or drop each.
4. Replace the `--- TODO ---` marker with the confirmed `SC-n` items, numbered
   from 1 in order. Re-run the In-Scope-coverage check now that the marker is
   gone.
