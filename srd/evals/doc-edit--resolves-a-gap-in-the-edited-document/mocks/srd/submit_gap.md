---
type: agent
---
The documentation-gap store of the srd server. At the start of this run the store holds exactly these gaps:

{"id":"gap-0410","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"scrub-refunds","doc_id":"1000000105","heading_path":["Scrub Refunds"],"search_terms":["scrub refund payout deadline"],"hits":2,"created":"2026-09-20T09:00:00Z","filled_by":[],"topic":"Payout deadline for a scrub refund","demand":"REF-3 needs the deadline by which a refund is paid out","detail":"No corpus page states how many working days after a scrub its refund is paid out.","target_claim":"","file":"gap-0410-payout-deadline-for-a-scrub-refund.md"}

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers {"gap_id":"<new id>"}.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (a field left out keeps its value; `add_hit` true adds 1 to
  `hits`) and answers {"ok":true}. Any other gap_id answers
  `ERROR: gap <gap_id> is not an editable draft or open gap`.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {"ok":true}; a gap_id that is not a draft answers
  `ERROR: gap <gap_id> is not a draft`.
- discard_gap deletes the draft named by `gap_id` and answers
  {"ok":true}; same error rule as submit_gap.
- fill_gap on an open gap sets `filled_by` to the given list and, when
  `complete` is true, status `filled`; `remaining` replaces its detail. It
  answers {"ok":true}. An entry whose identity starts with `initiatives/`
  or `http` answers `ERROR: <entry> is not a corpus section outside the
  initiatives folder`; a gap_id that is not open or filled answers
  `ERROR: gap <gap_id> is not open`.
- list_gaps answers {"gaps":[...]} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text; an
  empty or missing filter keeps every gap. A `query` keeps only gaps whose
  topic, detail, or search_terms share a word with it, best match first,
  each with a `score` field. No match answers {"gaps":[]}.
