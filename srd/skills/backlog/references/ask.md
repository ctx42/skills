# ask

Everything the backlog closes by asking: the `deferred` list, the `ask`
messages, and the replies pasted back. Read the section the run reaches.
Fill steps are step 6 of `gaps.md`.

## deferred

Take the deferred gaps one at a time, oldest `created` first. Ask the question
its `detail` words. Ask one closed question per turn, never an either/or a bare
"yes" cannot answer; ask the second half next turn.

- Answered: a numeric rule (threshold, tolerance, its base) first gets asked
  whether code implements it, and that code read — a "yes" to a leading
  question can confirm a wrong base. Hand the fact to `srd:kb` with the
  gap's id, then `update_gap` `answer: ""` — asked and answered, it owes only a
  corpus section now and joins `gaps`. `srd:kb` writes to its inbox, never a
  fill target: offer `/kb file`, and fill as step 6 of `gaps` says once a topic
  page states it.
- "Still not now": leave it; do not re-ask it this sitting.
- The user does not know: "Who would know" in `doc-corpus.md`; names merge
  into `ask` as `srd:report-doc-gap` merges them (a new name clears `asked`),
  with `update_gap`.
- No answer exists: it is an unknown, not a skip — `update_gap` with
  `answer: unknown`, and say so.

## ask

One paste-ready message per person a deferred gap names, and `asked` set only
on a confirmed send. Read when the run is `ask`.

1. `list_gaps` `status: open`, `asked: false`; keep `answer: deferred` gaps
   with a non-empty `ask`. `ask reminders`: `asked: true` instead. Count the
   other kind too, and drafts naming someone (`status: draft`): a draft is
   never asked; it is filed first (`/report-doc-gap <srd>`).
2. Group by person, each name as typed (case-only variants are one person,
   first spelling). A gap naming two people sits in both groups.
3. Per person: the name, then one fenced `text` block ready to paste into a
   chat:
   - One greeting line: `Hi <name>, a few questions for our documentation —
     could you answer when you have a moment?` A reminder says it follows up;
     each of its questions ends with the date it went out (`asked`).
   - A numbered list, oldest `created` first: per gap one self-contained
     plain-language question built from `topic`, `detail`, and
     `target_claim`, then one indented line of context from `demand`.
   - No gap ids, SRD folders, tool or field names in the block; the plain
     name, never an @-mention.

   Under the block, outside it, one mapping line: `1 gap-0042 · 2 gap-0047`.
4. One closing line: the other kind's count (already asked, oldest `asked`
   date, and `/backlog ask reminders`; or not yet asked and `/backlog ask`),
   plus the draft count when non-zero. Nothing to send: say so in that line.
5. Ask which blocks went out. Only on the user's confirmation: `update_gap`
   `asked` today's date on every gap whose blocks all went out, one call per
   gap. Never before, never for a person not confirmed, never on "will send
   later". A gap also in an unsent block stays unasked, so the next `/backlog
   ask` still carries it; say so. A confirmed reminder moves `asked` to today
   as well: it holds the last send.

## Answers back

Replies the user pastes, in any sitting:

1. Map each reply to its gap: by the mapping line when this sitting printed
   it, else `list_gaps` `status: open`, `ask` the sender's name, by content.
   Show the mapping (`Anna M 1 → gap-0042`) and act on the user's yes. A
   reply matching no gap is asked about, never guessed.
2. One outcome per gap; `ask` and `asked` stay as history:
   - Answered: as an answered deferred gap ("deferred" above) — the fact goes
     to `srd:kb`, or through `srd:doc-edit` when the user wants it on a doc
     page; fill as step 6 of `gaps` says once a section states it.
   - Partly answered: the answered part goes the same way; `update_gap`
     `detail` to what is still owed, `answer` stays `deferred`. Once a section
     states the part: `fill_gap` `complete: false`, `remaining` what is still
     owed.
   - "Don't know, ask Y": `update_gap` `ask` the existing names plus Y,
     `asked: ""`.
   - Nobody knows: `update_gap` `answer: unknown`.
