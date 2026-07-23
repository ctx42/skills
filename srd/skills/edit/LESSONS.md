# Lessons

Rules learned for the `edit` skill. Read before running; obey each line.

- Never propose changing an SRD's Status or list status advancement (e.g. to
  "ACCEPTED") as a follow-up — Status transitions are solely the human's
  decision; flag only a malformed STA-* value, never a transition.
- Never propose pushing or publishing an SRD (to Confluence or anywhere), and
  never frame "push before the next pull" or similar sync action as a
  follow-up or action item.
- Advance to the next entry ONLY when the user explicitly asks; after an entry
  is resolved, stop and wait — do not walk ahead to later entries, not even for
  read-only assessment.
- The introduction need not state what the system will NOT do — STR-9's "will
  and will not" is satisfied by purpose + what it will do (Out of Scope carries
  the rest); never flag the intro for a missing "will not do".
- Never require or propose a Glossary section when nothing genuinely needs
  defining (STR-10 is conditional: "terms that need a definition"). Proper names
  — product/module names, external tool names, device models — are not concepts
  needing definition; do not flag them as GLO-3 gaps or push a Glossary for them.
- Do not bold Markdown section/subsection headings (`### **X**`); SRD headings
  are plain (`### X`). Bold is redundant with heading markup — never add it, and
  de-bold existing ones.
- When a requirement would restate rules already defined in an authoritative
  platform doc, link to that doc and state only the minimal SRD-level constraint;
  do not duplicate the full mechanics in the SRD.
- Drop catch-all "features not explicitly addressed behave identically / stay
  unchanged" requirements — an SRD specifies only what changes; unspecified
  areas are unchanged by default (also weakly verifiable, REQ-5/LANG-7).
