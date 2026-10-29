---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{"id":"gap-0050","status":"filled","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"scrub-refunds","doc_id":"kb/scrub-refunds.md","heading_path":["Scrub refunds","Customer scrub refund"],"search_terms":["customer scrub refund"],"hits":1,"created":"2026-09-20T11:00:00Z","filled_by":[{"ref":"kb/scrub-refunds.md#customer-scrub-refund","hash":"9f2c4e1a7b3d5f60812a4c6e8b0d2f4a6c8e0a2b4d6f8a0c2e4a6b8d0f2a4c6e"}],"topic":"Customer-caused scrub refund","demand":"Blocks the requirements of scrub-refunds that depend on this fact.","detail":"The docs do not say how much of the slot fee a customer-caused scrub refunds.","target_claim":"A customer-caused scrub refunds 80% of the slot fee.","file":"gap-0050-customer-caused-scrub-refund.md","stale":true,"stale_refs":[{"ref":"kb/scrub-refunds.md#customer-scrub-refund","reason":"changed"}]}
{"id":"gap-0051","status":"filled","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"scrub-refunds","doc_id":"kb/scrub-refunds.md","heading_path":["Scrub refunds","Refund claim deadline"],"search_terms":["scrub refund claim deadline"],"hits":1,"created":"2026-09-20T11:05:00Z","filled_by":[{"ref":"kb/scrub-refunds.md#refund-claim-deadline","hash":"1b3d5f7092a4c6e8f0b2d4a6c8e0f2b4d6a8c0e2f4b6d8a0c2e4f6b8d0a2c4e6"}],"topic":"Scrub refund claim deadline","demand":"Blocks the requirements of scrub-refunds that depend on this fact.","detail":"The docs do not say whether a scrub refund must be claimed by a deadline.","target_claim":"A scrub refund can be claimed at any time; there is no deadline.","file":"gap-0051-scrub-refund-claim-deadline.md","stale":true,"stale_refs":[{"ref":"kb/scrub-refunds.md#refund-claim-deadline","reason":"changed"}]}
{"id":"gap-0052","status":"filled","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"telemetry-replay","doc_id":"1000000110","heading_path":["Hot-Fire Campaigns","Recordings"],"search_terms":["hot-fire recording cold archive","hot-fire recordings older than 30 days"],"hits":1,"created":"2026-09-08T10:12:00Z","filled_by":[{"ref":"1000000110#recordings","hash":"c4e6a8b0d2f4a6c8e0b2d4f6a8c0e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6"}],"topic":"When hot-fire recordings move to the cold archive","demand":"Blocks the requirements of telemetry-replay that depend on this fact.","detail":"Nowhere states when hot-fire recordings leave fast storage.","target_claim":"Hot-fire recordings older than 30 days move to the cold archive.","file":"gap-0052-when-hot-fire-recordings-move-to-the-cold-archive.md","stale":true,"stale_refs":[{"ref":"1000000110#recordings","reason":"vanished"}]}
{"id":"gap-0055","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"part-kit-tracking","doc_id":"","heading_path":[],"search_terms":["part kit label length"],"hits":1,"created":"2026-09-25T09:00:00Z","filled_by":[],"topic":"Part kit label length limit","demand":"Blocks the requirements of part-kit-tracking that depend on this fact.","detail":"No maximum length for a Part Kit label is documented.","target_claim":"","file":"gap-0055-part-kit-label-length-limit.md"}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it. The corpus sections that resolve right now are
exactly: `kb/scrub-refunds.md#customer-scrub-refund`, `kb/scrub-refunds.md#refund-claim-deadline`, `kb/scrub-refunds.md#provenance`, `1000000110#campaign-plan`, `1000000110#cold-archive` (`docs/engines/hot-fire-campaigns.md` is accepted for
`1000000110` and stored as `1000000110`).

- list_gaps answers {"gaps":[...],"invalid":[]} with the full current record
  of every gap that matches the call's filters: `status` keeps only gaps in
  exactly that status, `srd_ref` keeps only gaps whose srd_ref contains that
  text, `stale: true` keeps only gaps whose record has `stale: true`; an empty
  or missing filter keeps every gap. A `query` keeps only gaps whose topic,
  detail, or search_terms share a word with it, best match first, each with a
  `score` field.
- fill_gap: when any `filled_by` entry is not one of the resolving sections,
  answer `ERROR: invalid: filled_by entry <entry> does not resolve` and change
  nothing. A `filled` gap given `complete` false or missing answers
  `ERROR: invalid: gap <gap_id> is filled; only complete true is accepted`.
  Otherwise replace the gap's filled_by with the entries, each with a fresh
  64-hex `hash`, drop its `stale` and `stale_refs`, set status `filled` when
  `complete` is true (an open gap without it stays open), replace `detail`
  with `remaining` when given, and answer {"ok":true}.
- reopen_gap moves the filled gap named by `gap_id` to status `open`, keeps
  its filled_by, stale, and stale_refs, appends the reason to `detail`, and
  answers {"ok":true}; a gap that is not filled answers
  `ERROR: invalid: gap <gap_id> is not filled`.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` and answers {"ok":true}; wontfix_gap moves an open gap to
  `wontfix` and answers {"ok":true}.
