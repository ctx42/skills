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
- Before flagging a device/product model named in a requirement, check whether the
  UI surface or feature itself exists only for those models; when it does, the
  model name is the correct scope — never propose generalizing it away.
- Drop catch-all "features not explicitly addressed behave identically / stay
  unchanged" requirements — an SRD specifies only what changes; unspecified
  areas are unchanged by default (also weakly verifiable, REQ-5/LANG-7).
- Never trail a proposal with a paragraph of loose "things I'd flag" questions;
  ask ONE question at a time, and carry anything held over as a short numbered
  list (one line each) the user can answer by number.
- Never edit, reply to, or rewrite comment blocks in an SRD; treat them purely
  as a source of problems and information about the SRD, and leave them verbatim
  even when they hold stale references.
- Write requirements in plain, simple language: short sentences, everyday verbs,
  one clause of condition at most. Never stack nested qualifiers ("Devices whose
  sound files are eligible for correlation with the first Device's sound files")
  — say the simple thing and let the linked platform doc carry the precision.
- Keep the front-loaded issue summary to findings that survive scrutiny: before
  listing one, check it is a real rule violation, not a stylistic preference.
  Requirements that read as overlapping are often independently testable (a
  disabled control vs a grayed one; a length cap vs its truncation format), a
  scope item covering one capability across many surfaces is still atomic, and a
  compound term whose parts are both in the company glossary needs no entry.
  Withdrawing findings mid-session costs the user's trust in the whole list.
- "Tag", "metadata", "header", and "channel" are overloaded across the IFP
  corpus: always qualify which one a requirement means (e.g. "a sound file's
  `sen.kind` metadata tag", not "the `sen.kind` tag"). Being terse is no excuse
  for a term that resolves differently in another document.
- `REQ` is a legitimate requirement prefix for any SRD; the standard's own
  `STR-*`/`REQ-*` ids name its rules and must not be pasted in as an SRD's
  requirements, but the letter codes are NOT reserved. Never raise a prefix
  "collision" with the standard as a finding.
- When bulk-rewriting requirement ids (a renumbering pass), exclude every
  comment block from the substitution — comment text is verbatim history and an
  id inside it may name a requirement that never existed. Verify afterwards that
  no comment line contains a new-scheme id.
