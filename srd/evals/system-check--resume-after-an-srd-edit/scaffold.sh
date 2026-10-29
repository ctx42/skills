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
  - docs/api-gateway
  - docs/operations
  - docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
EOF_PC
mkdir -p specs kb
cat > specs/labeling.md <<'EOF_SRD'
# Photo Labeling

| Field      | Value                                                               |
|------------|---------------------------------------------------------------------|
| Summary    | Let users attach labels to photos and record who attached each one. |
| Maintainer | @ada.brook                                                          |
| Reviewers  | @lev.ortiz                                                          |
| Tracking   | [PIX-512](https://tickets.example.com/browse/PIX-512)               |
| Lifecycle  | DRAFT                                                               |
| Mockups    | none                                                                |

## Introduction

This document specifies how the platform stores
[Labels](<../docs/glossary/machine_learning_glossary.md#label>)
on a [Photo](<../docs/glossary/main_glossary.md#photo-pho>).
The system will let a user assign Labels to a Photo, remove them, and look
them up. Each Label is kept as a
[Tag](<../docs/glossary/main_glossary.md#tag-tag>), and every
assignment is written to the Label Audit Log. It will not train models on
labeled Photos or manage a Project's Label Set.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- `IN-1` Assigning Labels to Photos.
- `IN-2` Removing Label Assignments.
- `IN-3` Auditing Label Assignments.
- `IN-4` Exporting a Project's Label Assignments as a CSV file.

### Excluded

- `EX-1` Training machine learning models on labeled Photos.
- `EX-2` Managing the Label Set of a Project.

## Terms

### Label Assignment

The association of one Label with one Photo.

### Label Audit Log

The record of every Label Assignment and every rejected Label Assignment.

### Label Set

The Labels a Project allows its users to assign.

## Requirements

### General (GR)

- `GR-1` The system MUST allow a user to assign a Label to a Photo in a
  [Project](<../docs/glossary/main_glossary.md#project-prj>) the user belongs
  to.
- `GR-2` The system MUST store each Label as a Tag.
- `GR-3a` The system MUST reject a Label Assignment whose Label is not in the
  Photo's Project's Label Set.
- `GR-3b` The system MUST record each rejected Label Assignment in the label
  audit log.
- `GR-4` The system MUST write each Tag name as a slash-separated path.
- `GR-5` The system MUST delete every Label Assignment of a Tag when that Tag
  is deleted.
- `GR-6` The system MUST NOT delete a Label Assignment that is older than 30
  days.
- `GR-7` The system MUST answer a Tag lookup within 300 ms at the 95th
  percentile for a Project holding up to 100 000 Tags.
- `GR-8` The system MUST let a user list every Label Assignment of a Photo.
- `GR-9` The system MUST limit the Labels offered to a user to the Label Set
  of the Photo's Project.
- `GR-10` Each Label Assignment is written to the Label Audit Log.
- `GR-11` The system MUST allow a user to remove a Label Assignment.
- `GR-12` The system MUST keep the Label Audit Log reliable.
EOF_SRD
cat > specs/labeling.questions.md <<'EOF_Q'
# SRD Questions — Photo Labeling

Source: `specs/labeling.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** GR-5 deletes a Tag's Label Assignments with the Tag, while GR-6 forbids
deleting any assignment older than 30 days. What should happen when someone
deletes a Tag that has old assignments?
<!-- review: #5 -->

**Q2** GR-3 both rejects an undefined Label and logs the rejection. Are those
two separate behaviors we test separately, and should a rejection always be
logged?
<!-- review: #3 -->

**Q3** GR-7 asks for Tag lookups to be "fast". What response time are we
committing to, and for what Project size? QA can't test "fast".
<!-- review: #6 -->

**Q4** IN-2 promises removing Label Assignments, but no requirement covers it.
Do we want removal in this SRD, and who may remove an assignment?
<!-- review: #2 -->

**Q5** GR-9 relies on a "Label Set" that nothing defines. What exactly is in a
Project's Label Set?
<!-- review: #8 -->

**Q6** GR-4 has us write Tag names as a slash-separated path, but the Tags
concept document says a Tag name is a comma-separated series of named nodes.
Which separator do Label Tags use?
<!-- review: #4 -->

**Q7** GR-10 writes every Label Assignment to the Label Audit Log, but the SRD
defines it only as a record, and no platform document describes such a log. Is
it an existing platform log, and if so which one, or is this SRD introducing a
new store?
EOF_Q
cat > specs/labeling.review.md <<'EOF_R'
---
prepared: 2026-09-28 10:05
updated: 2026-09-28 10:05
source: specs/labeling.md
---

# SRD Review — Photo Labeling

## Errata

- [ ] #7 [minor, linguistic] GR-8 uses British spelling: `labelling` →
  `labeling`. (SRD:house)

---

## Header

- [ ] #1 [blocker, structure] Header (Reviewers): names only the maintainer —
  add a reviewer other than the maintainer. (SRD:DOC-2)

## Boundaries

- [ ] #2 [blocker, coverage] IN-2: no requirement covers removing a Label
  Assignment — add one or drop the item. (SRD:BND-2)

## Requirements

- [ ] #3 [blocker, atomicity] GR-3: states two rules ("reject ... and log
  ...") — split into one rule each. (SRD:RQT-1)

- [ ] #4 [major, reference] GR-4: requires Tag names written as a
  slash-separated path, but the Tags concept document states Tag names are a
  comma-separated series of named nodes — align GR-4 with the platform format.
  (SRD:ref 1774485611)

- [ ] #5 [blocker, logical] GR-5 and GR-6: deleting a Tag must delete its
  Label Assignments, but an assignment older than 30 days must never be
  deleted; no rule says which wins — state the precedence. (SRD:consistency)

- [ ] #6 [blocker, verifiability] GR-7: "fast" is a vague quality with no
  criterion — state a measurable limit. (SRD:RQT-6)

- [ ] #8 [blocker, terminology] GR-9: "Label Set" is used but defined neither
  in the Terms section nor in Shared Terms — define it. (SRD:TRM-3)

- [ ] #9 [major, linguistic] GR-10: passive voice with no subject ("Each Label
  Assignment is written ...") — make "the system" the subject. (SRD:CLR-1)
EOF_R
