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
mkdir -p kb
cat > kb/_inbox.md <<'EOF_INBOX'
---
title: Knowledge base inbox
last_verified: 2026-09-29
---

# Knowledge base inbox

## Part kits round fasteners up to a per-bay pack size

> Not in the platform docs. Attested part-kit-tracking
> interview 2026-09-29.

Part kits round fasteners up to a per-bay pack size. When Starforge picks a
part kit, it rounds each fastener count up to the pack size of the assembly
bay the kit goes to, not to one pack size for the whole factory.

## Provenance

Where each section of this inbox comes from.

| Section                                             | Source                                 |
|-----------------------------------------------------|----------------------------------------|
| Part kits round fasteners up to a per-bay pack size | part-kit-tracking interview 2026-09-29 |
EOF_INBOX
cat > kb/part-kits.md <<'EOF_CORR'
---
title: Part Kits
aliases: [kit, pick list, kit cart]
attested: 2026-09-10
srd_ref: bay-calendar
last_verified: 2026-09-20
---

# Part Kits

How Starforge picks the parts for each Stage of a Build Order: when a kit is
picked, which store supplies it, what a kit carries, and how kits are shown
and handled.

## What a part kit is at Starforge

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

A part kit is the set of parts Starforge picks for one Stage of one Build
Order. Starforge picks it from the parts store into kit carts, one cart per
Stage. A kit names the Build Order, the Stage, and a shortage count.

## When a part kit is picked

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

A part kit is picked 5 working days before its Stage's integration starts.
A kit for a Stage with no integration date is never picked.

## Parts store used for a kit

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

A kit is picked from the parts store of the site where its assembly bay
stands. Parts from different stores are never mixed within one kit.

## Kit shortage count

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

Every kit carries a shortage count from 0 upward: the number of parts the
store could not supply. A kit with a shortage count above 0 is shown amber on
the Build Board.

## Kit delivery to the assembly bay

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

A kit is delivered to the assembly bay's staging area on the working day
before its Stage's integration starts, not on the day itself.

## Part kits on the Build Board

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

The Build Board shows one row per kit, earliest integration first.
Selecting the row opens the kit's pick list, including the shortage count.

## Manual kits from the build order screen

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

A bay scheduler can request a kit by hand from the build order screen. A
manual kit is picked from the store's current stock. It is listed beside the
scheduled kits and marked as manual.

## Kits for engine swaps

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

Replacing an Anvil engine on a Stage is kitted on its own. That kit is
separate from the Stage kit described above.

## Kits and bill-of-materials quality

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

Picking depends on the Stage's bill of materials. A part with no revision
number is shown in violet on the build order screen and must be corrected
before its kit can be trusted.

## Part kit statuses

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

A kit is Planned when it is created. A bay scheduler can set it to
Picking, Short, or Delivered. Setting a kit to Short is what opens a
shortage review.

## Kit re-picking after bill-of-materials edits

> Not in the platform docs. Attested bay-calendar interview
> 2026-09-10.

Editing a Stage's bill of materials does not re-pick kits already picked.
Only kits picked after the edit use the changed bill of materials.

## Provenance

Where each section of this page comes from.

| Section                                      | Source                            |
|----------------------------------------------|-----------------------------------|
| What a part kit is at Starforge              | bay-calendar interview 2026-09-10 |
| When a part kit is picked                    | bay-calendar interview 2026-09-10 |
| Parts store used for a kit                   | bay-calendar interview 2026-09-10 |
| Kit shortage count                           | bay-calendar interview 2026-09-10 |
| Kit delivery to the assembly bay             | bay-calendar interview 2026-09-10 |
| Part kits on the Build Board                 | bay-calendar interview 2026-09-10 |
| Manual kits from the build order screen      | bay-calendar interview 2026-09-10 |
| Kits for engine swaps                        | bay-calendar interview 2026-09-10 |
| Kits and bill-of-materials quality           | bay-calendar interview 2026-09-10 |
| Part kit statuses                            | bay-calendar interview 2026-09-10 |
| Kit re-picking after bill-of-materials edits | bay-calendar interview 2026-09-10 |
EOF_CORR
