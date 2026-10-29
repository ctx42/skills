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
mkdir -p docs/glossary
cat > docs/glossary/terms.md <<'EOF_0'
---
title: Starforge Terms
---

# Starforge Terms

## Hot-Fire

A static firing of an engine or Stage at the test site.

## Hot-Fire Campaign

The series of Hot-Fires that clears a Stage to fly. Campaign hot-fires are
scheduled between 06:00 and 10:00 site time.
EOF_0
