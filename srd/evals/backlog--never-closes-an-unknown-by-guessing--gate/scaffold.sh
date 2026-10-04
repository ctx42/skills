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
mkdir -p kb
cat > kb/_open-questions.md <<'EOF_0'
---
title: Knowledge base open questions
cfsync-plugin: ignore-push
---

# Knowledge base open questions

Every open question the knowledge base tracks, one row each.

## Open

| Question                                                            | Kind    | Raised     | Hits | Lives in                                        |
|---------------------------------------------------------------------|---------|------------|------|-------------------------------------------------|
| Is a per-sensor-type propagation speed needed for leak correlation? | unknown | 2026-08-19 | 4    | [correlation.md](correlation.md#open-questions) |

## Closed

| Question | Kind | Raised | Hits | Closed | Answer | Lives in |
|----------|------|--------|------|--------|--------|----------|
EOF_0
cat > kb/correlation.md <<'EOF_1'
---
title: Leak correlation
last_verified: 2026-08-19
---

# Leak correlation

## Correlation inputs

> Not in the platform docs. Attested session 2026-08-19.

A leak correlation pairs two Sensors on the same pipe and compares the arrival
times of the leak noise at each.

## Open questions

- Does leak correlation need a propagation speed per sensor type, or is one
  speed for every Sensor enough?

## Provenance

Where each section of this page comes from.

| Section            | Source             |
|--------------------|--------------------|
| Correlation inputs | Session 2026-08-19 |
EOF_1
