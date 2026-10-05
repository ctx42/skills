---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{"id":"gap-0061","status":"open","kind":"missing","answer":"deferred","ask":["Anna M","Piotr K"],"asked":"","srd_ref":"wishlist-sharing","doc_id":"","heading_path":[],"search_terms":["wishlist link expiry"],"hits":1,"created":"2026-09-20T10:00:00Z","filled_by":[],"topic":"Shared wishlist link expiry","demand":"Blocks the requirements of wishlist-sharing that depend on this fact.","detail":"Does a shared wishlist link expire, and after how long?","target_claim":"","file":"gap-0061-shared-wishlist-link-expiry.md"}
{"id":"gap-0062","status":"open","kind":"missing","answer":"deferred","ask":["Anna M"],"asked":"2026-09-28","srd_ref":"gift-cards","doc_id":"","heading_path":[],"search_terms":["gift card refund"],"hits":1,"created":"2026-09-21T10:00:00Z","filled_by":[],"topic":"Gift card refund window","demand":"Blocks the requirements of gift-cards that depend on this fact.","detail":"How many days after purchase can a gift card still be refunded?","target_claim":"","file":"gap-0062-gift-card-refund-window.md"}
{"id":"gap-0063","status":"open","kind":"missing","answer":"deferred","ask":[],"asked":"","srd_ref":"wishlist-sharing","doc_id":"","heading_path":[],"search_terms":["wishlist size limit"],"hits":1,"created":"2026-09-22T10:00:00Z","filled_by":[],"topic":"Wishlist size limit","demand":"Blocks the requirements of wishlist-sharing that depend on this fact.","detail":"How many titles can one wishlist hold?","target_claim":"","file":"gap-0063-wishlist-size-limit.md"}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- list_gaps answers {"gaps":[...],"invalid":[]} with the full current record
  of every gap that matches all of the call's filters: `status` keeps only
  gaps in exactly that status (no gap above is a `draft`), `srd_ref` keeps
  only gaps whose srd_ref contains that text, `stale: true` keeps only gaps
  whose record has `stale: true` (none above), `ask` keeps only gaps with a
  name in `ask` containing that text ignoring case, `asked: true` keeps only
  gaps whose `asked` is non-empty and `asked: false` only those whose `asked`
  is empty; an empty or missing filter keeps every gap. A `query` keeps only
  gaps whose topic, detail, or search_terms share a word with it, best match
  first, each with a `score` field.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (`ask` replaces the list; `asked` must be a YYYY-MM-DD date or
  empty, else answer `ERROR: invalid: asked must be YYYY-MM-DD`) and answers
  {"ok":true}.
