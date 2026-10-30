#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
mcp-port: 7777
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
watch: true
---

# Project configuration

## Front matter keys

| Key          | Meaning                       |
|--------------|-------------------------------|
| `mcp-server` | Name the server registers as. |
EOF_PC
cat > .mcp.json <<'EOF_MJ'
{"mcpServers": {"srd": {"type": "http", "url": "http://localhost:7777/mcp"}}}
EOF_MJ
mkdir -p docs/api docs/glossary docs/initiatives/pay kb gap srd-work/pay
printf '# Invoices\n' > docs/api/invoices.md
printf '# Payments\n' > docs/api/payments.md
printf '# SRD standard\n' > docs/srd-standard.md
printf '# Main glossary\n' > docs/glossary/main_glossary.md
printf '# Card Payments\n' > docs/initiatives/pay/pay-srd.md
printf '# Billing\n' > kb/billing.md
printf '# Review\n' > srd-work/pay/pay-srd.review.md
