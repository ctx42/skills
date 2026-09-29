# SRD Shared Procedures

Operating procedures shared by the SRD skills. These are not rules
([srd-standard.md](srd-standard.md)) and not drafting aids
([authoring-guide.md](authoring-guide.md)) — they are steps a skill runs.
`create` and `edit` cite this file instead of restating the steps.

## Resolve the Company Glossary

The Company Glossary lets an SRD satisfy GLO-3 / STR-10 without redefining terms
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
   "This project has no Company Glossary" is an answer, not a missing one:
   record it as an explicit `none` and treat the known-term set as empty from
   then on. Without that record the question returns every session, which is
   the setup interruption this procedure exists to spend once.
4. Fingerprint the docs: run `glossary-fingerprint.sh <path>` from the `create`
   skill's `scripts/` directory (`../scripts/` from this file); it prints one
   content hash covering every `*.md` under the path.
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

Keep one record per project at `.claude/srd/glossary-memory.md`, relative to
the project root — the directory the SRD work is happening in, not the skill's
own checkout. It holds: the glossary path (file or directory); the last content
hash from `glossary-fingerprint.sh`; the date the digest was last regenerated;
and the digest body.

That location, and not `$HOME/.agent-data`, because the binding is
project-to-glossary: one machine works on several projects, and a
machine-global record would hand the wrong glossary to the next one. Create the
file and its directory on first use. Whether it is committed or ignored is the
project's call — a committed one saves every teammate the first-run question.

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
   requirement. Leave the candidates unnumbered: step 3 may drop or merge any
   of them, and an `SC-n` shown before that has to be taken back.
3. Show the candidate list once, then take them through the calling skill's
   confirm-each loop one at a time: approving keeps a candidate, `E` carries a
   reword — and a merge or a split, which arrive as amended text — and a skip
   drops it. Nothing is numbered yet, so a drop costs no renumbering.
4. Replace the `--- TODO ---` marker with the confirmed `SC-n` items, numbered
   from 1 in order. Re-run the In-Scope-coverage check now that the marker is
   gone.
