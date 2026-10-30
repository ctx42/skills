#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: docs
sources:
  - conflu
watch: true
mcp-port: 7791
---

# Project configuration

The docket plugin created this file to run its MCP doc server over the
sync folder. Add a top-level folder to `sources` to serve it too.
EOF_PC
mkdir -p conflu/doc/infraport/glossary conflu/doc/devices conflu/srd/int1-login
cat > conflu/doc/infraport/guidelines_for_software_requirements_documents.md <<'EOF_F1'
---
title: "Guidelines for Software Requirements Documents"
---

# Guidelines for Software Requirements Documents

Every SRD carries a metadata table, an introduction, and numbered requirements.
EOF_F1
cat > conflu/doc/infraport/glossary/data_point.md <<'EOF_F2'
---
title: "Data Point"
---

# Data Point

A Data Point is one measured value a device reports.
EOF_F2
cat > conflu/doc/devices/overview.md <<'EOF_F3'
---
title: "Devices"
---

# Devices

The platform reads meters through gateway devices.
EOF_F3
cat > conflu/srd/int1-login/login-srd.md <<'EOF_F4'
# Login Lockout

| Field     | Value |
|-----------|-------|
| Lifecycle | DRAFT |

## Introduction

How the system locks an account after repeated failed log-ins.
EOF_F4
