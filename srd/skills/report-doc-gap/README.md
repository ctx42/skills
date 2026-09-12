# report-doc-gap

Files documentation gaps found during SRD work as curated `report_gap` records.

## Usage

```
/report-doc-gap <srd>   work <srd>'s buffered doc gaps: grill, confirm, file each (default)
```

You rarely invoke it directly: `create`, `edit`, `review`, and `system-check`
delegate every gap here, and `backlog` later closes what this files. Invoke it
yourself to work an SRD's pending gaps.

## When to Use

- An SRD skill cannot confirm a claim against the corpus: delegated
  automatically, no direct call needed.
- To work the pending-gap buffer for an SRD before moving on.
- Not for SRD defects (missing owners, undefined terms, logical holes), which
  stay in the caller's own findings, nor for unknowns (facts nobody has pinned
  down), which go to the knowledge base through `kb`. Only documentation-corpus
  deficiencies (missing, wrong, incomplete, or ambiguous docs) belong here.

## How It Works

- Capture: on discovery a caller hands over a gap; it writes a light record to
  a per-SRD buffer at `$HOME/.agent-data/ctx42-skills/srd/docgaps/<srd-id>.json`
  and returns without interrupting the caller's flow. A repeat of a buffered
  fact merges into the existing record.
- Drain: on skill start, surfaces the SRD's pending gaps (count and topics) and
  offers to work them now; on defer they stay buffered.
- Grill: per gap the finder picks depth, light (confirm or sharpen the one-line
  `detail`) or heavy (a full `craft:grill-me` extraction), or opts out to a
  single `detail` line.
- Confirm and file: shows the assembled record and files via
  `mcp__srd-doc__report_gap` (or the `POST /gaps` REST mirror) only on the
  finder's yes, recording the returned `gap-NNNN`. The record leaves the buffer
  on filing or discard. No store configured: it says so and keeps the gap
  buffered.

## Related Skills

- `backlog` — consumer that works the gap backlog and drafts the docs.
- `kb` — takes the knowledge-base side when a fact is both tribal knowledge and
  a doc gap.
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
  `report_gap` only on yes, recording the returned `gap-NNNN` and dropping the
  record from the buffer.
- On "keep going", leaves both gaps buffered and returns to the caller.

**Scenario 3 — An SRD gap is refused.**
Request: a caller hands over "the SRD's §4 has no owner list."
- Recognizes this as an SRD gap, not a documentation gap; does not buffer or
  file it.
- Tells the caller to keep it in their own findings.

**Scenario 4 — Opt-out and duplicate merge.**
Request: a second caller session hands over the retry-count gap already
buffered for `SRD-42`; at drain the finder says "skip the questions".
- Merges into the existing record (wider `search_terms`, richer `detail`)
  instead of adding a duplicate.
- Takes only the one-line `detail`, leaves `target_claim` empty, and still shows
  the record for confirmation before filing.

**Scenario 5 — Terse output when no store is configured.**
Request: drain a buffer where neither `report_gap` nor `POST /gaps` exists.
- States filing is unavailable, notes the gap in output, and leaves it
  buffered.
- No preamble, each fact once, no closing restatement of what was shown.
