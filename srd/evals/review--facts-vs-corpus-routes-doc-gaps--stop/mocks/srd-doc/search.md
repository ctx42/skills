---
type: agent
---
The documentation corpus has exactly one section relevant to this SRD:

{"doc_id":"docs/api-gateway/timeouts.md","heading_path":["API Gateway","Upstream timeout"],"source_url":"https://docs.example.com/api-gateway/timeouts#upstream-timeout","score":0.81,"text":"The API Gateway closes an upstream call that has not answered after 30 seconds and answers the client with HTTP 504 Gateway Timeout. The timeout is fixed and is not configurable per upstream."}

For a query about the API Gateway's timeout, upstream timeouts, HTTP 504, or
how long the gateway waits for an upstream, answer {"results":[<that section>]}.
The corpus says nothing anywhere about gateway retries: for a query about
retries, retry counts, or a retry policy, answer {"results":[]}. For every
other query, answer {"results":[]}.
