---
type: agent
---
The documentation-gap store of the srd server. At the start of this run
the store holds exactly these gaps:

{"id":"gap-0061","status":"open","kind":"missing","answer":"deferred","ask":["Maya R","John K"],"asked":"","srd_ref":"part-kit-tracking","doc_id":"","heading_path":[],"search_terms":["part kit expiry"],"hits":1,"created":"2026-09-20T10:00:00Z","filled_by":[],"topic":"Picked part kit expiry","demand":"Blocks the requirements of part-kit-tracking that depend on this fact.","detail":"Does a picked part kit expire when its stage integration slips, and after how long?","target_claim":"","file":"gap-0061-picked-part-kit-expiry.md"}
{"id":"gap-0062","status":"open","kind":"missing","answer":"deferred","ask":["Maya R"],"asked":"2026-09-28","srd_ref":"scrub-refunds","doc_id":"","heading_path":[],"search_terms":["scrub refund payout"],"hits":1,"created":"2026-09-21T10:00:00Z","filled_by":[],"topic":"Scrub refund payout time","demand":"Blocks the requirements of scrub-refunds that depend on this fact.","detail":"How many days after a scrub is the refund paid out?","target_claim":"","file":"gap-0062-scrub-refund-payout-time.md"}
{"id":"gap-0063","status":"open","kind":"missing","answer":"deferred","ask":[],"asked":"","srd_ref":"bay-calendar","doc_id":"","heading_path":[],"search_terms":["bay d ember capacity"],"hits":1,"created":"2026-09-22T10:00:00Z","filled_by":[],"topic":"Bay D Ember capacity","demand":"Blocks the requirements of bay-calendar that depend on this fact.","detail":"How many Ember boosters can Bay D hold at once?","target_claim":"","file":"gap-0063-bay-d-ember-capacity.md"}

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
