---
type: agent
---
The gap store holds exactly two gaps, both drafts a prior session left for the
SRD `specs/gateway.md`:

{"id":"gap-0071","status":"draft","kind":"missing","answer":"","srd_ref":"specs/gateway.md","doc_id":"","heading_path":null,"search_terms":["gateway error body"],"hits":1,"created":"2026-09-20T09:00:00Z","filled_by":[],"topic":"API Gateway error body format","demand":"GW-4 needs the error body layout","detail":"No corpus page describes the JSON body of a gateway error answer.","target_claim":"","file":"gap-0071-api-gateway-error-body-format.md"}

{"id":"gap-0072","status":"draft","kind":"missing","answer":"","srd_ref":"specs/gateway.md","doc_id":"","heading_path":null,"search_terms":["correlation id header"],"hits":1,"created":"2026-09-20T09:00:00Z","filled_by":[],"topic":"API Gateway correlation id header","demand":"GW-4 needs the correlation id source","detail":"No corpus page names the header that carries the correlation id.","target_claim":"","file":"gap-0072-api-gateway-correlation-id-header.md"}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so any status other than
`draft` returns {"gaps":[]}), an `srd_ref` filter keeps only gaps whose
srd_ref contains that text. With no filter, return both gaps.
