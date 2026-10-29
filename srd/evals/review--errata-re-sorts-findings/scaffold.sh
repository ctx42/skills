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
mkdir -p initiatives/scrub-refunds
cat > initiatives/scrub-refunds/srd.md <<'EOF_F0'
# Scrub Refunds

| Field      | Value                                                     |
|------------|-----------------------------------------------------------|
| Summary    | Define how the system refunds the slot fee after a scrub. |
| Maintainer | @grace.l                                                  |
| Reviewers  | @john.k                                                   |
| Tracking   | [SF-153](https://tracker.example.com/browse/SF-153)       |
| Lifecycle  | DRAFT                                                     |
| Mockups    | none                                                      |

## Introduction

This document specifies how the system refunds the slot fee when a launch is
scrubbed: recording the cause of the scrub, computing the refund amout, and
paying it out. It does not change how launch slots are priced.

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

- Recording the cause of each scrub.
- Computing the refund for a scrubbed customer mission.
- Paying the refund to the customer account.

### Excluded

- Rebooking a scrubbed customer mission.

## Terms

### Customer-Caused Scrub

A scrub called because the customer's payload or its ground equipment was not
ready to fly.

## Requirements

---

### Scrub Refunds (REF)

- `REF-1` The system MUST record the cause of each scrub against the customer
  mission it belongs to.
- `REF-2` The system MUST refund 100% of the slot fee for a scrub caused by
  wheather or by the factory.
- `REF-3` The system MUST refund 80% of the slot fee for a Customer-Caused
  Scrub.
- `REF-4` A refund MUST be paid to the customer account that paid the slot
  fee, and the system MUST email the customer a refund statement when it pays
  the refund.
- `REF-5` A scrub that the payload's own behaviour causes MUST be refunded as
  a Customer-Caused Scrub.

---
EOF_F0
cat > initiatives/scrub-refunds/srd.review.md <<'EOF_F1'
---
prepared: 2026-10-01 09:00
updated: 2026-10-01 09:00
source: initiatives/scrub-refunds/srd.md
---

# SRD Review — Scrub Refunds

## Introduction

- [ ] #1 [minor, linguistic] Introduction ("computing the refund amout"):
  misspelling — `amout` → `amount`. (SRD:house)

## Requirements

- [ ] #2 [minor, linguistic] REF-2 misspells a word in "a scrub caused by
  wheather" — fix the spelling. (SRD:house)

- [ ] #3 [blocker, atomicity] REF-4: states two rules (pay the refund to the
  paying account and email a refund statement) — split into one rule each.
  (SRD:RQT-1)

- [ ] #4 [major, linguistic] REF-5 uses the British spelling "behaviour" and
  the passive voice — change it to "behavior" and restate REF-5 with the
  system as its subject. (SRD:CLR-1)

---

## Resolved

- [x] #5 [blocker, structure] Header (Reviewers): no reviewer other than the
  maintainer was listed — added @john.k. (SRD:DOC-2)
EOF_F1
