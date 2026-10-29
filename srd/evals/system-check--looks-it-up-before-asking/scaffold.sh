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
assignment records who made it and when. It will not train models on labeled
Photos.

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
- `IN-3` Recording who made each Label Assignment and when.
- `IN-4` Looking up the Label Assignments of a Photo.

### Excluded

- `EX-1` Training machine learning models on labeled Photos.
- `EX-2` Managing the set of Labels a Project defines.

## Terms

### Label Assignment

The association of one Label with one Photo.

## Requirements

### General (GR)

- `GR-1` The system MUST allow a user to assign a Label to a Photo in a
  [Project](<../docs/glossary/main_glossary.md#project-prj>) the user belongs
  to.
- `GR-2` The system MUST store each Label as a Tag.
- `GR-3` The system MUST reject a Label Assignment whose Label the Photo's
  Project does not define.
- `GR-4` The system MUST write each Tag name as a dot-separated series of Tag
  node names.
- `GR-5` The system MUST allow a user to remove a Label Assignment.
- `GR-6` The system MUST record the user and the
  [Date](<../docs/glossary/main_glossary.md#date>) of each Label Assignment.
- `GR-7` The system MUST answer a Tag lookup within 300 ms at the 95th
  percentile for a Project holding up to 100 000 Tags.
- `GR-8` The system MUST let a user list every Label Assignment of a Photo.
- `GR-9` The system MUST place each Label's Tag in a Namespace of the Photo's
  Project.
EOF_SRD
cat > specs/labeling.questions.md <<'EOF_Q'
# SRD Questions — Photo Labeling

Source: `specs/labeling.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** GR-9 puts each Label's Tag in a "Namespace", but the SRD never says what
a Namespace is. Is that a term the platform already defines, or do we need to
define it here?
<!-- review: #1 -->

**Q2** GR-2 stores each Label as a Tag, and a Tag on the platform needs a Tag
Kind besides its name. What Tag Kind should a Label Tag carry?
EOF_Q
cat > specs/labeling.review.md <<'EOF_R'
---
prepared: 2026-09-30 09:20
updated: 2026-09-30 09:20
source: specs/labeling.md
---

# SRD Review — Photo Labeling

## Requirements

- [ ] #1 [blocker, terminology] GR-9: "Namespace" is used but defined neither
  in the Terms section nor in Shared Terms — define it. (SRD:TRM-3)
EOF_R
