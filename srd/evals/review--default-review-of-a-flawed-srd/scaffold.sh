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
scrubbed: recording the cause of the scrub, computing the refund, and paying
it out. It does not change how launch slots are priced.

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
- Emailing the customer a refund statement when the refund is paid.
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
  weather or by the factory.
- `REF-3` The system MUST refund 80% of the slot fee for a Customer-Caused
  Scrub.
- `REF-4` The system SHALL validate the scrub cause and log the refund.
- `REF-5` The system MUST pay each refund to the customer account that paid
  the slot fee.
- `REF-6` The system MUST NOT pay more than one refund for the same scrub.
- `REF-7` The system MUST apply the same refund behaviour to Spark and Ember
  launches.

---
EOF_F0
