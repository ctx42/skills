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
mkdir -p docs/operations
cat > docs/operations/correlation.md <<'EOF_0'
---
id: 2215906431
title: Correlation
url: https://wiki.example.com/pages/2215906431
---

# Correlation

A correlation run compares the recordings of two Loggers to locate a leak on
the water main between them.

## Prerequisites

Both Loggers sit on the same water main and record at the same sample rate.

## Results

A run reports the leak position as a distance from the first Logger.
EOF_0
