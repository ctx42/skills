---
type: agent
---
The gap store holds exactly two gaps:

{"id":"gap-0042","status":"open","kind":"missing","answer":"","srd_ref":"gw-firmware","doc_id":"kb/_inbox.md","heading_path":["Knowledge base inbox","Gateway firmware updates run only at night"],"search_terms":[],"hits":1,"created":"2026-09-26T10:00:00Z","filled_by":[],"topic":"LoRa Gateway firmware update window","demand":"","detail":"","target_claim":"EXAMPLE pushes a firmware update to an ALTECNO LoRa Gateway only between 01:00 and 04:00 in the Project's time zone.","file":"gap-0042-lora-gateway-firmware-update-window.md"}
{"id":"gap-0043","status":"open","kind":"missing","answer":"deferred","srd_ref":"gw-firmware","doc_id":"kb/_inbox.md","heading_path":["Knowledge base inbox","Gateway firmware updates run only at night"],"search_terms":[],"hits":1,"created":"2026-09-26T10:05:00Z","filled_by":[],"topic":"Night-only firmware window and emergency security updates","demand":"","detail":"Does the night-only firmware window also apply to emergency security updates for gateways?","target_claim":"","file":"gap-0043-night-only-firmware-window-and-emergency-security-updates.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so `status: filled` or
`status: draft` returns {"gaps":[]}), an `srd_ref` filter keeps only gaps whose
srd_ref contains that text, a `query` keeps only gaps whose topic, detail, or
search_terms share a word with it. With no filter, return both gaps.
