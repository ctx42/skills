---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{"id":"gap-0042","status":"open","kind":"missing","answer":"deferred","ask":[],"asked":"","srd_ref":"session 2026-09-12","doc_id":"kb/logger-battery.md","heading_path":["Logger battery","Battery reporting"],"search_terms":["altecno battery low threshold"],"hits":1,"created":"2026-09-12T15:30:00Z","filled_by":[],"topic":"ALTECNO logger default battery-low threshold","demand":"Blocks the requirements of session 2026-09-12 that depend on this fact.","detail":"What battery-low threshold does an ALTECNO logger use by default?","target_claim":"","file":"gap-0042-altecno-logger-default-battery-low-threshold.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: filled` or
`status: draft` returns {"gaps":[]} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text, a `stale:
true` filter keeps only gaps whose record has `stale: true` (none above
unless shown), a `query` keeps only gaps whose topic, detail, or search_terms
share a word with it, best match first, each with a `score` field. With no
filter, return every gap above.
