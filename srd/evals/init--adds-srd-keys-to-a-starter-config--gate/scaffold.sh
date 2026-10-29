#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: docs
sources:
  - wiki
watch: true
mcp-port: 7791
---

# Project configuration

The docket plugin created this file to run its MCP doc server over the
sync folder. Add a top-level folder to `sources` to serve it too.
EOF_PC
mkdir -p wiki/doc/process wiki/doc/glossary wiki/doc/engines wiki/srd/slot-swap
cat > wiki/doc/process/srd-guidelines.md <<'EOF_F1'
---
title: "Software Requirements Document Guidelines"
---

# Software Requirements Document Guidelines

Every SRD carries a metadata table, an introduction, and numbered requirements.
EOF_F1
cat > wiki/doc/glossary/launch-slot.md <<'EOF_F2'
---
title: "Launch Slot"
---

# Launch Slot

A Launch Slot is a 90-minute period booked for one launch.
EOF_F2
cat > wiki/doc/engines/overview.md <<'EOF_F3'
---
title: "Engines"
---

# Engines

Boosters fly Anvil engines; upper stages fly one Wisp engine.
EOF_F3
cat > wiki/srd/slot-swap/slot-swap-srd.md <<'EOF_F4'
# Slot Swap

| Field     | Value |
|-----------|-------|
| Lifecycle | DRAFT |

## Introduction

How a customer moves a mission to another launch slot.
EOF_F4
