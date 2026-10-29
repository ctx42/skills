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
mkdir -p docs/glossary
cat > docs/glossary/main_glossary.md <<'EOF_0'
---
title: Main Glossary
---

# Main Glossary

## Ledger

An account book that records every payment posted to one merchant account.

## Reconciliation

The comparison of two Ledgers' postings to find a payment mismatch between
them. A reconciliation run uses postings made between 02:00 and 04:00.
EOF_0
