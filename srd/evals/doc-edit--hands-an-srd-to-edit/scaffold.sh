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
mkdir -p initiatives/autoco
cat > initiatives/autoco/srd.md <<'EOF_0'
# Automated Reconciliation

| Field      | Value                                                 |
|------------|-------------------------------------------------------|
| Summary    | Run reconciliations without an operator.              |
| Maintainer | @anna.keller                                          |
| Reviewers  | @marek.nowak                                          |
| Tracking   | [ABC-640](https://tickets.example.com/browse/ABC-640) |
| Lifecycle  | DRAFT                                                 |
| Mockups    | none                                                  |

## Introduction

This document specifies how the platform starts reconciliation runs on its own.
The system will start runs without an operator; it will not change how a run
compares postings.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- Starting reconciliation runs without an operator.

### Excluded

- Changing how a run compares postings.

## Requirements

### Automation (AC)

- `AC-1` The system MUST start a reconciliation run each night.
- `AC-2` The system should kind of pick Ledgers that are close enough to each
  other, more or less.
EOF_0
