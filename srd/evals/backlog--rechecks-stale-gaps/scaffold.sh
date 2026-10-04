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
cat > kb/gift-cards.md <<'EOF_0'
---
title: Gift cards
attested: 2026-09-20
srd_ref: gift-cards, checkout-v3
last_verified: 2026-09-30
---

# Gift cards

## Refund window

> Not in the platform docs. Attested gift-cards interview 2026-09-20.

A buyer may return an unused gift card for a full refund during the first 14
days after purchase. Later requests go to support, case by case.

## Gift card expiry

> Not in the platform docs. Attested gift-cards interview 2026-09-20;
> checkout-v3 interview 2026-09-29.

A gift card expires 24 months after purchase; its unspent balance is then
lost.

## Provenance

Where each section of this page comes from.

| Section          | Source                             |
|------------------|------------------------------------|
| Refund window    | gift-cards interview               |
| Gift card expiry | gift-cards, checkout-v3 interviews |
EOF_0
cat > kb/_inbox.md <<'EOF_1'
---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox
EOF_1
