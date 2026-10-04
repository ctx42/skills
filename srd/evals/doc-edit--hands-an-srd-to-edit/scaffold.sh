#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/guidelines_for_software_requirements_documents.md
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
# Automated Correlation

|                |                                                       |
|----------------|-------------------------------------------------------|
| **Objective**  | Run correlations without an operator.                 |
| **Initiative** | [INT-640](https://tickets.example.com/browse/INT-640) |
| **Owners**     | @anna.keller                                          |
| **Status**     | IN PROGRESS                                           |
| **Designs**    | N/A                                                   |

## Introduction

This document specifies how the platform starts correlation runs on its own.

## Scope

### In Scope

**SC-1:** Starting correlation runs without an operator.

## Requirements

### Automation (AC)

**AC-1:** The system MUST start a correlation run each night.

**AC-2:** The system should kind of pick Loggers that are near enough to each
other, more or less.
EOF_0
