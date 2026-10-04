---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{"id":"gap-0050","status":"filled","kind":"missing","answer":"","srd_ref":"gift-cards","doc_id":"kb/gift-cards.md","heading_path":["Gift cards","Refund window"],"search_terms":["gift card refund window"],"hits":1,"created":"2026-09-20T11:00:00Z","filled_by":[{"ref":"kb/gift-cards.md#refund-window","hash":"9f2c4e1a7b3d5f60812a4c6e8b0d2f4a6c8e0a2b4d6f8a0c2e4a6b8d0f2a4c6e"}],"topic":"Gift card refund window","demand":"Blocks the requirements of gift-cards that depend on this fact.","detail":"The docs do not say how long a gift card can be refunded.","target_claim":"An unused gift card can be refunded within 14 days of purchase.","file":"gap-0050-gift-card-refund-window.md","stale":true,"stale_refs":[{"ref":"kb/gift-cards.md#refund-window","reason":"changed"}]}
{"id":"gap-0051","status":"filled","kind":"missing","answer":"","srd_ref":"gift-cards","doc_id":"kb/gift-cards.md","heading_path":["Gift cards","Gift card expiry"],"search_terms":["gift card expiry"],"hits":1,"created":"2026-09-20T11:05:00Z","filled_by":[{"ref":"kb/gift-cards.md#gift-card-expiry","hash":"1b3d5f7092a4c6e8f0b2d4a6c8e0f2b4d6a8c0e2f4b6d8a0c2e4f6b8d0a2c4e6"}],"topic":"Gift card expiry","demand":"Blocks the requirements of gift-cards that depend on this fact.","detail":"The docs do not say whether a gift card expires.","target_claim":"A gift card never expires.","file":"gap-0051-gift-card-expiry.md","stale":true,"stale_refs":[{"ref":"kb/gift-cards.md#gift-card-expiry","reason":"changed"}]}
{"id":"gap-0052","status":"filled","kind":"missing","answer":"","srd_ref":"leak-archive","doc_id":"1882030917","heading_path":["Storage housekeeping","Cold storage"],"search_terms":["recording archive tier","recordings older than 90 days"],"hits":1,"created":"2026-09-08T10:12:00Z","filled_by":[{"ref":"1882030917#cold-storage","hash":"c4e6a8b0d2f4a6c8e0b2d4f6a8c0e2b4d6f8a0c2e4b6d8f0a2c4e6b8d0f2a4c6"}],"topic":"When recordings move to the archive tier","demand":"Blocks the requirements of leak-archive that depend on this fact.","detail":"Nowhere states when recordings leave hot storage.","target_claim":"Recordings older than 90 days move to the archive tier.","file":"gap-0052-when-recordings-move-to-the-archive-tier.md","stale":true,"stale_refs":[{"ref":"1882030917#cold-storage","reason":"vanished"}]}
{"id":"gap-0055","status":"open","kind":"missing","answer":"","srd_ref":"tag-import","doc_id":"","heading_path":[],"search_terms":["tag name length"],"hits":1,"created":"2026-09-25T09:00:00Z","filled_by":[],"topic":"Tag name length limit","demand":"Blocks the requirements of tag-import that depend on this fact.","detail":"No maximum length for a Tag node name is documented.","target_claim":"","file":"gap-0055-tag-name-length-limit.md"}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it. The corpus sections that resolve right now are
exactly: `kb/gift-cards.md#refund-window`, `kb/gift-cards.md#gift-card-expiry`, `kb/gift-cards.md#provenance`, `1882030917#nightly-jobs`, `1882030917#archive-tier` (`docs/operations/storage-housekeeping.md` is accepted for
`1882030917` and stored as `1882030917`).

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
