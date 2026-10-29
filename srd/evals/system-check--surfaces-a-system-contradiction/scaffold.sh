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
# Photo Tagging

| Field      | Value                                                        |
|------------|--------------------------------------------------------------|
| Summary    | Let API clients tag Photos with Tags and find Photos by Tag. |
| Maintainer | @ada.brook                                                   |
| Reviewers  | @lev.ortiz                                                   |
| Tracking   | [PIX-512](https://tickets.example.com/browse/PIX-512)        |
| Lifecycle  | DRAFT                                                        |
| Mockups    | none                                                         |

## Introduction

This document defines how API clients tag a
[Photo](../docs/glossary/main_glossary.md#photo-pho)
with existing [Tags](../docs/glossary/main_glossary.md#tag-tag)
and how they find Photos by Tag. The system will let an API client attach a
Tag to a Photo, remove it again, and look up the Photos of a
[Project](../docs/glossary/main_glossary.md#project-prj) that carry a given
Tag. It will not change the web user interface or manage the Tags themselves.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- `IN-1` Attaching a Tag to a Photo through the API.
- `IN-2` Removing a Tag from a Photo through the API.
- `IN-3` Looking up the Photos that carry a Tag through the API.

### Excluded

- `EX-1` Changes to the web user interface.
- `EX-2` Creating, renaming, or deleting Tags.

## Requirements

### General (GR)

- `GR-1` The system MUST let an API client attach an existing Tag to a Photo
  of the same Project.
- `GR-2` The system MUST reject a request to attach a Tag that does not exist
  in the Photo's Project.
- `GR-3` The system MUST let an API client remove a Tag from a Photo.
- `GR-4` The system MUST write each Tag name in API requests and responses as
  a slash-separated path.
- `GR-5` The system MUST return, for a lookup by Tag name, every Photo in the
  Project that carries that Tag.
- `GR-6` The system MUST order the Photos of a Tag lookup by Photo name,
  ascending.
- `GR-7` The system MUST answer Tag lookups fast.
EOF_SRD
