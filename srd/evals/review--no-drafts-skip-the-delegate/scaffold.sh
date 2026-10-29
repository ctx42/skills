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
mkdir -p initiatives/bay-calendar
cat > initiatives/bay-calendar/srd.md <<'EOF_F0'
# Bay Calendar

| Field      | Value                                                               |
|------------|---------------------------------------------------------------------|
| Summary    | Define how a bay scheduler books an assembly bay for a build order. |
| Maintainer | @maya.r                                                             |
| Reviewers  | @john.k                                                             |
| Tracking   | [SF-157](https://tracker.example.com/browse/SF-157)                 |
| Lifecycle  | DRAFT                                                               |
| Mockups    | none                                                                |

## Introduction

This document specifies how a bay scheduler books an assembly bay for a build
order, and how the system keeps two bookings of one bay apart. It does not
change how build orders are created.

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

- Booking an assembly bay for a build order.
- Refusing a bay booking that overlaps another booking of the same bay.
- Showing bay bookings on the Bay Map.

### Excluded

- Creating build orders.

## Terms

### Bay Booking

A span of days for which one assembly bay is reserved for one build order.

## Requirements

---

### Bay Bookings (CAL)

- `CAL-1` The system MUST let a bay scheduler create a Bay Booking for a build
  order.
- `CAL-2` The system MUST refuse a Bay Booking that overlaps another Bay
  Booking of the same assembly bay.
- `CAL-2` The system MUST show each Bay Booking on the Bay Map with the build
  order it holds.
- `CAL-3` Every refused Bay Booking MUST be reported to the bay scheduler
  together with the Bay Booking it overlaps.
- `CAL-4` A Bay Booking MUST be removed from the Bay Map when its build order
  is closed.
- `CAL-5` The system MUST let a bay scheduler cancel a Bay Booking.

---
EOF_F0
