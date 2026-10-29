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

This document specifies how the Booking API authorises and checks each booking
request a customer sends, and how the system limits slot swaps on a booked
customer mission. It does not cover how launch slots are priced.

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

- `PB-1` The system MUST reject an unauthorised booking request with HTTP status
  401.
- `PB-2` The system MUST reject a booking request whose launch slot starts in
  fewer than 21 days with HTTP status 409.
- `PB-3` The system MUST reject a booking request whose Mission Manifest can not
  be parsed with HTTP status 422.

### Slot Swaps

- `SW-1` The system MUST refuse a second slot swap for the same customer
  mission.
- `SW-2` The system MUST refuse a slot swap requested shortly before the booked
  launch slot.
EOF_0
cat > initiatives/payload-booking/srd.review.md <<'EOF_1'
---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: initiatives/payload-booking/srd.md
---

# SRD Review — Payload Booking

## Errata

- [ ] #4 [minor, linguistic] PB-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #7 [minor, linguistic] PB-3 uses an open form: `can not` → `cannot`.
  (SRD:house)

- [ ] #9 [minor, linguistic] PB-2 misspells a word: `recieves` → `receives`.
  (SRD:house)

---

## Requirements

- [ ] #5 [major, verifiability] SW-2: "shortly before" is vague — state the
  swap deadline. (SRD:RQT-6)
EOF_1
