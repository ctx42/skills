# SRD Shared Procedures

Operating procedures shared by the SRD skills. These are not rules
([srd-standard.md](srd-standard.md)), not checks
([srd-checklist.md](srd-checklist.md)), and not drafting aids
([authoring-guide.md](authoring-guide.md)) — they are steps a skill runs.
`create` and `edit` cite this file instead of restating the steps.

## Resolve the shared glossary

The shared glossary lets an SRD satisfy GLO-3 / STR-10 without redefining terms
that are already defined elsewhere. The glossary may be a single Markdown file or
a directory of Markdown documents; the extractor accepts either. Run this before
drafting or editing:

1. Determine the glossary path. If a path is remembered from a previous run
   (memory note `srd-glossary-dir`), show it and ask the user to confirm or
   override. Otherwise ask for it. The remembered path is confirmed every run,
   never assumed.
2. State the path you will use, noting whether it is a file or a directory.
3. Run the extractor `create/scripts/glossary-terms.sh <path>` to load the
   known-term set.
4. If the path does not exist, tell the user and proceed with an empty set —
   every term must then be defined locally.
5. Save the confirmed path to memory for next time.
