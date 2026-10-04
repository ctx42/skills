#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd-doc
kb: kb
initiatives: initiatives
srd-standard: docs/guidelines_for_software_requirements_documents.md
glossary: docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd-doc/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
EOF_PC
mkdir -p kb initiatives/hydrophone-sensor-types
cat > initiatives/hydrophone-sensor-types/srd.md <<'EOF_SRD'
---
title: Hydrophone Sensor Types
status: IN PROGRESS
---

# Hydrophone Sensor Types

## Purpose

Record on every Channel which kind of acoustic sensor produced its data, so
that hydrophone and vibrophone channels can be told apart in the Asset Service
and in downstream processing.

## Scope

In scope: the sensor-type field on a Channel, how it is set, and how it is
shown. Out of scope: every other asset attribute.

## Requirements

- **ST-1** The system MUST store a sensor type on each Channel.
- **ST-2** The system MUST set a Channel's sensor type from the channel
  purpose declared in Header F of the latest measurement file.
- **ST-3** The system MUST reject a sensor-type value outside the allowed
  set. (Allowed set: to be confirmed in interview.)
EOF_SRD
