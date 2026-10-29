#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/srd-standard.md
glossary: docs/glossary
precedence:
  - kb
  - docs/concepts
  - docs/api
  - docs/operations
  - docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
EOF_PC
mkdir -p initiatives/telemetry-replay
cat > initiatives/telemetry-replay/srd.md <<'EOF_F0'
# Telemetry Replay

| Field      | Value                                                              |
|------------|--------------------------------------------------------------------|
| Summary    | Define how the system stores downlink frames and replays a flight. |
| Maintainer | @noah.t                                                            |
| Reviewers  | @ethan.p                                                           |
| Tracking   | [SF-161](https://tracker.example.com/browse/SF-161)                |
| Lifecycle  | DRAFT                                                              |
| Mockups    | none                                                               |

## Introduction

This document specifies how the system stores the downlink frames a vehicle
sends and replays a stored flight on the Replay Timeline. It does not change
how the ground station receives downlink.

## Conventions

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Boundaries

### Included

- Storing each downlink frame a vehicle sends.
- Replaying a stored flight on the Replay Timeline.

### Excluded

- Changing how the ground station receives downlink.

## Terms

### Frame Gap

A run of downlink frames missing between two frames the ground station
received.

## Requirements

---

### Telemetry Replay (TLM)

- `TLM-1` The system MUST store each downlink frame with the time the ground
  station received it.
- `TLM-2` The system MUST log each of the ground station's 3× resend requests
  for a lost downlink frame.
- `TLM-3` The system MUST show each Frame Gap on the Replay Timeline.
- `TLM-4` The system MUST replay a flight's downlink frames in the order of
  their timestamps.
- `TLM-5` The system MUST store the 20 downlink frames per second that a
  vehicle sends during flight.
- `TLM-6` The system MUST keep the pad downlink of each vehicle for the
  Telemetry Replay retention period of 30 days.

---
EOF_F0
mkdir -p kb
cat > kb/telemetry-channels.md <<'EOF_KB'
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
EOF_KB
