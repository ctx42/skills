---
name: report-doc-gap
description: >
  Files documentation gaps found during SRD work: a fact the SRD needs that the
  platform documentation cannot confirm because it is missing, wrong,
  incomplete, or ambiguous. Use when an SRD skill cannot confirm a claim
  against the corpus, when a doc gap should reach the documentation backlog,
  or to work an SRD's unreported doc gaps.
argument-hint: "[<srd path or id>]"
license: MIT
---

# report-doc-gap

## Usage

```
/report-doc-gap <srd>  work <srd>'s buffered doc gaps: grill, confirm, file each (default)
```

Rarely invoked by hand: `create`, `edit`, `review`, and `system-check` delegate
every gap here, and `backlog` later closes what this files. Invoke it yourself
to work one SRD's pending gaps before moving on.

Producer end of the doc-gap loop: `srd:create`, `srd:edit`, `srd:review`, and
`srd:system-check` delegate all gap handling here, and `srd:backlog` later
closes what this files. This skill owns capture, the buffer, the grill, and the
filing; the caller owns only its primary flow.

## Boundaries

- Role: the single producer-side gap handler. Capture a gap the moment a caller
  finds one, hold it in a buffer, grill the finder for context, file it on
  their yes.
- Must not: file silently (every record is confirmed first; the backlog is
  human-curated, so noise is the enemy); author or edit the corpus; draft the
  fix (that is `srd:backlog`); file an SRD gap (see
  [The boundary](#the-doc-gap-vs-srd-gap-boundary)); file an unknown, a fact
  nobody has pinned down, which belongs in the knowledge base's open-questions
  list through `srd:kb`.
- Depends on: the `srd-doc` server's gap store, reached through the
  [gap channel](#the-gap-channel). Absent, capture still runs and filing
  degrades as [Confirm and file](#d-confirm-and-file) says.

## Support files

- [../create/references/doc-corpus.md](../create/references/doc-corpus.md)
  (on-demand: when unsure whether a handed-over item is a doc gap, tribal
  knowledge for `srd:kb`, or both) — the shared corpus reference; its "Where a
  lookup's outcome goes" section is the caller-side contract this skill serves.

## The doc-gap vs SRD-gap boundary

Only documentation-corpus deficiencies belong here: a fact the SRD work needs
cannot be confirmed against the corpus because the content is missing, wrong,
incomplete, or ambiguous. An SRD gap (unmet `STR-*`/`STA-*` rules, undefined
terms, missing owners, logical holes in the document under work) stays in the
caller's own findings:

- "The SRD's §4 has no owner list": SRD gap; the caller reports it.
- "The SRD claims the gateway retries 3×, but no corpus doc states the retry
  count": doc gap; hand it here.

When unsure, ask whether the deficiency is in the SRD or in the docs; only the
latter crosses into the buffer. A fact the corpus lacks but the user confirms
is also tribal knowledge for `srd:kb`: one fact may be both, and the caller
sends it to both.

## The gap channel

Reach `report_gap` by, in priority order, falling through only when a step
genuinely is not there, never on one failed call:

1. MCP: `mcp__srd-doc__report_gap` with the record below; returns the assigned
   `id` (`gap-NNNN`). The read tools `mcp__srd-doc__search`, `get_doc`, and
   `list_docs` come from the same server; the caller uses them to decide a
   claim is unconfirmable before handing the gap here.

   The absence of these tools says this client has no MCP wiring, not that the
   server is down — fall through to REST and probe it before reporting no
   channel.
2. REST mirror, when the server runs but MCP is not wired into this client:
   `POST /gaps` with the record as a JSON body.

**Probe with `GET /gaps`, never with `POST`.** The store is production and
append-only: it has no delete, so a probe record is permanent and someone has
to notice it and clean it out of a real backlog by hand. A successful `GET`
proves the route, the host, and the schema — everything a probe is for. This is
not hypothetical: an eval run took "probe it" at its word, sent a `POST` with a
junk body to see whether the endpoint existed, and filed `gap-0025` into the
real store.

Reaching the host at all is the test. A `GET` that answers — with rows, or with
an empty list — means the channel is up. Connection refused or no route means
it is not. An error *from* the store is a working store with a problem: report
it, do not fall past it and do not retry.

Neither present means the store is not enabled;
[Confirm and file](#d-confirm-and-file) says what happens then.

## The gap record

The finder or this skill fills these; the store assigns `id`, `status`,
`created_at`. Fill enough that a later person plus agent can write the article
without this session:

- `kind` — `missing` (nothing found), `wrong`, `incomplete`, or `ambiguous`.
- `topic` — short label for the missing knowledge.
- `demand` — why the gap blocks the SRD work at hand. The capturing skill
  fills this at capture, from what it was doing when the gap surfaced, so it
  survives an opt-out: the finder declining the grill does not make the
  blocking reason unknown, and every record in the store carries one.
- `detail` — what is missing, wrong, incomplete, or ambiguous. Required: the
  one field a finder must supply even on opt-out. May carry grilled prose in
  heavy mode.
- `target_claim` — the specific fact the docs should state, when known. Empty
  on opt-out.
- `doc_id`, `heading_path`, `source_url` — copied verbatim from the
  `search`/`get_doc` hit the gap is about; all empty when nothing relevant was
  found.
- `search_terms` — the queries tried, so a reviewer can tell genuinely absent
  content from content that exists but does not rank.
- `srd_ref` — the SRD id and section that raised it (e.g. `SRD-42 §4.3`).

## The buffer

Captured gaps live in a per-SRD buffer until filed, so a session that clears
mid-flow loses nothing.

- Location:
  `${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/srd/docgaps/<srd-id>.json`
  — `AGENT_DATA_DIR` lets a sandbox or an eval redirect the store, and unset
  means the real one. Outside every corpus source by construction, so cfsync
  never indexes or clobbers it; beside the lessons files.
- Key: the SRD id (e.g. `SRD-42`). All four SRD skills share one buffer per
  SRD id on this machine, so a reviewer's session appends to the file an
  author's session started. Before an id exists, key off the SRD's absolute
  file path — a path is not a filename, so derive one the same way every time:
  `path-` plus the first 12 hex characters of the path's SHA-256
  (`printf %s "$abs" | sha256sum`). Any other transform breaks the shared-file
  promise, since two skills that slugify differently silently keep separate
  buffers for one SRD. Resolve the path to absolute first; a relative path
  keyed from two working directories does the same damage. Rename the file to
  the id once assigned — done by the next capture or drain that finds a
  path-keyed file for an SRD that now has one, since no phase is entered at the
  moment of assignment.
- Contents: a JSON array of [gap records](#the-gap-record), filled as far as
  capture or grill got them. Buffered means unconfirmed: a record leaves on
  filing or discard, and the file is deleted when the last record leaves it. An
  empty `[]` is never a resting state on disk: a file that exists means records
  are pending, so an empty one would have every later drain report a buffer it
  does not have.

## Invocation

The first token is the SRD path or id; callers pass it. A gap handed over in the
invocation prose means capture (phase B); otherwise drain (phase A). With no
arguments, ask which SRD.

## Workflow

Callers invoke this skill at start (drain) and on gap discovery (capture); the
user invokes it directly to drain.

- [ ] A. On start: drain the buffer for this SRD; offer to work pending gaps.
      "Start" means the caller's session start, not every entry into this
      skill. A capture (phase B) is not a start: it records and returns
      without draining, or the no-interruption rule it exists to serve would
      be broken by the very invocation that serves it.

      There are two moments, not one, and they carry different gaps. At the
      caller's start you surface what a *prior* session left unfiled — work
      the user may have forgotten. When the caller finishes you offer what
      *this* session buffered, which they watched accumulate. Same phase C
      and D either way; only the invitation differs.
- [ ] B. On discovery: capture the gap light to the buffer, no interruption.
- [ ] C. Working a gap: check the channel is reachable, then grill the finder
      at their chosen depth (or honor opt-out); assemble the record. Resolve
      the channel first — interviewing someone about a gap that cannot then be
      filed spends their attention for nothing. With no channel, say so, leave
      the gap buffered, and do not open the grill.
- [ ] D. Confirm the record, file via `report_gap`, drop it from the buffer.

### A. Drain

Read this SRD's buffer on skill start (a prior session may have cleared with
gaps unfiled) and on direct invocation. Empty: tell the caller so and show the
user nothing — the caller states in its own report that the drain ran and was
empty. Invoked directly by the user, say it in one clause: there is no caller
to say it for you. Otherwise resolve the channel before offering: with none reachable,
give the count, say filing is unavailable, and do not offer work that cannot
finish. Phase C checks it again for the capture path, which does not come
through here. With a channel, surface count and topics and offer to work them
now: "N
unreported doc gaps for `SRD-42`; work them now or keep going?" Never force it;
on defer the gaps stay buffered for the next start. On accept, work them one at
a time through phases C and D.

### B. Capture on discovery

Write a light record to the buffer at once and return: no user interruption,
no grill, no `report_gap` call. Fill only what is free now: `detail` (the
caller's one-line "what is missing") plus whatever the caller already holds
(`kind`, `topic`, `demand`, `srd_ref`, and the `doc_id`/`heading_path`/
`source_url`/`search_terms` from the lookups that exposed the gap). `demand`
belongs here because the caller knows it now — it is what they were doing when
the gap surfaced — and nobody can reconstruct it later; that is what makes it
survive an opt-out. Leave the rest empty.

One record per distinct missing fact. Same fact means the same thing is missing
from the documentation — same `topic`, and a `detail` that would be closed by
the same page — not the same requirement, the same SRD, or the same search
terms. Two SRDs needing the retry count is one gap found twice. One SRD needing
the retry count and the timeout is one gap when a single page on the gateway's
resend behavior would state both, and two when they belong to different pages —
the page is the test, not the count of facts. Two facts a backlog author would
write in one sitting are one gap; a reviewer reading two records that resolve
together learns nothing the first did not say.

If the same fact is already buffered for this SRD, merge into it rather than
duplicate: union `search_terms`, keep the richer `detail` and `target_claim`,
keep the earliest `demand` and add the new one if it differs, keep the existing
`kind` unless the new capture is strictly more specific (`missing` yielding to
`wrong` or `ambiguous`, never the reverse — the second finder saw the same
absence, not a different one), append to `srd_ref` comma-separated since one
gap can block two SRDs, and keep the `doc_id`/`heading_path`/`source_url`
already set — a later capture
that found nothing must not blank a pointer an earlier one recorded. Repeats
are a priority signal the reviewer reads, not new gaps.

### C. Grill at chosen depth

Ask the finder how deep to go, light or heavy, or [opt out](#opt-out). Depth is
theirs per gap: some gaps deserve a full extraction, others a one-liner.

- Light: confirm or sharpen the one-line `detail`; set `target_claim` when the
  fact is already obvious. No interview.
- Heavy: invoke `craft:grill-me` on the gap to pull out an article's worth of
  knowledge (the `target_claim` confirmed or corrected, the context a reader
  needs, terms and synonyms) and fold it into `detail` and `target_claim` as
  prose; the schema does not change.

This grill is a head start for `srd:backlog`, which runs its own authoring
grill when the page is written, not a substitute for it.

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
correction path the next two sentences depend on. On a correction, adjust and
re-show; on a no, discard. Either outcome removes the
record from the buffer.

A discard is a decision, not a deletion: say what was dropped, and record the
topic in the caller's output — in this skill's own reply when the user invoked
it directly — so the same weak lookup does not re-capture the same gap next
session and put the finder through it again. Nothing durable is
written for it — a rejected gap is not a gap — but the finder should not have
to remember rejecting it.

On yes, file through the [gap channel](#the-gap-channel) and record the
returned `id` (`gap-NNNN`) in your report. Filing only records the gap; the
corpus is unchanged, and the gap sits `open` for `srd:backlog`.

No gap store: say filing is unavailable, note the gap in the caller's output,
and leave it buffered for a session where the store is reachable. Never invent
a store. Say which kind of unavailable it is — no route on a server that
answers, or no server answering at all — because the first is a deployment
that needs the gap endpoint and the second is a host that is simply not up, and
the reader fixes them differently.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md`
and `$HOME/.agent-data/ctx42-skills/lessons/srd/report-doc-gap.md`, the
sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs
have none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.