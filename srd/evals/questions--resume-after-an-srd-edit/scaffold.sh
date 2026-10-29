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

| Field      | Value                                                                |
|------------|----------------------------------------------------------------------|
| Summary    | Let users record the parts picked into Part Kits and log every pick. |
| Maintainer | @dana.k                                                              |
| Reviewers  | @john.k                                                              |
| Tracking   | [SF-103](https://tracker.example.com/browse/SF-103)                  |
| Lifecycle  | DRAFT                                                                |
| Mockups    | none                                                                 |

## Introduction

This document specifies how the platform tracks the parts picked into a
[Part Kit](<../../docs/glossary/terms.md#part-kit>) for one
[Stage](<../../docs/glossary/terms.md#stage>) of a
[Build Order](<../../docs/glossary/terms.md#build-order-bo>). The system will
let a user record Kit Picks, undo them, and look them up, and every Kit Pick is
written to the Kit Pick Log. It will not order parts from suppliers or change
the Stage Parts List of a Stage design.

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
- `IN-3` Logging Kit Picks.
- `IN-4` Exporting a Build Order's Kit Picks as a CSV file.

### Excluded

- `EX-1` Ordering parts from suppliers.
- `EX-2` Changing the Stage Parts List of a Stage design.

## Terms

### Kit Pick

The record of one part picked into one Part Kit.

### Kit Pick Log

The record of every Kit Pick and every rejected Kit Pick.

### Stage Integration

The start of assembling one Stage of a Build Order from its Part Kit.

### Stage Parts List

The parts a Stage design allows in its Part Kit.

## Requirements

### Part kits (KIT)

- `KIT-1` The system MUST allow a user to record a Kit Pick against a Part Kit
  of a Build Order in an
  [Assembly Bay](<../../docs/glossary/terms.md#assembly-bay>) the user works
  in.
- `KIT-2` The system MUST link each Kit Pick to the Build Order of its Part
  Kit.
- `KIT-3a` The system MUST reject a Kit Pick whose part is not on the Stage
  Parts List of the Part Kit's Stage.
- `KIT-3b` The system MUST record each rejected Kit Pick in the kit pick log.
- `KIT-4` The system MUST schedule the picking of each Part Kit 3 working days
  before its Stage Integration.
- `KIT-5` The system MUST delete every Kit Pick of a Part Kit when that Part
  Kit is cancelled.
- `KIT-6` The system MUST NOT delete a Kit Pick that is older than 30 days.
- `KIT-7` The system MUST answer a Part Kit lookup within 300 ms at the 95th
  percentile for up to 2,000 open Build Orders.
- `KIT-8` The system MUST let a user list every Kit Pick of a Part Kit.
- `KIT-9` The system MUST limit the parts offered to a user to the Stage Parts
  List of the Part Kit's Stage.
- `KIT-10` Each Kit Pick is written to the Kit Pick Log.
- `KIT-11` The system MUST allow a user to undo a Kit Pick.
- `KIT-12` The system MUST keep the Kit Pick Log reliable.
EOF_SRD
cat > initiatives/part-kit-tracking/srd.questions.md <<'EOF_Q'
# SRD Questions — Part Kit Tracking

Source: `initiatives/part-kit-tracking/srd.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** KIT-5 deletes a Part Kit's Kit Picks when the kit is cancelled, while
KIT-6 forbids deleting any Kit Pick older than 30 days. What should happen
when someone cancels a Part Kit that has old picks?
<!-- review: #5 -->

**Q2** KIT-3 both rejects a part that is not on the list and logs the
rejection. Are those two separate behaviors we test separately, and should a
rejection always be logged?
<!-- review: #3 -->

**Q3** KIT-7 asks for Part Kit lookups to be "fast". What response time are
we committing to, and for how many Build Orders? QA can't test "fast".
<!-- review: #6 -->

**Q4** IN-2 promises undoing Kit Picks, but no requirement covers it. Do we
want undo in this SRD, and who may undo a pick?
<!-- review: #2 -->

**Q5** KIT-9 relies on a "Stage Parts List" that nothing defines. What exactly
is on a Stage's parts list?
<!-- review: #8 -->

**Q6** KIT-4 has us pick each Part Kit 3 working days before stage
integration, but the Part Kits concept document says kits are picked 5
working days before. Which lead time do we build to?
<!-- review: #4 -->

**Q7** KIT-10 writes every Kit Pick to the Kit Pick Log, but the SRD defines it
only as a record, and no platform document describes such a log. Is it an
existing platform log, and if so which one, or is this SRD introducing a new
store?
EOF_Q
cat > initiatives/part-kit-tracking/srd.review.md <<'EOF_R'
---
prepared: 2026-09-28 10:05
updated: 2026-09-28 10:05
source: initiatives/part-kit-tracking/srd.md
---

# SRD Review — Part Kit Tracking

## Errata

- [ ] #7 [minor, linguistic] KIT-8 repeats a word: `the the` → `the`.
  (SRD:house)

---

## Header

- [ ] #1 [blocker, structure] Header (Reviewers): names only the maintainer —
  add a reviewer other than the maintainer. (SRD:DOC-2)

## Boundaries

- [ ] #2 [blocker, coverage] IN-2: no requirement covers undoing a Kit Pick —
  add one or drop the item. (SRD:BND-2)

## Requirements

- [ ] #3 [blocker, atomicity] KIT-3: states two rules ("reject ... and log
  ...") — split into one rule each. (SRD:RQT-1)

- [ ] #4 [major, reference] KIT-4: schedules picking 3 working days before
  Stage Integration, but the Part Kits concept document states kits are
  picked 5 working days before stage integration — align KIT-4 with the
  platform lead time. (SRD:ref 1000000103)

- [ ] #5 [blocker, logical] KIT-5 and KIT-6: cancelling a Part Kit must delete
  its Kit Picks, but a Kit Pick older than 30 days must never be deleted; no
  rule says which wins — state the precedence. (SRD:consistency)

- [ ] #6 [blocker, verifiability] KIT-7: "fast" is a vague quality with no
  criterion — state a measurable limit. (SRD:RQT-6)

- [ ] #8 [blocker, terminology] KIT-9: "Stage Parts List" is used but defined
  neither in the Terms section nor in Shared Terms — define it. (SRD:TRM-3)

- [ ] #9 [major, linguistic] KIT-10: passive voice with no subject ("Each Kit
  Pick is written ...") — make "the system" the subject. (SRD:CLR-1)
EOF_R
