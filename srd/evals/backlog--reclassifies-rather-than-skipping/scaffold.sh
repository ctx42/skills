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
mkdir -p kb
cat > kb/logger-battery.md <<'EOF_0'
---
title: Logger battery
last_verified: 2026-09-12
---

# Logger battery

## Battery reporting

> Not in the platform docs. Attested session 2026-09-12.

> Open: gap-0042.

An ALTECNO logger reports its battery voltage with every upload.

## Provenance

Where each section of this page comes from.

| Section           | Source             |
|-------------------|--------------------|
| Battery reporting | Session 2026-09-12 |
EOF_0
