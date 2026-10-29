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

| Field      | Value                                                                     |
|------------|---------------------------------------------------------------------------|
| Summary    | Let users record the parts picked into Part Kits and who picked each one. |
| Maintainer | @dana.k                                                                   |
| Reviewers  | @john.k                                                                   |
| Tracking   | [SF-103](https://tracker.example.com/browse/SF-103)                       |
| Lifecycle  | DRAFT                                                                     |
| Mockups    | none                                                                      |

## Introduction

This document specifies how the platform tracks the parts picked into a
[Part Kit](<../../docs/glossary/terms.md#part-kit>) for one
[Stage](<../../docs/glossary/terms.md#stage>) of a
[Build Order](<../../docs/glossary/terms.md#build-order-bo>). The system will
let a user record Kit Picks, undo them, and look them up, and every Kit Pick
records who made it and when. It will not order parts from suppliers.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- `IN-1` Recording Kit Picks against Part Kits.
- `IN-2` Undoing Kit Picks.
- `IN-3` Recording who made each Kit Pick and when.
- `IN-4` Looking up the Kit Picks of a Part Kit.

### Excluded

- `EX-1` Ordering parts from suppliers.
- `EX-2` Changing the parts a Stage design lists.

## Terms

### Kit Pick

The record of one part picked into one Part Kit.

### Stage Integration

The start of assembling one Stage of a Build Order from its Part Kit.

## Requirements

### Part kits (KIT)

- `KIT-1` The system MUST allow a user to record a Kit Pick against a Part Kit
  of a Build Order in an
  [Assembly Bay](<../../docs/glossary/terms.md#assembly-bay>) the user works
  in.
- `KIT-2` The system MUST create one Part Kit for each Stage of a Build Order.
- `KIT-3` The system MUST reject a Kit Pick whose part the Part Kit's Stage
  design does not list.
- `KIT-4` The system MUST schedule the picking of each Part Kit 5 working days
  before its Stage Integration.
- `KIT-5` The system MUST allow a user to undo a Kit Pick.
- `KIT-6` The system MUST record the user and the time of each Kit Pick.
- `KIT-7` The system MUST answer a Part Kit lookup within 300 ms at the 95th
  percentile for up to 2,000 open Build Orders.
- `KIT-8` The system MUST let a user list every Kit Pick of a Part Kit.
- `KIT-9` The system MUST record, for each Part Kit, the Launch Slot of its
  Build Order.
EOF_SRD
cat > initiatives/part-kit-tracking/srd.questions.md <<'EOF_Q'
# SRD Questions — Part Kit Tracking

Source: `initiatives/part-kit-tracking/srd.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** KIT-9 records each Part Kit's "Launch Slot", but the SRD never says what
a Launch Slot is. Is that a term the platform already defines, or do we need
to define it here?
<!-- review: #1 -->

**Q2** KIT-2 creates a Part Kit for each Stage, and a Part Kit on the platform
needs a pick priority. What pick priority should a new Part Kit carry?
EOF_Q
cat > initiatives/part-kit-tracking/srd.review.md <<'EOF_R'
---
prepared: 2026-09-30 09:20
updated: 2026-09-30 09:20
source: initiatives/part-kit-tracking/srd.md
---

# SRD Review — Part Kit Tracking

## Requirements

- [ ] #1 [blocker, terminology] KIT-9: "Launch Slot" is used but defined
  neither in the Terms section nor in Shared Terms — define it. (SRD:TRM-3)
EOF_R
