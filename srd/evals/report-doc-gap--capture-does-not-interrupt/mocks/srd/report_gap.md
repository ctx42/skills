---
type: agent
---
The documentation-gap store of the srd server. At the start of this run the store holds no gaps at all.

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers {"gap_id":"<new id>"}.
- update_gap changes only the fields given on the draft or open gap named by
  `gap_id` (a field left out keeps its value; `add_hit` true adds 1 to
  `hits`) and answers {"ok":true}. A gap_id the store does not hold, or one
  in status `filled` or `wontfix`, answers
  `ERROR: gap <gap_id> is not an editable draft or open gap`.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {"ok":true}; a gap_id that is not a draft answers
  `ERROR: gap <gap_id> is not a draft`.
- discard_gap deletes the draft named by `gap_id` and answers
  {"ok":true}; same error rule as submit_gap.
- reopen_gap moves the filled gap named by `gap_id` to status `open`,
  appending `reason` to its detail, and answers {"ok":true}; a gap_id that
  is not filled answers `ERROR: gap <gap_id> is not filled`.
- list_gaps answers {"gaps":[...]} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text; an
  empty or missing filter keeps every gap. A `query` keeps only gaps whose
  topic, detail, or search_terms share a word with it, best match first,
  each with a `score` field. No match answers {"gaps":[]}.
