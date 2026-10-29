# ask

The `ask` list's procedure: one paste-ready message per person a deferred gap
names, and `asked` set only on a confirmed send. Read when the run is `ask`.

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
