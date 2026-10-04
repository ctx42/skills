---
type: agent
---
The documentation corpus has exactly one section relevant to this SRD:

{"title":"API Gateway Timeouts","id":"2207301642","path":"docs/api-gateway/timeouts.md","rank":3,"heading_path":["API Gateway","Upstream timeout"],"source_url":"https://docs.example.com/api-gateway/timeouts","score":0.81,"text":"The API Gateway closes an upstream call that has not answered after 30 seconds and answers the client with HTTP 504 Gateway Timeout. The timeout is fixed and is not configurable per upstream."}

For a query about the API Gateway's timeout, upstream timeouts, HTTP 504, or
how long the gateway waits for an upstream, answer {"results":[<that section>]}.
The knowledge base holds one relevant section too:

{"title":"API Gateway","id":"kb/api-gateway.md","path":"kb/api-gateway.md","rank":1,"heading_path":["API Gateway","Error log retention"],"source_url":"","score":0.78,"text":"> Not in the platform docs. Attested `specs/audit.md` interview 2026-08-14.\n\nThe API Gateway keeps each error log entry for 90 days, then deletes it."}

For a query about the API Gateway's error log, log entries, log retention, or
how long failed calls are kept, answer {"results":[<that KB section>]}.
The corpus says nothing anywhere about gateway retries: for a query about
retries, retry counts, or a retry policy, answer {"results":[]}. For every
other query, answer {"results":[]}.
