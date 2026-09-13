# The decision log

`<srd>.decisions.md` — what it records, its shape, and what each mode owes it.
Read before writing the first entry of a session; no mode needs it earlier.

`autofix` is a bulk path through the same gate, not an exception to it: every
substitution it applies is an applied edit and owes its entry, and
[`autofix.md`](autofix.md) is the procedure for finding and
applying them, not the whole of what the mode owes.

Record every applied edit in `<srd>.decisions.md` beside the source — the
author-facing account of what changed and why, which a diff cannot carry.

- Write after each applied edit, never batched to session end: a session that
  clears mid-flow must lose nothing.
- Accumulate: one file per SRD, `##` session blocks headed by the date, newest
  first. Never rewrite or prune an earlier block.
- Record the entry/id, the change in prose (not a diff), and the reason: the
  user's rationale when they gave one, the proposal's when it stood unamended.
- Rephrase the user's words into clean prose — fix typos, expand shorthand,
  drop the conversational frame — keeping decision and reason intact. Never
  invent a reason the user did not give.
- Every applied edit, loop or not: `autofix` logs one entry per substitution,
  Add-to-TODO logs its line. Same changes, same log.
- Skipped and flagged-but-unfixed issues are not logged: they stay in the
  review file, or — with none, since `edit` may not create one — in the closing
  manifest, which then says which were left and why.
- Write for the SRD's author, not a reviewer: name the surface in the SRD's own
  words; cite a rule id only where the user did.
- Create the file on the first write, frontmatter and title included;
  `cfsync-plugin: ignore-push` keeps the Confluence sync from pushing it.

Example of the file after one session — the date, heading, ids, and prose are
illustrative, not boilerplate to copy:

````
---
cfsync-plugin: ignore-push
---

# Changes — <Document Title>
