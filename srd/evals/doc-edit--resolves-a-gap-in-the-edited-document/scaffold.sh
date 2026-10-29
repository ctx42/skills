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
mkdir -p docs/operations
cat > docs/operations/reconciliation.md <<'EOF_0'
---
id: 2215906431
title: Reconciliation
url: https://wiki.example.com/pages/2215906431
---

# Reconciliation

A reconciliation run compares the postings of two Ledgers to find a payment
mismatch between them.

## Prerequisites

Both Ledgers use the same currency and close at the same cut-off.

## Results

A run reports each mismatch as an amount and the pair of postings behind it.
EOF_0
