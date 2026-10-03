---
type: agent
---
The gap store holds exactly two gaps, both drafts a prior session left for the
SRD `specs/gateway.md`:

{"id":"gap-0071","status":"draft","kind":"missing","topic":"API Gateway error body format","doc_id":"","heading_path":null,"source_url":"","srd_ref":"specs/gateway.md","demand":"GW-4 needs the error body layout","target_claim":"","detail":"No corpus page describes the JSON body of a gateway error answer.","search_terms":["gateway error body"]}

{"id":"gap-0072","status":"draft","kind":"missing","topic":"API Gateway correlation id header","doc_id":"","heading_path":null,"source_url":"","srd_ref":"specs/gateway.md","demand":"GW-4 needs the correlation id source","target_claim":"","detail":"No corpus page names the header that carries the correlation id.","search_terms":["correlation id header"]}

Answer with {"gaps":[...]} holding every gap that matches the call's filters:
a `status` filter keeps only gaps with that status (so any status other than
`draft` returns {"gaps":[]}), an `srd_ref` filter keeps only gaps whose
srd_ref contains that text. With no filter, return both gaps.
