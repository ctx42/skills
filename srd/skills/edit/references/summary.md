# summary — the logged changes as a chat message

The procedure for `edit <srd> summary`, read on demand when that mode runs.
Every other mode can ignore this file.

Read-only. It reads the SRD, `<srd>.decisions.md`, and `<srd>.review.md`,
nothing else — no transcript, corpus, or glossary call — and writes no file.
The reply is a message the user pastes into a chat channel whose readers may
not know the review, so every line must read on its own.

## Contents

- Select
- Link findings
- Compose
- Close

## Select

The tokens after `summary` pick the blocks of `<srd>.decisions.md`
([decision-log.md](decision-log.md)):

- none → the newest block.
- `today`, or a date (`2026-10-23`) → every block headed with that date,
  merged.
- a date and a time (`2026-10-23 11:05`) → the one block with that heading.

No decision log, or no block matches: say so in one line and stop.

A block's span runs from its heading's time — the start of the day for a
date-only heading — to the next newer block's heading, or to now for the
newest block.

## Link findings

A finding of `<srd>.review.md` is named only when the selection touched it:

- Resolved, or open with a `*(Partial — …)*` note: it cites an id a selected
  entry changed, and its resolution or partial note describes that entry's
  change. A finding on the same id whose note describes another change — one
  an earlier block made — is not linked.
- Withdrawn: its stamp `(withdrawn <YYYY-MM-DD HH:MM>: …)` falls inside a
  selected block's span. An unstamped withdrawal is never listed.

An open finding with no note is never named. No review file: compose without
numbers.

## Compose

Merge first: a requirement, scope item, or glossary term several selected
decision entries changed is one line stating its end state; one added and
removed within the selection is dropped.
Then classify each line: a change in meaning alters what a rule requires,
permits, or applies to; anything else — subject or voice, a term swap, an
article, spelling, whitespace — is wording. A requirement with a change in
meaning absorbs its own wording edits and their finding numbers.

1. Header: `<SRD title>: changes <date>`, plus ` <HH:MM>` when one block is
   selected; the title is the SRD's front-matter `title`, else its H1.
2. Groups, in document order: each requirement group name — the SRD's own
   group heading — on its own line, then one `- ` line per change in meaning
   to an entry of that group. Glossary, Scope, and Introduction changes take
   groups named after their section.
3. Each line says what the rule now does, in plain words, without the
   decision log's reasons. The linked finding numbers trail it in parentheses,
   `(#104, #111)`, never worded into the sentence: deleting them leaves a
   complete statement.
   - A removed requirement is paraphrased with why, never named by id alone.
   - A split says in a few words what it became.
   - A new glossary term is its name alone.
   - A placeholder appears only inside the line that introduced it ("a
     timeout still to be set").
4. `Withdrawn`: one `- ` line per withdrawn finding, its number then a short
   reason. Omitted when none.
5. `Wording`, last: one `- ` line per kind of wording edit, its ids then its
   numbers — `- Reworded GR-3 and GR-7 with the system as subject (#107,
   #112)`, `- Fixed stray whitespace (#116)`. Omitted when none.

Never: a still-open or status line, a finding the selection did not touch, a
count of edits, Markdown — no `*`, backticks, bold, `#` headings, or code
block; `#` appears only in finding numbers. Group names and the two closing
section names are plain lines.

## Close

The reply is the message alone: no preamble, no closing line, no offer. The
session's next applied edit opens a new decision-log block
([decision-log.md](decision-log.md)), so a later `summary` covers only what
came after this one.
