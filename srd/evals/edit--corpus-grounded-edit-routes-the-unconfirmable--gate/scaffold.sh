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
mkdir -p initiatives/payload-booking
cat > initiatives/payload-booking/srd.md <<'EOF_0'
# Payload Booking

| Field      | Value                                                |
|------------|------------------------------------------------------|
| Summary    | Specify how the Booking API checks booking requests. |
| Maintainer | @dana.k                                              |
| Reviewers  | @ethan.p, @grace.l                                   |
| Tracking   | [SF-151](https://tracker.example.com/browse/SF-151)  |
| Lifecycle  | DRAFT                                                |
| Mockups    | none                                                 |

[[TOC]]

## Introduction

This document specifies how the Booking API checks each booking request a
customer sends, and how the system limits slot swaps on a booked customer
mission. It does not cover how launch slots are priced.

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

- Checks on every booking request the Booking API receives.
- Limits on slot swaps for a booked customer mission.

### Excluded

- Pricing of launch slots.

## Terms

### Booking Request

A customer's request, sent through the Booking API, to book one launch slot for
one payload.

## Requirements

### Booking Requests

- `PB-1` The system MUST reject a booking request that names no launch slot with
  HTTP status 400.
- `PB-2` The Booking API retries a failed slot lookup against the Launch
  Calendar before it rejects the booking request.
- `PB-3` The system MUST reject a booking request whose payload mass exceeds the
  payload limit of the vehicle with HTTP status 422.

### Slot Swaps

- `SW-1` The system MUST refuse a second slot swap for the same customer
  mission.
- `SW-2` The system MUST refuse a slot swap requested less than 14 days before
  the booked launch slot.
EOF_0
