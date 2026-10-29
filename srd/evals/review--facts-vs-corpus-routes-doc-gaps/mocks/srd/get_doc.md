---
type: agent
---
Answer with the full text of the document whose id or path the call names.

- `docs/srd-standard.md`: answer with exactly the text between the BEGIN and
  END marker lines below, verbatim and complete, the marker lines themselves
  left out.
- `1000000112` or `docs/telemetry/downlink-format.md`: answer with exactly the
  text between the DOWNLINK-BEGIN and DOWNLINK-END marker lines below.
- `kb/telemetry-channels.md`: answer with exactly the text between the
  KB-BEGIN and KB-END marker lines below.
- `docs/glossary/terms.md`: answer with exactly the text between the
  TERMS-BEGIN and TERMS-END marker lines below.
- `docs/glossary/ui-terms.md`: answer with exactly the text between the
  UI-BEGIN and UI-END marker lines below.
- `docs/glossary/ml-terms.md`: answer with exactly the text between the
  ML-BEGIN and ML-END marker lines below.
- Any other id or path that `list_docs` lists: answer with that document's
  title as a level-1 heading and one short paragraph on the page's own topic
  at Starforge Rocketworks; it says nothing about downlink frames, telemetry
  retention, or resend requests.
- Any other id: answer `{"error":"no document with id <the id>"}`.

BEGIN
{{file:fixtures/srd-standard.md}}
END

DOWNLINK-BEGIN
# Downlink Frame Format

A Downlink Frame is one timestamped packet of Telemetry Channel values a
vehicle sends to the ground.

## Frame rate

Downlink frames arrive at 10 per second during flight and 1 per second on the
pad; each frame carries up to 64 channels.
DOWNLINK-END

KB-BEGIN
---
title: Telemetry Channels
aliases: [downlink retention, telemetry replay]
attested: 2026-08-14
srd_ref: hot-fire-scheduler
last_verified: 2026-08-14
---

# Telemetry Channels

## Downlink retention

> Not in the platform docs. Attested hot-fire-scheduler interview
> 2026-08-14.

Telemetry Replay keeps flight downlink for 2 years and pad downlink for 90
days, then deletes it.
KB-END

TERMS-BEGIN
{{file:fixtures/glossary-terms.md}}
TERMS-END

UI-BEGIN
{{file:fixtures/glossary-ui-terms.md}}
UI-END

ML-BEGIN
{{file:fixtures/glossary-ml-terms.md}}
ML-END
