---
type: agent
---
The documentation corpus has exactly one section relevant to this SRD:

{"title":"Downlink Frame Format","id":"1000000112","path":"docs/telemetry/downlink-format.md","rank":6,"heading_path":["Downlink Frame Format","Frame rate"],"source_url":"https://wiki.example.com/pages/1000000112","score":0.81,"text":"Downlink frames arrive at 10 per second during flight and 1 per second on the pad; each frame carries up to 64 channels."}

For a query about downlink frame rates, frames per second, how fast a vehicle
sends frames, or how many frames the system must store, answer
{"results":[<that section>]}.
The knowledge base holds one relevant section too:

{"title":"Telemetry Channels","id":"kb/telemetry-channels.md","path":"kb/telemetry-channels.md","rank":1,"heading_path":["Telemetry Channels","Downlink retention"],"source_url":"","score":0.78,"text":"> Not in the platform docs. Attested hot-fire-scheduler interview\n> 2026-08-14.\n\nTelemetry Replay keeps flight downlink for 2 years and pad downlink for 90\ndays, then deletes it."}

For a query about downlink retention, how long pad or flight downlink is kept,
or when stored frames are deleted, answer {"results":[<that KB section>]}.
The corpus says nothing anywhere about resend requests: for a query about
resends, retries, retry or resend counts, or lost frames, answer
{"results":[]}. For every other query, answer {"results":[]}.
