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
mkdir -p initiatives/booster-turnaround
cat > initiatives/booster-turnaround/srd.md <<'EOF_0'
# Booster Turnaround

| Field      | Value                                               |
|------------|-----------------------------------------------------|
| Summary    | Plan each booster's turnaround without a planner.   |
| Maintainer | @dana.k                                             |
| Reviewers  | @john.k                                             |
| Tracking   | [SF-118](https://tracker.example.com/browse/SF-118) |
| Lifecycle  | DRAFT                                               |
| Mockups    | none                                                |

## Introduction

This document specifies how the platform plans a booster's turnaround on its
own once the booster lands on the drone ship Meridian. The system will plan
the turnaround work; it will not change how a booster is inspected.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- Planning the turnaround of an Ember booster after it lands.

### Excluded

- Changing how a landed booster is inspected.

## Requirements

### Booster Turnaround (BT)

- `BT-1` The system MUST open a turnaround plan when an Ember booster lands on
  Meridian.
- `BT-2` The system should kind of book the booster's next flight close enough
  to the end of its turnaround, more or less.
EOF_0
