---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{"id":"gap-0031","status":"open","kind":"missing","answer":"deferred","srd_ref":"gift-cards","doc_id":"","heading_path":[],"search_terms":[],"hits":1,"created":"2026-09-20T11:00:00Z","filled_by":[],"topic":"Gift card expiry","demand":"Blocks the requirements of gift-cards that depend on this fact.","detail":"Does a gift card expire?","target_claim":"","file":"gap-0031-gift-card-expiry.md"}

{"id":"gap-0035","status":"open","kind":"missing","answer":"","srd_ref":"gift-cards","doc_id":"","heading_path":[],"search_terms":["gift card refund"],"hits":1,"created":"2026-09-21T10:00:00Z","filled_by":[],"topic":"Gift card refund window","demand":"Blocks the requirements of gift-cards that depend on this fact.","detail":"The docs do not say how long a gift card can be refunded.","target_claim":"","file":"gap-0035-gift-card-refund-window.md"}

{"id":"gap-0040","status":"open","kind":"wrong","answer":"","srd_ref":"wishlist-v2","doc_id":"kb/wishlists.md","heading_path":["Wishlists","Wishlist size limit"],"search_terms":["wishlist size limit"],"hits":1,"created":"2026-09-28T09:00:00Z","filled_by":[],"topic":"Wishlist size limit rests on rejected SRD wishlist-v2","demand":"Blocks the requirements of wishlist-v2 that depend on this fact.","detail":"Abandoned SRD wishlist-v2 (REJECTED) attested this section; no other SRD attests it.","target_claim":"","file":"gap-0040-wishlist-size-limit-rests-on-rejected-srd-wishlist-v2.md"}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers {"gap_id":"<new id>"}.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (a field left out keeps its value; `add_hit` true adds 1 to
  `hits`) and answers {"ok":true}.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {"ok":true}; a gap_id that is not a draft answers
  `ERROR: gap <gap_id> is not a draft`.
- reopen_gap moves the filled gap named by `gap_id` to status `open` and
  answers {"ok":true}; a gap_id that is not filled answers
  `ERROR: gap <gap_id> is not filled`.
- list_gaps answers {"gaps":[...]} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text,
  `stale: true` keeps only gaps whose record has `stale: true`; an empty or
  missing filter keeps every gap. A `query` keeps only gaps whose
  topic, detail, or search_terms share a word with it, best match first,
  each with a `score` field. No match answers {"gaps":[]}.
