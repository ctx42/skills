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
mkdir -p initiatives/part-kit-tracking kb
cat > initiatives/part-kit-tracking/srd.md <<'EOF_SRD'
# Part Kit Tracking

| Field      | Value                                                                   |
|------------|-------------------------------------------------------------------------|
| Summary    | Let API clients record picked parts and find a Build Order's Part Kits. |
| Maintainer | @dana.k                                                                 |
| Reviewers  | @john.k                                                                 |
| Tracking   | [SF-103](https://tracker.example.com/browse/SF-103)                     |
| Lifecycle  | DRAFT                                                                   |
| Mockups    | none                                                                    |

## Introduction

This document defines how API clients track the parts picked into a
[Part Kit](../../docs/glossary/terms.md#part-kit) and how they find the Part
Kits of a [Build Order](../../docs/glossary/terms.md#build-order-bo). Each Part
Kit holds the parts for one [Stage](../../docs/glossary/terms.md#stage) of its
Build Order. The system will let an API client record a picked part against a
Part Kit, mark a Part Kit complete, and look up the Part Kits of a Build Order.
It will not change any screen or order parts from suppliers.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- `IN-1` Recording a picked part against a Part Kit through the API.
- `IN-2` Marking a Part Kit complete through the API.
- `IN-3` Looking up the Part Kits of a Build Order through the API.

### Excluded

- `EX-1` Changes to any screen.
- `EX-2` Ordering parts from suppliers.

## Terms

### Stage Integration

The start of assembling one Stage of a Build Order from its Part Kit.

## Requirements

### Part kits (KIT)

- `KIT-1` The system MUST let an API client record a picked part against a Part
  Kit that is not complete.
- `KIT-2` The system MUST reject a picked part recorded against a Part Kit that
  does not exist.
- `KIT-3` The system MUST let an API client mark a Part Kit complete.
- `KIT-4` The system MUST schedule the picking of each Part Kit 3 working days
  before its Stage Integration.
- `KIT-5` The system MUST return, for a lookup by Build Order, every Part Kit
  of that Build Order.
- `KIT-6` The system MUST order the Part Kits of a lookup by Stage number,
  ascending.
- `KIT-7` The system MUST answer Part Kit lookups fast.
EOF_SRD
