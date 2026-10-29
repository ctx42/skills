---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{"id":"gap-0021","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"hot-fire-scheduler","doc_id":"1000000110","heading_path":["Hot-Fire Campaigns","Recordings"],"search_terms":["hot-fire recording retention","how long are hot-fire recordings kept","delete hot-fire recordings"],"hits":1,"created":"2026-09-08T10:12:00Z","filled_by":[],"topic":"How long hot-fire recordings are kept","demand":"Blocks the requirements of hot-fire-scheduler that depend on this fact.","detail":"The docs do not say how long a hot-fire recording is kept before it is deleted, nor who can change that period.","target_claim":"","file":"gap-0021-how-long-hot-fire-recordings-are-kept.md"}
{"id":"gap-0027","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"bay-calendar","doc_id":"","heading_path":[],"search_terms":["bay map stage without bay"],"hits":1,"created":"2026-09-15T14:40:00Z","filled_by":[],"topic":"Bay Map for a stage without a bay","demand":"Blocks the requirements of bay-calendar that depend on this fact.","detail":"The docs do not say what the Bay Map shows for a stage not yet assigned to a bay.","target_claim":"","file":"gap-0027-bay-map-for-a-stage-without-a-bay.md"}
{"id":"gap-0034","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"telemetry-replay","doc_id":"","heading_path":[],"search_terms":["hot-fire recording deletion","hot-fire recording retention period"],"hits":1,"created":"2026-09-22T09:05:00Z","filled_by":[],"topic":"When hot-fire recordings are deleted","demand":"Blocks the requirements of telemetry-replay that depend on this fact.","detail":"Nowhere states when hot-fire recordings are deleted.","target_claim":"","file":"gap-0034-when-hot-fire-recordings-are-deleted.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: filled` or
`status: draft` returns {"gaps":[]} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text, a `stale:
true` filter keeps only gaps whose record has `stale: true` (none above
unless shown), a `query` keeps only gaps whose topic, detail, or search_terms
share a word with it, best match first, each with a `score` field. With no
filter, return every gap above.
