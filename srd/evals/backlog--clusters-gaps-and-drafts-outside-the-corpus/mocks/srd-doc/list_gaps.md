---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{"id":"gap-0021","status":"open","created_at":"2026-09-08T10:12:00Z","kind":"missing","topic":"How long raw Sound Files are kept","doc_id":"confluence/infraport/operations/storage-housekeeping.md","heading_path":["Storage housekeeping","Cold storage"],"source_url":"https://confluence.example.com/infraport/operations/storage-housekeeping#cold-storage","demand":"Blocks the requirements of initiatives/sound-export/srd.md that depend on this fact.","target_claim":"","detail":"The docs do not say how long a raw Sound File is kept before it is deleted, nor who can change that period.","search_terms":["sound file retention","how long are sound files kept","delete sound files"],"srd_ref":"initiatives/sound-export/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0027","status":"open","created_at":"2026-09-15T14:40:00Z","kind":"missing","topic":"Infobar for a Device without a location","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/device-map/srd.md that depend on this fact.","target_claim":"","detail":"The docs do not say what the Infobar shows for a Device with no location.","search_terms":["infobar device without location"],"srd_ref":"initiatives/device-map/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0034","status":"open","created_at":"2026-09-22T09:05:00Z","kind":"missing","topic":"When recorded Sound Files are deleted","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/leak-archive/srd.md that depend on this fact.","target_claim":"","detail":"Nowhere states when recorded Sound Files are deleted.","search_terms":["sound file deletion","recording retention period"],"srd_ref":"initiatives/leak-archive/srd.md","kb_marked_at":null,"kb_entry":null}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: kb` or
`status: draft` returns {"gaps":[]} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text. With no
filter, return every gap above.
