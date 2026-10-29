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
mkdir -p docs/operations
cat > docs/operations/scrub-refunds.md <<'EOF_0'
---
id: 1000000105
title: Scrub Refunds
url: https://wiki.example.com/pages/1000000105
---

# Scrub Refunds

A scrub refund returns part or all of a launch slot fee to the customer when a
launch attempt is scrubbed.

## Refund rates

A weather or factory scrub refunds 100% of the slot fee. A customer-caused
scrub refunds 80% of it.

## Refund record

Each refund is recorded against the customer mission and the launch slot that
was scrubbed.
EOF_0
