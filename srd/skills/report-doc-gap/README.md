# report-doc-gap

Producer end of the SRD documentation-gap loop: turns a fact SRD work needs but
cannot confirm against the corpus into a curated `report_gap` record. `create`,
`edit`, `review`, and `system-check` delegate **all** gap handling here — it
captures each gap to a per-SRD buffer, grills the finder for context at a chosen
depth, and files it only on confirmation. `resolve-doc-gaps` is the consumer
that later closes what this files.

You rarely invoke it directly — the four SRD skills call it for you. Invoke it
yourself to drain an SRD's pending-gap buffer.

## Usage

```
/report-doc-gap <srd>   drain <srd>'s buffered doc gaps: grill, confirm, file each (default)
```

## When to Use

- An SRD skill hit a corpus gap it cannot confirm a claim against — delegated
  automatically, no direct call needed.
- To drain the pending-gap buffer for an SRD before moving on.
- **Not** for SRD defects (missing owners, undefined terms, logical holes):
  those stay in the caller's own findings. Only documentation-corpus
  deficiencies — missing, wrong, incomplete, or ambiguous docs — belong here.

## How It Works

- **Capture** — on discovery a caller hands over a gap; it writes a light record
  to a per-SRD buffer at
  `$HOME/.agent-data/ctx42-skills/srd/docgaps/<srd-id>.json` and returns without
  interrupting the caller's flow.
- **Drain** — on skill start and at each flow checkpoint, surfaces the SRD's
  pending gaps (count and topics) and offers to work them now.
- **Grill** — per gap the finder picks depth: **light** (confirm or sharpen the
  one-line `detail`) or **heavy** (a full `craft:grill-me` extraction); or opts
  out to a single `detail` line.
- **Confirm and file** — shows the assembled record and files via
  `mcp__srd-doc__report_gap` (or the `POST /gaps` REST mirror) **only on the
  finder's yes**, recording the returned `gap-NNNN`. The record leaves the
  buffer on filing or discard. No store configured → it says so and keeps the
  gap buffered.

## Related Skills

- `resolve-doc-gaps` — consumer that clusters filed gaps and drafts the docs.
- `create`, `edit`, `review`, `system-check` — the callers that delegate gaps
  here.

## Evaluations

**Scenario 1 — Capture on discovery does not interrupt.**
Request: `review` finds the SRD claims "the gateway retries 3×" but no corpus
doc states a retry count.
- Writes a light record (`detail`, `srd_ref`, and the `search_terms` from the
  failed lookups) to the buffer and returns at once.
- Runs no grill, makes no `report_gap` call, and prompts the user for nothing at
  capture time.

**Scenario 2 — Drain, grill, confirm, file.**
Request: `/report-doc-gap specs/gateway.md` with two gaps buffered for that SRD.
- Surfaces the count and topics and offers to work them now.
- Per gap asks light/heavy, assembles the record, shows it, and files via
  `report_gap` **only on yes** — recording the returned `gap-NNNN` and dropping
  the record from the buffer.

**Scenario 3 — An SRD gap is refused.**
Request: a caller hands over "the SRD's §4 has no owner list."
- Recognizes this as an SRD gap, not a documentation gap; does not buffer or
  file it, and tells the caller to keep it in their own findings.

**Scenario 4 — Terse output when no store is configured.**
Request: drain a buffer where neither `report_gap` nor `POST /gaps` exists.
- States filing is unavailable, notes the gap in output, and leaves it buffered
  — no preamble, each fact once, no closing restatement of what was shown.
