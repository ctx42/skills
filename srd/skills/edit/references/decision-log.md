# The decision log

`<srd>.decisions.md` — what it records, its shape, and what each mode owes it.
Read before writing the first entry of a session; no mode needs it earlier.

`<srd>.decisions.md` is the SRD's `decisions` working file (`project-config.md`,
"5. Working files"): beside the SRD (`initiatives/slot-swap/srd.md` gives
`initiatives/slot-swap/srd.decisions.md`), or under `srd-work` when set.
`<srd>.review.md` and `<srd>.questions.md` are found the same way.

`autofix` is a bulk path through the same gate, not an exception to it: every
substitution it applies is an applied edit and owes its entry, and `autofix.md`
is the procedure for finding and applying them, not the whole of what the mode
owes.

Record every applied edit in `<srd>.decisions.md` — the author-facing account
of what changed and why, which a diff cannot carry. `edit` owns the file; no
other skill writes it.

- Write after each applied edit, never batched to session end: a session that
  clears mid-flow must lose nothing.
- Accumulate: one file per SRD, `##` blocks newest first, each headed
  `## <YYYY-MM-DD> <HH:MM>` — the local time of its first entry, read from the
  clock (`date '+%Y-%m-%d %H:%M'`); with no clock, the date alone. Open a block
  at the session's first applied edit and at the first applied edit after a
  `summary` run; every other entry joins the newest block. Never rewrite or
  prune an earlier block; a date-only heading stays as found.
- One `###` heading per section per block: a later entry for a section this
  block already wrote under appends to it, it never opens a second one. A new
  `###` heading only for a section the block has not touched yet.
  Incremental writing is what makes this explicit — the entries arrive one at a
  time, and the block they join is the one already on the page.
- Record the entry/id, the change in prose (not a diff), and the reason,
  quoted verbatim: the user's words when they gave a reason, else the
  proposal's one-line rationale when it stood unamended (a bare `Y`). Quote,
  never paraphrase — a paraphrase is where invented reasons got in. Keep the
  source's own case and wording ("one rule per", never "One rule per"):
  compare against it before writing. Trim only
  the conversational frame around the quote (`yes, because`) and the
  interaction text a rationale carries — keystroke hints (`` `E` to give a
  different limit ``) and process notes (`so no corpus lookup`, `read as a
  figure the SRD sets`); keep its typos and shorthand. No quotable reason, no
  reason logged — an `autofix` entry has no proposal, so it logs the user's
  words or nothing, never the review finding's text. Quote the whole
  rationale, never its first sentence alone. A reason that holds a double
  quote is wrapped in single quotes, verbatim — never in double quotes with
  backslash escapes.
- An entry ends with every source line its proposal carried, verbatim, one
  per line — a KB section the change contradicts included: the user approved
  the text knowing where it came from, and the log is where that stays
  traceable. A cut's entry carries none, not even for the KB sections its
  proposal named: those are gaps, listed in the manifest.
- Every applied edit, loop or not: `autofix` logs one entry per substitution,
  Add-to-TODO logs its line. Same changes, same log.
- Skipped and flagged-but-unfixed issues are not logged: they stay in the
  review file, or — with none, since `edit` may not create one — in the closing
  manifest, which then says which were left and why.
- Write for the SRD's author, not a reviewer: name the surface in the SRD's own
  words; cite a rule id only where the user did.
- Create the file on the first write, title included.

## The manifest line

The closing manifest's decision-log line, with the block's real heading:

```
Decision log: <srd>.decisions.md — /edit <srd> summary turns its newest block, ## <date> <HH:MM>, into a chat message
```

Omitted when nothing was applied, since the file does not exist.

## Example

Example of the file after one session — the date, heading, ids, and prose are
illustrative, not boilerplate to copy:

````
# Changes — <Document Title>

## 2026-07-27 14:05

### Replay Timeline

TLM-14 was removed, with its open "retention period to be confirmed" note.
Reason: "retention isnt part of this srd, TLM-13 already covers replay after
a scrub".

TLM-9 now names the frame rate in frames per second instead of "high
resolution".
Reason: "Names a measurable value in place of an untestable adjective."
Source: Downlink Frame Format › Frame rate (rank 6, 1 = most trusted) — https://wiki.example.com/pages/1000000112

### General

The British spellings in the Introduction were changed to US English.
````

The second Replay Timeline entry was written later in the same block and joined
the heading already there; General is a second heading because the block had
not written under it before.
