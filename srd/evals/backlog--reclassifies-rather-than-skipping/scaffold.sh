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
mkdir -p kb
cat > kb/anvil-engine.md <<'EOF_0'
---
title: Anvil engine
last_verified: 2026-09-12
---

# Anvil engine

## Chamber temperature reporting

> Not in the platform docs. Attested session 2026-09-12.

> Open: gap-0042.

An Anvil engine reports its chamber temperature on its own telemetry channel
in every downlink frame of a hot-fire.

## Provenance

Where each section of this page comes from.

| Section                       | Source             |
|-------------------------------|--------------------|
| Chamber temperature reporting | Session 2026-09-12 |
EOF_0
