---
type: agent
---
The documentation-gap store of the srd-doc server. At the start of this run the store holds no gaps at all.

Every earlier gap call this run changes the store; always answer from the
store as those calls left it.

- report_gap records a new gap: status `draft` when `draft` is true, else
  `open`. It takes the next unused id in the series gap-0901, gap-0902,
  gap-0903 (never one already issued) and answers
  {"id":"<new id>","status":"<status>"}.
- update_gap replaces the descriptive fields of the draft named by
  `gap_id` with the ones given (a field left out becomes empty) and answers
  {"ok":true,"id":"<gap_id>"}. A gap_id the store does not hold, or one not
  in status `draft`, answers `ERROR: gap <gap_id> is not an editable draft`.
- submit_gap moves the draft named by `gap_id` to status `open` and answers
  {"ok":true,"id":"<gap_id>","status":"open"}; same error rule as update_gap.
- discard_gap deletes the draft named by `gap_id` and answers
  {"ok":true,"id":"<gap_id>"}; same error rule as update_gap.
- list_gaps answers {"gaps":[...]} with the full current record of every
  gap that matches the call's filters: `status` keeps only gaps in exactly
  that status, `srd_ref` keeps only gaps whose srd_ref contains that text; an
  empty or missing filter keeps every gap. No match answers {"gaps":[]}.
