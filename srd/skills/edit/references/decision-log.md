# The decision log

`<srd>.decisions.md` — what it records, its shape, and what each mode owes it.
Read before writing the first entry of a session; no mode needs it earlier.

`<srd>.decisions.md` names the SRD's path with its `.md` extension replaced:
`specs/login.md` gives `specs/login.decisions.md`, never
`specs/login.md.decisions.md`. `<srd>.review.md` and `<srd>.questions.md` are
formed the same way.

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
- One `###` heading per section per session: a later entry for a section this
  session already wrote under appends to that block, it never opens a second
  one. A new `###` heading only for a section the session has not touched yet.
  Incremental writing is what makes this explicit — the entries arrive one at a
  time, and the block they join is the one already on the page.
- Record the entry/id, the change in prose (not a diff), and the reason,
  quoted verbatim: the user's words when they gave a reason, else the
  proposal's one-line rationale when it stood unamended (a bare `Y`). Quote,
  never paraphrase — a paraphrase is where invented reasons got in. Trim only
  the conversational frame around the quote (`yes, because`) and the
  interaction text a rationale carries — keystroke hints (`` `E` to give a
  different limit ``) and process notes (`so no corpus lookup`, `read as a
  figure the SRD sets`); keep its typos and shorthand. No quotable reason, no
  reason logged — an `autofix` entry has no proposal, so it logs the user's
  words or nothing, never the review finding's text. A reason that holds a
  double quote is wrapped in single quotes.
- Every applied edit, loop or not: `autofix` logs one entry per substitution,
  Add-to-TODO logs its line. Same changes, same log.
- Skipped and flagged-but-unfixed issues are not logged: they stay in the
  review file, or — with none, since `edit` may not create one — in the closing
  manifest, which then says which were left and why.
- Write for the SRD's author, not a reviewer: name the surface in the SRD's own
  words; cite a rule id only where the user did.
- Create the file on the first write, title included.

Example of the file after one session — the date, heading, ids, and prose are
illustrative, not boilerplate to copy:

````
# Changes — <Document Title>

## 2026-07-27

### Details page

DET-14 was removed, with its open "retention period to be confirmed" note.
Reason: "retention isnt part of this srd, DET-13 already covers history after
reassignment".

DET-9 now names the sample rate in hertz instead of "high resolution".
Reason: "Names a measurable value in place of an untestable adjective."

### General

The British spellings in the Introduction were changed to US English.
````

The second Details page entry was written later in the same session and joined
the heading already there; General is a second heading because the session had
not written under it before.
