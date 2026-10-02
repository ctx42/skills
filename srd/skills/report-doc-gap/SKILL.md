---
name: report-doc-gap
description: >
  Files documentation gaps found during SRD work: a fact the SRD needs that the
  platform documentation cannot confirm because it is missing, wrong,
  incomplete, or ambiguous. Use when an SRD skill cannot confirm a claim
  against the corpus, when a doc gap should reach the documentation backlog,
  or to work an SRD's unreported doc gaps.
argument-hint: "[<srd path>]"
license: MIT
---

# report-doc-gap

## Usage

```
/report-doc-gap <srd>  work <srd>'s draft doc gaps: grill, confirm, file each (default)
```

Rarely invoked by hand: `create`, `edit`, `review`, and `system-check` delegate
every gap here, and `backlog` later closes what this files. Invoke it yourself
to work one SRD's draft gaps before moving on.

Producer end of the doc-gap loop: this skill owns capture, the grill, and the
filing; the caller owns only its primary flow. A captured gap is a server-side
**draft** until filed — nothing is kept on this machine.

## Boundaries

- Role: the single producer-side gap handler. Capture a gap as a draft the
  moment a caller finds one, grill the finder for context, file it on their
  yes.
- Must not: file silently (every record is confirmed first; the backlog is
  human-curated, so noise is the enemy); author or edit the corpus; draft the
  fix (that is `srd:backlog`); file an SRD gap (see
  [The boundary](#the-doc-gap-vs-srd-gap-boundary)); file an unknown, a fact
  nobody has pinned down, which belongs in the knowledge base's open-questions
  list through `srd:kb`.
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

Only documentation-corpus deficiencies belong here: a fact the SRD work needs
cannot be confirmed against the corpus because the content is missing, wrong,
incomplete, or ambiguous. An SRD gap (unmet `STR-*`/`STA-*` rules, undefined
terms, missing owners, logical holes in the document under work) stays in the
caller's own findings:

- "The SRD's §4 has no owner list": SRD gap; the caller reports it.
- "The SRD claims the gateway retries 3×, but no corpus doc states the retry
  count": doc gap; hand it here.

When unsure, ask whether the deficiency is in the SRD or in the docs; only the
latter becomes a draft. A fact the corpus lacks but the user confirms is also
tribal knowledge for `srd:kb`: one fact may be both, and the caller sends it to
both.

## The gap tools

All on `mcp__<mcp-server>__`, from `project-config.md`:

| Step           | Call                                                       |
|----------------|------------------------------------------------------------|
| capture        | `report_gap` with `draft: true` and `srd_ref` → draft `id` |
| grill / refine | `update_gap` on the draft's descriptive fields             |
| file           | `submit_gap` → status `open`                               |
| drop           | `discard_gap` (deletes the draft)                          |
| drain / resume | `list_gaps` with `status: draft`, `srd_ref: <srd>`         |

Only a draft is editable or discardable; a submitted gap is permanent, so
`report_gap` without `draft: true` is never called. An error from a call is a
working store with a problem: report it, never retry or work around it.

## The gap record

The finder or this skill fills these; the store assigns `id`, `status`,
`created_at`. Fill enough that a later person plus agent can write the article
without this session:

- `kind` — `missing` (nothing found), `wrong`, `incomplete`, or `ambiguous`.
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
- `doc_id`, `heading_path`, `source_url` — copied verbatim from the
  `search`/`get_doc` hit the gap is about; all empty when nothing relevant was
  found.
- `search_terms` — the queries tried, so a reviewer can tell genuinely absent
  content from content that exists but does not rank.
- `srd_ref` — the SRD's path from the project root (e.g.
  `initiatives/gateway/srd.md`). One gap blocking two SRDs lists both,
  comma-separated. Empty only while a `create` interview has no path yet; set
  it with `update_gap` once the path exists. Never invent an id.

## Invocation

The first token is the SRD path; callers pass it. A gap handed over in the
invocation prose means capture (phase B); otherwise drain (phase A). With no
arguments, ask which SRD.

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
no grill, no filing. Fill only what is free now: `detail` (the caller's
one-line "what is missing") plus whatever the caller already holds (`kind`,
`topic`, `demand`, `srd_ref`, and the `doc_id`/`heading_path`/`source_url`/
`search_terms` from the lookups that exposed the gap). `demand` belongs here
because the caller knows it now — it is what they were doing when the gap
surfaced — and nobody can reconstruct it later; that is what makes it survive
an opt-out. Leave the rest empty. Keep the returned draft `id` for the session.

One record per distinct missing fact. Same fact means the same thing is missing
from the documentation — same `topic`, and a `detail` that would be closed by
the same page — not the same requirement, the same SRD, or the same search
terms. Two SRDs needing the retry count is one gap found twice. One SRD needing
the retry count and the timeout is one gap when a single page on the gateway's
resend behavior would state both, and two when they belong to different pages —
the page is the test, not the count of facts. Two facts a backlog author would
write in one sitting are one gap; a reviewer reading two records that resolve
together learns nothing the first did not say.

Before capturing, check every draft (`list_gaps`, `status: draft`, no `srd_ref`
filter — another SRD's draft may hold the same fact): if it is already a
draft, merge into it with `update_gap` rather than
duplicate: union `search_terms`, keep the richer `detail` and `target_claim`,
keep the earliest `demand` and add the new one if it differs, each in the words
its capture recorded — the merge writes no sentence of its own — keep the
existing `kind` unless the new capture is strictly more specific (`missing`
yielding to `wrong` or `ambiguous`, never the reverse — the second finder saw
the same absence, not a different one), append to `srd_ref` comma-separated
since one gap can block two SRDs, and keep the `doc_id`/`heading_path`/
`source_url` already set — a later capture that found nothing must not blank a
pointer an earlier one recorded. Repeats are a priority signal the reviewer
reads, not new gaps.

### C. Grill at chosen depth

Ask the finder how deep to go, light or heavy, or [opt out](#opt-out). Depth is
theirs per gap: some gaps deserve a full extraction, others a one-liner.

- Light: confirm or sharpen the one-line `detail`; set `target_claim` when the
  fact is already obvious. No interview.
- Heavy: invoke `craft:grill-me` on the gap to pull out an article's worth of
  knowledge (the `target_claim` confirmed or corrected, the context a reader
  needs, terms and synonyms) and fold it into `detail` and `target_claim` as
  prose; the schema does not change.

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
and re-show; on a no, `discard_gap`.

A discard is a decision, not a deletion: say what was dropped, and record the
topic in the caller's output — in this skill's own reply when the user invoked
it directly — so the same weak lookup does not re-capture the same gap next
session and put the finder through it again. Nothing durable is written for it
— a rejected gap is not a gap — but the finder should not have to remember
rejecting it.

On yes, `submit_gap` and record the gap's `id` (`gap-NNNN`) in your report.
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