#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: docs
mcp-port: 7777
sources:
  - docs
kb: kb
initiatives: docs/initiatives
srd-standard: docs/srd-standard.md
glossary: docs/glossary
precedence:
  - kb
  - docs/api
srd-work: srd-work
watch: true
---

# Project configuration

## SRD skill keys

The srd skills read three keys that only they use; `/srd:init` proposes and
writes them, and never changes another key. The docket plugin writes the rest
of this file and runs the doc server.

| Key            | Meaning                                                                                                              |
|----------------|----------------------------------------------------------------------------------------------------------------------|
| `kb`           | Knowledge-base folder; confirmed platform facts land in its `_inbox.md`. List it in `sources` too, or it is not searched |
| `srd-standard` | The SRD standard document, by path or `id`; the skills read it through the doc server at the start of every session  |
| `srd-work`     | Folder for SRD working files (`review`, `decisions`, `questions`), outside every source; `none` keeps them beside each SRD |

A skill that finds one of these missing, `kb` not in `sources`, or a
`srd-work` folder inside a source stops and names the fix. `/srd:check`
reports every problem at once.
EOF_PC
cat > .mcp.json <<'EOF_MJ'
{"mcpServers": {"srd": {"type": "http", "url": "http://localhost:7777/mcp"}}}
EOF_MJ
mkdir -p docs/api docs/glossary docs/initiatives/pay kb gap srd-work/pay
touch gap/.gitkeep
printf '# Invoices\n' > docs/api/invoices.md
printf '# Payments\n' > docs/api/payments.md
printf '# SRD standard\n' > docs/srd-standard.md
printf '# Terms\n' > docs/glossary/terms.md
printf '# Card Payments\n' > docs/initiatives/pay/pay-srd.md
printf '# Billing\n' > kb/billing.md
printf '# Review\n' > srd-work/pay/pay-srd.review.md
