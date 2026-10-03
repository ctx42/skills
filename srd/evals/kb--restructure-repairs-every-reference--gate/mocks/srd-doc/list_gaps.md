---
type: agent
---
The gap store holds exactly one gap:

{"id":"gap-0042","status":"open","kind":"missing","topic":"LoRa Gateway firmware update window","doc_id":"kb/_inbox.md","heading_path":["Knowledge base inbox","Gateway firmware updates run only at night"],"srd_ref":"initiatives/gw-firmware/srd.md","kb_entry":null,"target_claim":"EXAMPLE pushes a firmware update to an ALTECNO LoRa Gateway only between 01:00 and 04:00 in the Project's time zone."}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: kb` or
`status: draft` returns {"gaps":[]}), an `srd_ref` filter keeps only gaps whose
srd_ref contains that text. With no filter, return the one gap.
