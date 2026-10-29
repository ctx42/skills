#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
sources:
  - docs
  - kb
kb: kb
initiatives: docs/initiatives
srd-standard: docs/srd-standard.md
glossary: docs/glossary
gaps: gap
precedence:
  - kb
  - docs/api
srd-work: srd-work
---

# Project configuration

## Front matter keys

| Key          | Meaning                       |
|--------------|-------------------------------|
| `mcp-server` | Name the server registers as. |
EOF_PC
mkdir -p docs/api docs/glossary docs/initiatives/pay kb gap srd-work
touch gap/.gitkeep srd-work/.gitkeep
printf '# SRD standard\n' > docs/srd-standard.md
printf '# API\n' > docs/api/overview.md
printf '# Invoice\n' > docs/glossary/invoice.md
printf '# Card Payments\n' > docs/initiatives/pay/pay-srd.md
printf '# Billing\n' > kb/billing.md
