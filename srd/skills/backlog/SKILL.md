---
name: backlog
description: >
  Works the open backlog of everything the documentation and the knowledge base
  still owe: questions deferred during SRD work, facts nobody has pinned down,
  and reported gaps, facts the corpus does not supply reliably. Use when asked
  to work the backlog, clear open questions, answer what was deferred, or write
  up and fill reported documentation gaps.
argument-hint: "[all*|deferred|unknowns|gaps|ask [reminders]]"
license: MIT
---

# backlog

## Usage

```
/srd:backlog                counts for all three lists, then you pick one (default)
/srd:backlog deferred       questions someone knows the answer to; closed by asking
/srd:backlog unknowns       things nobody has pinned down; triage, not answering
/srd:backlog gaps           reported gaps; drafts the fix, fills from the corpus
/srd:backlog ask            one paste-ready message per person a deferred gap names
/srd:backlog ask reminders  the same for questions already sent
```

One sitting over the three lists the SRD skills fill as a byproduct, cheap wins
first.

| List        | Says                        | Closed by               |
|-------------|-----------------------------|-------------------------|
| `deferred`  | someone knows; no time then | asking, right now       |
| `unknowns`  | nobody has pinned it down   | deciding or finding out |
| `gaps`      | the corpus falls short      | a corpus section        |

All three are open gaps in the server's store, told apart by `answer`:
`deferred`, `unknown`, or empty for a plain gap. Each closes only when a corpus
section states its fact: a KB topic page or a pulled doc page. A URL, or a
draft not yet pulled, never closes one.

The lists are not interchangeable: a deferred gap closes by asking, an unknown
by a decision or a finding, a plain gap by authorship. Never draft a page for a
fact nobody has given.

Each question to the user on a gap opens with its context: what the SRD needs,
what the corpus says, earlier answers verbatim with who gave them. Text for
others — a draft, a message, a note — stands alone: plain terms, an example,
nothing they cannot open.

## Boundaries

- Role: the consumer end of every backlog — list, triage, extract, close.
- Must not: write any file under the `kb` folder (`srd:kb` owns it; every
  knowledge-base write is delegated there); publish anywhere; author or edit
  an SRD; file new gaps (`srd:report-doc-gap` owns that, the sweep's
  included).
- Depends on: `srd:kb` for every KB write, `srd:report-doc-gap` for the
  sweep's gaps, the server's gap store for all three lists.

## Sources of truth

- [../kb/references/retrieval-authoring.md](../kb/references/retrieval-authoring.md)
  (on-demand: drafting a page in `gaps`) — how to write Markdown the corpus
  chunks and ranks well. `srd:kb` owns it.
- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate every sitting passes first, and the `kb` folder and
  server it names.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: the first corpus lookup) — the server's tools and how to use
  them. `srd:create` owns it.
- [references/ask.md](references/ask.md) (on-demand: `deferred`, `ask`,
  replies pasted) — asking the user, one message per person, when `asked` is
  set, mapping replies.
- [references/gaps.md](references/gaps.md) (on-demand: `gaps`, or filling any
  gap) — cluster, check, grill, write the fix, fill, wontfix, reopen.

## Backends

The lists use the server's gap tools on `mcp__<mcp-server>__`: `list_gaps`
(optional `status`, `srd_ref`, `stale`, `ask`, `asked`, ranked `query`),
`update_gap` (`gap_id` and only the fields that change), `fill_gap`
(`gap_id`, `filled_by`, `complete`, optional `remaining`), `reopen_gap` and
`wontfix_gap` (`gap_id`, `reason`); the read tools `search`, `get_doc`,
`list_docs` come from the same server. One
`list_gaps` with `status: open` feeds all three lists, split by `answer`. An
error from a call is a store that exists and is unwell: report it with its
message and stop; never retry it or work around it. Stop on an error means the
sitting ends there, sweep and re-check included: no later step or list runs.

A gap record carries `id`, `status`, `kind`
(missing/wrong/incomplete/ambiguous), `answer` (deferred/unknown/empty), `ask`
(who can answer, as typed), `asked` (`YYYY-MM-DD` the questions went out),
`topic`, `demand`, `detail`, `target_claim`, `doc_id`, `heading_path`,
`search_terms`, `srd_ref`, `hits` (encounters in SRD work), `created`, and
`filled_by` (`ref`, `hash`); a stale one adds `stale: true` and `stale_refs`
(`ref`, `reason`: `changed`, `vanished`, `unhashed`). Empty
`doc_id`/`heading_path` mean the reporter found nothing relevant. Statuses:
`draft`, `open` (partly filled when `filled_by` is set; `detail` says what
remains), `filled`, `wontfix`. A `draft` is still `srd:report-doc-gap`'s —
never in this backlog.

## Workflow

A list word names one list.
`all`, the default, names none: step 3 shows the counts and waits for a pick.
`ask` runs the gate and step 7 only. A `key=value` that names no control here,
or a word left over once the modes, the target, and any text the skill takes are
read: say it was not recognized, name the ones that exist, and run with the
defaults as if it were absent — unless dropping it would widen what the run
changes; then ask. A target that resolves to nothing: say so and ask — never
guess what to work on. Copy this checklist and tick it off:

- [ ] 0. Pass the gate. Always, before anything below.
- [ ] 1. Sweep abandoned SRDs. Always, any list named (not `ask`).
- [ ] 2. Re-check stale gaps. Always, any list named (not `ask`).
- [ ] 3. Open the sitting: count each list, stop and wait for the user's pick,
      then run that list. Skipped when a list was named.
- [ ] 4. `deferred`: ask, hand the answer to `srd:kb`, fill once a topic page
      states it.
- [ ] 5. `unknowns`: triage, never answer.
- [ ] 6. `gaps`: cluster, check the corpus, grill, write the fix, fill or
      wontfix.
- [ ] 7. `ask`: one message per person; `asked` only on confirmed sends.
- [ ] 8. Answers pasted, any sitting: map, route, fill.

Work one list at a time; a pick names one list, and when it is done offer the
next non-empty one in a line naming only that list — what closed waits for the
closing line. Close each item through its own mechanism, one call per
item.

### 1. Sweep abandoned SRDs

An abandoned SRD is one whose lifecycle field holds the value the SRD standard
gives a document that will not be built: the KB facts it attested are suspect
until someone checks them. Take the field's name and that value from the
standard (`get_doc` on the `srd-standard` identity). A failed call is an error
like any other: report it and stop. A project that names no standard, or a
standard that defines no such value, is a warning: skip the sweep with one line
("sweep skipped: <why>") and go on to step 2.

1. `list_docs`; `get_doc` each SRD under the `initiatives` folder (not its
   working files, such as `.review.md` or `.questions.md`) and read that
   field of its metadata. An SRD whose field is missing or holds a value the
   standard does not list is skipped with one warning line naming the SRD and
   the value.
   Keep the folder of each abandoned one; none, the sweep ends
   silently.
2. `get_doc` each page under the `kb` folder; keep every section whose
   attestation line names an abandoned folder. A page whose `srd_ref` names it
   while no attestation line does is one section: its `#` heading.
3. Per abandoned folder, `list_gaps` with `status: open` and `srd_ref` the
   folder: an open `wrong` gap with the section's `doc_id` and `heading_path`
   already reverts it — skip the section, no hit.
4. Hand each remaining section to `srd:report-doc-gap` as
   [an abandoned SRD's](../report-doc-gap/SKILL.md#a-cut-requirement) gap:
   `doc_id` and `heading_path` the section, `srd_ref` the folder, `detail`
   naming the abandoned SRD and every other SRD the attestation line names.
   The abandoning value is the confirmation: no proposal, no grill; it files
   each open at once. Never edit the section.

The sweep is one clause of the opening counts line, or the reply's first line
when a list was named: `crew-seats abandoned: 2 gaps filed, 1 already open`.
No abandoned SRD, no clause. Its gaps are plain open gaps: count them in
`gaps`.

### 2. Re-check stale gaps

A stale gap cites a section that changed or vanished since the fill, or was
never hashed; the server flags it and never changes its status. End with each
one refreshed or open; only an open gap with no ref left that holds stays
flagged, since `fill_gap` needs one.

1. `list_gaps` with `stale: true`; none, the re-check ends silently.
2. Per gap, `get_doc` each `filled_by` ref's document; for a `vanished` ref,
   `search` the gap's `search_terms` for where the fact moved. Judge each ref
   against the gap's `target_claim`, else its `detail`: does the section still
   state its part of the fact, in any wording?
3. One call per gap; a filled gap's list must resolve in full:
   - Every ref still states it: `fill_gap` with the same `filled_by` —
     `complete: true` refreshes a filled gap, `complete: false` re-hashes an
     open one.
   - A ref vanished and the fact moved: `fill_gap` with the new ref in its
     place, `complete` as above.
   - A filled gap's section no longer states its part: when the other refs
     still state the whole fact, `fill_gap` them, `complete: true`; else
     `reopen_gap`, `reason` what changed; it joins `gaps`.
   - An open gap's section no longer states it: `fill_gap` the refs that
     still hold, `complete: false`, `remaining` adding the lost part; none
     hold: no call, name it in the report as still stale.
4. Unsure whether a section still states the fact: ask the user then, before
   the counts line, one question per gap, quoting the section beside the
   claim; act on the answer as step 3 says. Never refresh on a guess: a
   refresh re-vouches the section.

The re-check is one clause of the opening counts line, or the reply's first
line when a list was named: `stale: 2 refreshed, 1 reopened`. No stale gap,
no clause.

### 3. Open the sitting

State the counts in one line and wait for the user to pick a list, then run it
(step 4, 5, or 6). Lead with `deferred` when it is non-empty: a sitting that
opens with quick closes keeps going. With `deferred` empty, lead with
`unknowns`, then `gaps`. Recommend a list by name only; the counts line is the
one place each count appears. All three empty: say the backlog is clear and
stop.

### 4. deferred

Ask each deferred gap's question, one closed question per turn; an answer goes
to `srd:kb` and clears `answer`; no answer exists makes it an unknown. Read
"deferred" in [references/ask.md](references/ask.md) *(on-demand: working
`deferred`)* and follow it.

### 5. unknowns

Only the user closes an unknown. You may read the corpus, but a hit is
evidence to put in front of them, never a closure. It is either about a
different question or the answer itself, and only they can say which. Bring
the hit, name what it does and does not settle, and let them decide.

For each unknown gap:

- Answered since (a decision was taken, or someone found out): handled as an
  answered deferred gap — the fact goes to `srd:kb`, then `answer: ""`.
- The user confirms a corpus hit states the answer: no `srd:kb` hand-off —
  `fill_gap` on that section per step 6 of
  [references/gaps.md](references/gaps.md); its `answer` needs no reset.
- Still open: confirm and move on. Bump nothing — `hits` tracks encounters
  during SRD work, not reviews.
- Moot (the feature changed, the subject went away): on the user's word,
  `wontfix_gap` with `reason` why, so it is not re-opened.

Never invent an answer to close a gap: an unknown left open is correct; one
closed with a guess is a fact the corpus will serve as truth.

### 6. gaps

Get each gap's fact into a corpus section, then record the section on the gap;
fill only from a section `get_doc` shows. Read
[references/gaps.md](references/gaps.md) *(on-demand: working `gaps`, or
filling any gap)* and follow it.

### 7. ask

Turns the deferred gaps that name someone into one message per person for the
user to send. No sweep, no re-check, no counts line. Read "ask" in
[references/ask.md](references/ask.md) *(on-demand: `ask` only)* and follow it.

### 8. Answers back

Replies the user pastes, in any sitting: map each to its gap on the user's yes,
one outcome per gap. Read "Answers back" in
[references/ask.md](references/ask.md) *(on-demand: replies pasted)* and follow
it.

### Report

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Counts and what closed are enough — never
re-print a drafted page or the gaps just changed.

Name `srd:kb` as the writer whenever a page changed, as a count per delegate:
this skill writes nothing under the `kb` folder. Never say what the answers
were or where they landed, in any shape. Wrong: `srd:kb saved 2 answers
(80% customer-scrub refund, 21-day freeze)`, or "the refund (80%) is now on
`kb/scrub-refunds.md`". Right: `srd:kb: 2 answers`.

"What closed" is said once per sitting, in the closing line — not again as each
list finishes, and not restated in two shapes ("`gap-0010`, `gap-0015`
filled" and "1 cluster closed (2 gaps)"). Name partly
filled gaps apart from filled ones (`gap-0003` partly filled).

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/srd/backlog.md` (pass `~` as is,
the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
