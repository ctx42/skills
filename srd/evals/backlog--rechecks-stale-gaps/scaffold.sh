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
cat > kb/scrub-refunds.md <<'EOF_0'
---
title: Scrub refunds
attested: 2026-09-20
srd_ref: scrub-refunds, payload-booking
last_verified: 2026-09-30
---

# Scrub refunds

## Customer scrub refund

> Not in the platform docs. Attested scrub-refunds interview 2026-09-20.

When the customer causes a scrub, Starforge pays back 80% of the slot fee;
the other 20% covers the pad crew's costs for the day.

## Refund claim deadline

> Not in the platform docs. Attested scrub-refunds interview 2026-09-20;
> payload-booking interview 2026-09-29.

A customer must claim a scrub refund within 60 days of the scrub; later
claims are refused.

## Provenance

Where each section of this page comes from.

| Section               | Source                                    |
|-----------------------|-------------------------------------------|
| Customer scrub refund | scrub-refunds interview                   |
| Refund claim deadline | scrub-refunds, payload-booking interviews |
EOF_0
cat > kb/_inbox.md <<'EOF_1'
---
title: Knowledge base inbox
last_verified: 2026-09-01
---

# Knowledge base inbox
EOF_1
