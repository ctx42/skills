---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{"id":"gap-0051","status":"open","created_at":"2026-09-08T10:12:00Z","kind":"missing","topic":"How long raw Sound Files are kept","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/sound-export/srd.md that depend on this fact.","target_claim":"Raw Sound Files are deleted 400 days after upload.","detail":"Grilled at filing: the user stated raw Sound Files are deleted 400 days after upload, archived or not.","search_terms":["sound file retention","delete sound files"],"srd_ref":"initiatives/sound-export/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0058","status":"open","created_at":"2026-09-22T09:05:00Z","kind":"missing","topic":"When recorded Sound Files are deleted","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/leak-archive/srd.md that depend on this fact.","target_claim":"","detail":"Nowhere states when recorded Sound Files are deleted.","search_terms":["sound file deletion"],"srd_ref":"initiatives/leak-archive/srd.md","kb_marked_at":null,"kb_entry":null}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: kb` or
`status: draft` returns {"gaps":[]} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text. With no
filter, return every gap above.
