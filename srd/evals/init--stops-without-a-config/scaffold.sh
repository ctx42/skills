#!/usr/bin/env bash
set -euo pipefail
mkdir -p docs/api docs/standards docs/initiatives/pay kb
cat > docs/api/overview.md <<'EOF_F1'
# API overview

The API serves invoices and payments.
EOF_F1
cat > docs/standards/srd-standard.md <<'EOF_F2'
---
title: "Software Requirements Document Standard"
---

# Software Requirements Document Standard

Every SRD carries a metadata table and numbered requirements.
EOF_F2
cat > docs/glossary.md <<'EOF_F3'
# Glossary

**Invoice** — a request for payment.
EOF_F3
cat > docs/initiatives/pay/pay-srd.md <<'EOF_F4'
# Card Payments

| Field     | Value |
|-----------|-------|
| Lifecycle | DRAFT |
EOF_F4
cat > kb/billing.md <<'EOF_F5'
# Billing

Invoices are issued on the first day of the month.
EOF_F5
