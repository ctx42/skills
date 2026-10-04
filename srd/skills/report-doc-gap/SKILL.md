---
name: report-doc-gap
description: >
  Files documentation gaps found during SRD work: a fact the SRD needs that the
  corpus (pulled docs or the knowledge base) does not supply reliably because
  it is missing, wrong, incomplete, or ambiguous. Use when an SRD skill cannot
  confirm a claim against the corpus, when a doc gap should reach the
  documentation backlog, or to work an SRD's unreported doc gaps.
argument-hint: "[<srd path>]"
license: MIT
---

# report-doc-gap

## Usage

```
/report-doc-gap <srd>  work <srd>'s draft doc gaps: grill, confirm, file each (default)
```

Rarely invoked by hand: `create`, `edit`, `doc-edit`, `review`, and
`system-check` delegate every gap here, and `backlog` later fills what this
files. Invoke it yourself
to work one SRD's draft gaps before moving on.

Producer end of the doc-gap loop: this skill owns capture, the grill, and the
filing; the caller owns only its primary flow. A captured gap is a server-side
**draft** until filed — nothing is kept on this machine.

## Boundaries

- Role: the single producer-side gap handler. Capture a gap as a draft the
  moment a caller finds one, grill the finder for context, file it on their
  yes.
- Must not: file silently (every record is confirmed first — in phase D, or
  for [a cut requirement](#a-cut-requirement) by the caller's proposal or a
  `REJECTED` Status; the
  backlog is human-curated, so noise is the enemy); author or edit the
  corpus; draft the fix, fill a gap, or close it as wontfix (that is
  `srd:backlog`); file an SRD gap (see
  [The boundary](#the-doc-gap-vs-srd-gap-boundary)).
- Depends on: the gap tools of the server named in `project-config.md`, which
  the gate in
  [../create/references/project-config.md](../create/references/project-config.md)
  checks before anything else.

## Support files

- [../create/references/project-config.md](../create/references/project-config.md)
  (eager) — the gate, and the server and project root it names.
- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: when unsure whether a handed-over item is a doc gap, tribal
  knowledge for `srd:kb`, or both) — the shared corpus reference; its "Where a
  lookup's outcome goes" section is the caller-side contract this skill serves.

## The doc-gap vs SRD-gap boundary

Only corpus deficiencies belong here: a fact the SRD work needs that pulled docs
or the `kb` folder do not supply reliably — missing, wrong, incomplete, or
ambiguous. A gap closes only when a corpus section (a KB topic page or a pulled
doc page) states the fact, never on a URL. An SRD gap (unmet `STR-*`/`STA-*`
rules, undefined terms, missing owners, logical holes in the document under
work) stays in the caller's own findings:

- "The SRD's §4 has no owner list": SRD gap; the caller reports it.
- "The SRD claims the gateway retries 3×, but no corpus doc states the retry
  count": doc gap; hand it here.

When unsure, ask whether the deficiency is in the SRD or in the docs; only the
latter becomes a draft. A fact the corpus lacks but the user confirms is also
tribal knowledge for `srd:kb`: one fact may be both, and the caller sends it to
both — invoked directly, this skill hands a fact the grill confirmed to
`srd:kb` itself.

A platform question SRD work leaves open is a gap too, marked by `answer`:
`deferred` when someone knows but was not asked (the user waved it off, or it
is the agent's own unconfirmed guess), `unknown` when nobody has pinned it
down. Both are filed here, never written to the KB.

## The gap tools

All on `mcp__<mcp-server>__`, from `project-config.md`:

| Step           | Call                                                                     |
|----------------|--------------------------------------------------------------------------|
| dedup          | `list_gaps` with `query` (topic and detail words), no filter             |
| capture        | `report_gap` with `draft: true` and `srd_ref` → draft `id`               |
| repeat         | `update_gap` with `add_hit: true` on the matching draft or open gap      |
| grill / refine | `update_gap` with only the fields that change                            |
| file           | `submit_gap` → status `open`                                             |
| reopen         | `reopen_gap` with `reason`, on a filled gap whose sections lack the fact |
| drop           | `discard_gap` (deletes the draft)                                        |
| drain / resume | `list_gaps` with `status: draft`, `srd_ref` the SRD reference            |

Only a draft is discardable; draft and open gaps are editable, filled and
wontfix ones are not. Every new record starts as a draft: `report_gap` without
`draft: true` is never called. An error from a call is a working store with a
problem: report it, never retry or work around it.

## The gap record

The finder or this skill fills these; the store assigns `id`, `status`, `hits`,
`created`, and `filled_by`. Fill enough that a later person plus agent can
write the corpus section without this session:

- `kind` — `missing` (nothing found), `wrong`, `incomplete`, or `ambiguous`.
- `answer` — `deferred` or `unknown` for an open question (see
  [The boundary](#the-doc-gap-vs-srd-gap-boundary)), its wording in `detail`;
  omitted for a plain doc gap. A repeat that learns the `answer` was wrong
  changes it with `update_gap`.
- `topic` — short label for the missing knowledge.
- `demand` — why the gap blocks the SRD work at hand, including the SRD section
  that raised it. The capturing skill fills this at capture, from what it was
  doing when the gap surfaced, so it survives an opt-out: the finder declining
  the grill does not make the blocking reason unknown.
- `detail` — what is missing, wrong, incomplete, or ambiguous. Required: the
  one field a finder must supply even on opt-out. May carry grilled prose in
  heavy mode.
- `target_claim` — the specific fact the docs should state, when known. Empty
  on opt-out.
- `doc_id`, `heading_path` — the `id` and heading trail of the
  `search`/`get_doc` hit the gap is about, copied verbatim — the `id`, never
  the `path`, even when they differ; both empty when nothing relevant was
  found.
- `search_terms` — the queries tried, so a reviewer can tell genuinely absent
  content from content that exists but does not rank.
- `srd_ref` — the SRD reference: its folder name under `initiatives`
  (`int384-hydrophone`), per the gate reference. One gap blocking two SRDs
  lists both, comma-separated. Empty only between a `create` gap's capture and
  the branch restatement that agrees the path; set it with `update_gap` then.
  Never invent an id.

## Invocation

The first token is the SRD path; callers pass it. `srd:doc-edit` passes the
path of the document it edits instead, which is then the `srd_ref` of its gaps
unless an SRD needs the fact. A gap handed over in the
invocation prose means capture (phase B); otherwise drain (phase A). With no
arguments, ask which SRD. A caller finishing its run may pass its closing
report as `closing: <text>`: open the end-of-pass offer with that text
verbatim, so the caller's report and the offer reach the user as one message.

## Workflow

Run the gate first. Callers invoke this skill at start (drain, only when their
draft check found drafts) and on gap discovery (capture); the user invokes it
directly to drain.

- [ ] A. On start: list this SRD's drafts; offer to work them.
      "Start" means the caller's session start, not every entry into this
      skill. A capture (phase B) is not a start: it records and returns
      without draining, or the no-interruption rule it exists to serve would
      be broken by the very invocation that serves it.

      There are two moments, not one, and they carry different gaps. At the
      caller's start you surface what a *prior* session left unfiled — work
      the user may have forgotten. When the caller finishes you offer what
      *this* session captured, which they watched accumulate. Same phase C
      and D either way; only the invitation differs.
- [ ] B. On discovery: capture a light draft, no interruption.
- [ ] C. Working a draft: grill the finder at their chosen depth (or honor
      opt-out); write what it yields with `update_gap`.
- [ ] D. Confirm the record; `submit_gap` on yes, `discard_gap` on no.

### A. Drain

`list_gaps` with `status: draft` and `srd_ref` this SRD. Empty: tell the caller
so and show the user nothing — the caller states in its own report that the
drain ran and was empty. Invoked directly by the user, say it in one clause:
there is no caller to say it for you. Otherwise surface count and topics and
offer to work them now: "N unreported doc gaps for
`initiatives/gateway/srd.md`; work them now or keep going?" Never force it; on
defer the drafts stay on the server for the next start. On accept, work them
one at a time through phases C and D.

### B. Capture on discovery

Call `report_gap` with `draft: true` at once and return: no user interruption,
no grill, no filing. Fill only what is free now: `detail` (the caller's one-line
"what is missing") plus whatever the caller already holds (`kind`, `topic`,
`demand`, `srd_ref`, and the `doc_id`/`heading_path`/`search_terms` from the
lookups that exposed the gap). `demand` belongs here because the caller knows it
now — it is what they were doing when the gap surfaced — and nobody can
reconstruct it later; that is what makes it survive an opt-out. Leave the rest
empty. Keep the returned draft `id` for the session.

One record per distinct missing fact. Same fact means the same thing is missing
from the documentation — same `topic`, and a `detail` that would be closed by
the same page — not the same requirement, the same SRD, or the same search
terms. Two SRDs needing the retry count is one gap found twice. One SRD needing
the retry count and the timeout is one gap when a single page on the gateway's
resend behavior would state both, and two when they belong to different pages —
the page is the test, not the count of facts. Two facts a backlog author would
write in one sitting are one gap; a reviewer reading two records that resolve
together learns nothing the first did not say.

Before capturing, run `list_gaps` with `query` the topic and detail words, no
`status` or `srd_ref` filter — another SRD's gap may hold the same fact. Judge
the top-scored results by the same-fact test; the score only ranks. On a match:

- `draft`: merge into it with `update_gap` rather than duplicate, with
  `add_hit: true`: union `search_terms`, keep the richer `detail` and
  `target_claim`, keep the earliest `demand` and add the new one on its own
  line if it differs, each in the words its capture recorded — the merge writes
  no sentence of its own — keep the existing `kind` unless the new capture is
  strictly more specific (`missing` yielding to `wrong` or `ambiguous`, never
  the reverse — the second finder saw the same absence, not a different one),
  append to `srd_ref` comma-separated since one gap can block two SRDs, and
  keep the `doc_id`/`heading_path` already set — a later capture that found
  nothing must not blank a pointer an earlier one recorded.
- `open`: `update_gap` with `add_hit: true`, appending this SRD to `srd_ref`
  and new queries to `search_terms`, `kind` changing only as a draft's would;
  tell the caller the gap's id. A partly filled one counts too: its `detail`
  says what remains.
- `filled`: `get_doc` its `filled_by` sections. Stating the fact, there is no
  gap: hand the caller the citation. Not stating it, capture a draft whose
  `detail` opens `Reopens gap-NNNN:` and says what the sections lack; phase D
  turns it into a reopen.
- `wontfix`: the corpus will not carry it by decision; tell the caller the id
  and the reason in its `detail`. A fact the user confirms still goes to
  `srd:kb` through the caller.

Repeats are a priority signal the reviewer reads, not new gaps.

#### A cut requirement

A KB section left behind by a cut requirement (or an abandoned SRD) arrives
confirmed: by the user's key on the caller's proposal naming the gap, or, from
`srd:backlog`'s sweep, by the SRD's `REJECTED` Status. Per section, dedup as
above, then file at once — no grill, no phase D: an `open` match takes its hit
as above; a `draft` match is merged, then `submit_gap`; a `filled` match is
`reopen_gap` at once, `reason` the cut requirement or the rejected SRD — the
handover is the confirmation — then takes the `open` repeat as above; a
`wontfix` match only returns its id; no match is `report_gap` with `draft:
true`, `kind: wrong`, `doc_id` and `heading_path` the section, `srd_ref` the
SRD, `detail` naming the cut requirement (or the rejected SRD) and every other
SRD attesting the section, then `submit_gap`. Return each id to the caller.

### C. Grill at chosen depth

Ask the finder how deep to go, light or heavy, or [opt out](#opt-out). Depth is
theirs per gap: some gaps deserve a full extraction, others a one-liner.

- Light: confirm or sharpen the one-line `detail`; set `target_claim` when the
  fact is already obvious. No interview.
- Heavy: invoke `craft:grill-me` on the gap to pull out an article's worth of
  knowledge (the `target_claim` confirmed or corrected, the context a reader
  needs, terms and synonyms) and fold it into `detail` and `target_claim` as
  prose; the schema does not change.

An `answer` draft gets no grill: show it in phase D, and an answer the finder
gives now is a fact for `srd:kb`, not a gap — hand it there and `discard_gap`
the draft.

Write what the grill yields to the draft with `update_gap` before phase D, so a
session that clears mid-flow loses nothing. This grill is a head start for
`srd:backlog`, which runs its own authoring grill when the page is written, not
a substitute for it.

#### Opt-out

The floor is one field, `detail`: one line of what is missing; never file
without it. Everything else is auto-filled (`srd_ref`, the corpus-lookup
fields, `kind`, `topic`) or left empty; `target_claim` stays empty for the
backlog author. Two granularities: this gap ("skip the questions, just take
what's missing") and this session (stop grilling for every remaining gap, one
line each). Opt-out drops extraction depth only; the confirm gate in phase D
still applies to every record.

### D. Confirm and file

Show the finder the assembled record and file only on their yes. Ask so that
all three answers are on offer — file it, change something first, or drop it —
rather than a bare "File it?", which reads as yes-or-no and buries the
correction path the next two sentences depend on. On a correction, `update_gap`
and re-show the whole record; on a no, `discard_gap`.

A discard is a decision, not a deletion: say what was dropped, and record the
topic in the caller's output — in this skill's own reply when the user invoked
it directly — so the same weak lookup does not re-capture the same gap next
session and put the finder through it again. Nothing durable is written for it
— a rejected gap is not a gap — but the finder should not have to remember
rejecting it.

On yes, `submit_gap` and record the gap's `id` (`gap-NNNN`) in your report. A
`Reopens gap-NNNN:` draft is shown as that reopen: on yes, `reopen_gap` on
`gap-NNNN` with the draft's `detail` as `reason`, then the `open` repeat on it
(phase B), then `discard_gap` the draft.
Filing only records the gap; the corpus is unchanged, and the gap sits `open`
for `srd:backlog`.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/srd/report-doc-gap.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.