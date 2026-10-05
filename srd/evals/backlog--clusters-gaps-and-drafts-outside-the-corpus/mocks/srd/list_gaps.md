---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{"id":"gap-0021","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"sound-export","doc_id":"1882030917","heading_path":["Storage housekeeping","Cold storage"],"search_terms":["sound file retention","how long are sound files kept","delete sound files"],"hits":1,"created":"2026-09-08T10:12:00Z","filled_by":[],"topic":"How long raw Sound Files are kept","demand":"Blocks the requirements of sound-export that depend on this fact.","detail":"The docs do not say how long a raw Sound File is kept before it is deleted, nor who can change that period.","target_claim":"","file":"gap-0021-how-long-raw-sound-files-are-kept.md"}
{"id":"gap-0027","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"device-map","doc_id":"","heading_path":[],"search_terms":["infobar device without location"],"hits":1,"created":"2026-09-15T14:40:00Z","filled_by":[],"topic":"Infobar for a Device without a location","demand":"Blocks the requirements of device-map that depend on this fact.","detail":"The docs do not say what the Infobar shows for a Device with no location.","target_claim":"","file":"gap-0027-infobar-for-a-device-without-a-location.md"}
{"id":"gap-0034","status":"open","kind":"missing","answer":"","ask":[],"asked":"","srd_ref":"leak-archive","doc_id":"","heading_path":[],"search_terms":["sound file deletion","recording retention period"],"hits":1,"created":"2026-09-22T09:05:00Z","filled_by":[],"topic":"When recorded Sound Files are deleted","demand":"Blocks the requirements of leak-archive that depend on this fact.","detail":"Nowhere states when recorded Sound Files are deleted.","target_claim":"","file":"gap-0034-when-recorded-sound-files-are-deleted.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: filled` or
`status: draft` returns {"gaps":[]} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text, a `stale:
true` filter keeps only gaps whose record has `stale: true` (none above
unless shown), a `query` keeps only gaps whose topic, detail, or search_terms
share a word with it, best match first, each with a `score` field. With no
filter, return every gap above.
