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
mkdir -p initiatives/booking-holds
cat > initiatives/booking-holds/srd.md <<'EOF_SRD'
# Payload Booking Holds

| Field      | Value                                                                |
|------------|----------------------------------------------------------------------|
| Summary    | Define how the system holds a launch slot while a customer books it. |
| Maintainer | Dana K                                                               |
| Reviewers  | John K                                                               |
| Tracking   | [SF-140](https://tracker.example.com/browse/SF-140)                  |
| Lifecycle  | DRAFT                                                                |
| Mockups    | none                                                                 |

## Introduction

This document specifies how the system holds a Launch Slot for a customer
while a booking completes, and how it answers when the hold lapses. It does
not change the Booking API's timeout or retry policy.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- Holding a Launch Slot while a customer completes a booking.
- Logging lapsed holds.

### Excluded

- Changing the Booking API's timeout or retry policy.

## Terms

### Slot Hold

The reservation the Booking API places on one Launch Slot while a customer
completes a booking.

## Requirements

### Payload Booking (PB)

- `PB-1` The system MUST answer HTTP 409 when a customer confirms a booking
  after its Slot Hold has lapsed.
- `PB-2` The system MUST release each Slot Hold when the Booking API's
  15-minute hold period ends.
- `PB-3` The system MUST log each lapsed Slot Hold with the id of its
  Customer Mission.
- `PB-4` The system MUST put the Slot Hold's id in the body of each HTTP 409
  answer.
EOF_SRD
