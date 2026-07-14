---
name: report-doc-gap
description: >
  Captures documentation gaps found while authoring or reviewing an SRD and
  files them to an mcp-doc server. The four SRD skills (create, edit, review,
  system-check) delegate here: it buffers each gap, grills the finder for
  context at a user-chosen depth, and files it via report_gap only on
  confirmation. Use when an SRD skill hits a corpus gap it cannot confirm a
  claim against, or to drain the pending-gap buffer for an SRD.
license: MIT
---

# report-doc-gap

Producer end of the doc-gap loop: turn documentation gaps found during SRD work
into curated `report_gap` records. `srd:create`, `srd:edit`, `srd:review`, and
`srd:system-check` delegate **all** gap handling here; `srd:resolve-doc-gaps` is
the consumer that later closes them. This skill owns capture, the buffer, the
grill, and the filing; the calling skill owns only its primary flow.

## Boundaries

- **Role:** the single producer-side gap handler. Capture a gap the moment a
  caller finds one, hold it in a buffer, grill the finder for context, and file
  it on their yes.
- **Must not:** file silently — every record is confirmed first; the backlog is
  human-curated, so noise is the enemy. Never author or edit the corpus, never
  draft the fix (that is `srd:resolve-doc-gaps`), never report an **SRD** gap —
  unmet `STR-*`/`STA-*` rules and logical holes in the document stay in the
  caller's own findings (see [The boundary](#the-doc-gap-vs-srd-gap-boundary)).
- **Depends on:** an `mcp-doc` server with a gap store — the `report_gap` tool
  (or the `POST /gaps` REST mirror). Absent, capture still runs but filing
  degrades to noting the gap in output (see [Confirm and file](#confirm-and-file)).

## The gap channel

Reach `report_gap` by, in priority order:

1. **MCP** — `report_gap` with the record below, e.g. `mcp__<name>__report_gap`;
   returns the assigned `id` (`gap-NNNN`). Preferred. The read tools `search`,
   `get_doc`, `list_docs` come from the same server — the caller uses them to
   decide a claim is unconfirmable before handing the gap here.
2. **REST mirror** — same server when MCP is not wired into this client:
   `POST /gaps` with the record as a JSON body.

Fall through only when a step genuinely is not there, not on one failed call.
If neither exists, the store is not enabled — capture to the buffer, but say
filing is unavailable and stop before `report_gap`.

## The gap record

The finder or this skill fills these; the store assigns `id`, `status`,
`created_at`. Fill enough that a later person plus agent can write the article
without this session:

- `kind` — `missing` (nothing found), `wrong`, `incomplete`, or `ambiguous`.
- `topic` — short label for the missing knowledge.
- `demand` — why the gap blocks the SRD work at hand.
- `detail` — what is missing, wrong, incomplete, or ambiguous. **Required** —
  the one field a finder must supply even on opt-out. May carry grilled prose
  in heavy mode.
- `target_claim` — the specific fact the docs should state, when known. Empty
  on opt-out.
- `doc_id`, `heading_path`, `source_url` — copied **verbatim** from the
  `search`/`get_doc` hit the gap is about; all empty when nothing relevant was
  found.
- `search_terms` — the queries tried, so a reviewer can tell genuinely absent
  content from content that exists but does not rank.
- `srd_ref` — the SRD id and section that raised it (e.g. `SRD-42 §4.3`).

## Workflow

Two entry points. Callers invoke this skill **at start** (drain) and **on gap
discovery** (capture).

- [ ] A. On start: drain the buffer for this SRD — surface pending gaps, offer
      to work them now.
- [ ] B. On discovery: capture the gap light and immediately to the buffer, no
      interruption.
- [ ] C. When working a gap: grill the finder at their chosen depth (or honour
      opt-out), assemble the record.
- [ ] D. Confirm the record, then file via `report_gap`; drop it from the buffer.

Detailed phases follow.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/srd/report-doc-gap.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
