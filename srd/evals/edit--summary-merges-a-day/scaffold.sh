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
- `PB-2` The system MUST reject a booking request whose launch slot starts in
  fewer than 21 days with HTTP status 409.
- `PB-3` The system MUST reject a booking request whose payload mass exceeds the
  payload limit of the vehicle with HTTP status 422.

### Slot Swaps

- `SW-1` The system MUST refuse a second slot swap for the same customer
  mission.
- `SW-2` The system MUST refuse a slot swap requested less than 14 days before
  the booked launch slot.
EOF_0
cat > initiatives/payload-booking/srd.decisions.md <<'EOF_1'
# Changes — Payload Booking

## 2026-09-30 15:20

### Requirements

SW-2 now refuses a slot swap requested less than 14 days before the booked
launch slot, instead of "shortly before the booked launch slot".
Reason: "a tester can count 14 days."

PB-2 now rejects a booking request whose launch slot starts in fewer than 21
days, instead of 28 days.
Reason: "the build order freezes 21 days out; 28 turned good bookings away."

PB-3 now has the system as its subject: "The system MUST reject …" instead of
"A booking request … MUST be rejected".
Reason: "this makes the system the subject."

## 2026-09-30 09:10

### Requirements

PB-1 now rejects a booking request that names no launch slot, instead of "an
incomplete booking request".
Reason: "names a condition a tester can create."

PB-2 now rejects a booking request only when its launch slot starts in fewer
than 28 days.
Reason: "the factory needs time before the build order freezes."

## 2026-09-29

### Requirements

SW-2 was added: the system refuses a slot swap requested shortly before the
booked launch slot.
Reason: "a swap must not land after the build order freezes."
EOF_1
cat > initiatives/payload-booking/srd.review.md <<'EOF_2'
---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: initiatives/payload-booking/srd.md
---

# SRD Review — Payload Booking

## Requirements

- [ ] #12 [major, verifiability] SW-1: "second slot swap" does not say whether
  a swap that was rolled back counts — state it. (SRD:RQT-5)

---

## Resolved

- [x] #3 [blocker, coverage] Boundaries, Included: no requirement says how late
  a slot swap may be requested — add one. (SRD:BND-2) — added SW-2.

- [x] #5 [blocker, verifiability] PB-1: "incomplete" names no condition a
  tester can create — state it. (SRD:RQT-5) — PB-1 now names a request with no
  launch slot.

- [x] #6 [major, logical] PB-2: a booking accepted after the build order
  freezes cannot be built — state the cutoff. (SRD:consistency) — PB-2 now
  rejects a booking request inside a cutoff.

- [x] #8 [major, verifiability] SW-2: "shortly before" is vague — state the
  swap deadline. (SRD:RQT-6) — SW-2 now refuses a swap less than 14 days out.

- [x] #10 [major, linguistic] PB-3: "MUST be rejected" is passive — rewrite with
  "the system" as subject. (SRD:CLR-1) — PB-3 now has the system as subject.

---

## Withdrawn

- #2 [minor, terminology] Booking Request is defined twice (withdrawn: one
  entry, confirmed by author).

- #4 [major, redundancy] PB-1 and PB-2 overlap (withdrawn 2026-09-30 09:30:
  distinct conditions, confirmed by author).

- #9 [minor, format] SW-1: a trailing space after the word "mission"
  (withdrawn 2026-09-30 15:40: the sync restores it).
EOF_2
