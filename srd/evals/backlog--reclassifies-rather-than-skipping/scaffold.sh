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
mkdir -p kb
cat > kb/reader-battery.md <<'EOF_0'
---
title: Reader battery
last_verified: 2026-09-12
---

# Reader battery

## Battery reporting

> Not in the platform docs. Attested session 2026-09-12.

> Open: gap-0042.

A Reader device reports its battery level with every sync.

## Provenance

Where each section of this page comes from.

| Section           | Source             |
|-------------------|--------------------|
| Battery reporting | Session 2026-09-12 |
EOF_0
