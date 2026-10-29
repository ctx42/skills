---
type: agent
---
The gap store holds exactly two gaps, both drafts a prior session left for the
SRD `telemetry-replay`:

{"id":"gap-0071","status":"draft","kind":"missing","answer":"","srd_ref":"telemetry-replay","doc_id":"","heading_path":null,"search_terms":["downlink frame receive time"],"hits":1,"created":"2026-09-20T09:00:00Z","filled_by":[],"topic":"Downlink frame receive time","demand":"TLM-1 needs the field that carries a frame's receive time","detail":"No corpus page names where the ground station records the time it received a downlink frame.","target_claim":"","file":"gap-0071-downlink-frame-receive-time.md"}

{"id":"gap-0072","status":"draft","kind":"missing","answer":"","srd_ref":"telemetry-replay","doc_id":"","heading_path":null,"search_terms":["frame gap threshold"],"hits":1,"created":"2026-09-20T09:00:00Z","filled_by":[],"topic":"Frame gap threshold","demand":"TLM-3 needs how long a silence counts as a Frame Gap","detail":"No corpus page says how many missing frames make a gap on the Replay Timeline.","target_claim":"","file":"gap-0072-frame-gap-threshold.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so any status other than
`draft` returns {"gaps":[]}), an `srd_ref` filter keeps only gaps whose
srd_ref contains that text or is contained in it (`telemetry-replay` and
`initiatives/telemetry-replay/srd.md` both match). With no filter, return both
gaps.
