---
type: agent
---
The gap store holds exactly two gaps:

{"id":"gap-0042","status":"open","kind":"missing","answer":"","srd_ref":"hot-fire-scheduler","doc_id":"kb/_inbox.md","heading_path":["Knowledge base inbox","Hot-fires run only in the daytime test window"],"search_terms":[],"hits":1,"created":"2026-09-26T10:00:00Z","filled_by":[],"topic":"Daytime test window for hot-fires","demand":"","detail":"","target_claim":"Starforge runs a hot-fire at the test site only between 08:00 and 18:00 site time.","file":"gap-0042-daytime-test-window-for-hot-fires.md"}
{"id":"gap-0043","status":"open","kind":"missing","answer":"deferred","srd_ref":"hot-fire-scheduler","doc_id":"kb/_inbox.md","heading_path":["Knowledge base inbox","Hot-fires run only in the daytime test window"],"search_terms":[],"hits":1,"created":"2026-09-26T10:05:00Z","filled_by":[],"topic":"Daytime test window and short ignition checks","demand":"","detail":"Does the daytime-only hot-fire window also apply to short ignition checks on the test stand?","target_claim":"","file":"gap-0043-daytime-test-window-and-short-ignition-checks.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: filled` or
`status: draft` returns {"gaps":[]}), an `srd_ref` filter keeps only gaps whose
srd_ref contains that text, a `query` keeps only gaps whose topic, detail, or
search_terms share a word with it. With no filter, return both gaps.
