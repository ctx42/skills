---
type: agent
---
The gap store holds exactly these gaps, one JSON record per line:

{"id":"gap-0011","status":"open","created_at":"2026-09-10T08:00:00Z","kind":"missing","topic":"Sound File retention period","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/sound-export/srd.md that depend on this fact.","target_claim":"","detail":"The docs do not say how long a Sound File is kept.","search_terms":["sound file retention"],"srd_ref":"initiatives/sound-export/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0014","status":"open","created_at":"2026-09-10T08:00:00Z","kind":"missing","topic":"How long recordings are kept","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/leak-archive/srd.md that depend on this fact.","target_claim":"","detail":"Nowhere states when recordings are deleted.","search_terms":["recording retention"],"srd_ref":"initiatives/leak-archive/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0016","status":"open","created_at":"2026-09-10T08:00:00Z","kind":"missing","topic":"Infobar for a Device without location","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/device-map/srd.md that depend on this fact.","target_claim":"","detail":"The Infobar page does not cover a Device with no location.","search_terms":["infobar no location"],"srd_ref":"initiatives/device-map/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0018","status":"open","created_at":"2026-09-10T08:00:00Z","kind":"missing","topic":"Tag name length limit","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/tag-import/srd.md that depend on this fact.","target_claim":"","detail":"No maximum length for a Tag node name is documented.","search_terms":["tag name length"],"srd_ref":"initiatives/tag-import/srd.md","kb_marked_at":null,"kb_entry":null}
{"id":"gap-0019","status":"open","created_at":"2026-09-10T08:00:00Z","kind":"missing","topic":"Leak Instance merge rules","doc_id":"","heading_path":[],"source_url":"","demand":"Blocks the requirements of initiatives/leak-merge/srd.md that depend on this fact.","target_claim":"","detail":"The docs do not say when two Leak Instances merge.","search_terms":["merge leak instances"],"srd_ref":"initiatives/leak-merge/srd.md","kb_marked_at":null,"kb_entry":null}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: kb` or
`status: draft` returns {"gaps":[]} unless a gap above has that status), an
`srd_ref` filter keeps only gaps whose srd_ref contains that text. With no
filter, return every gap above.
