#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd-doc
kb: kb
initiatives: initiatives
srd-standard: confluence/infraport/guidelines_for_software_requirements_documents.md
glossary: confluence/infraport/glossary
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

| Question                                                          | Kind     | Raised     | Hits | Lives in                                              |
|-------------------------------------------------------------------|----------|------------|------|-------------------------------------------------------|
| What battery-low threshold does an ALTECNO logger use by default? | deferred | 2026-09-20 | 1    | [altecno-logger.md](altecno-logger.md#open-questions) |
| How often does an ALTECNO logger upload its buffered readings?    | deferred | 2026-09-20 | 1    | [altecno-logger.md](altecno-logger.md#open-questions) |

## Closed

| Question | Kind | Raised | Hits | Closed | Answer | Lives in |
|----------|------|--------|------|--------|--------|----------|
EOF_0
cat > kb/altecno-logger.md <<'EOF_1'
---
title: ALTECNO logger
last_verified: 2026-09-20
---

# ALTECNO logger

## Battery reporting

> Not in the platform docs. Attested session 2026-09-20.

An ALTECNO logger reports its battery voltage with every upload.

## Open questions

- What battery-low threshold does an ALTECNO logger use by default?
- How often does an ALTECNO logger upload its buffered readings?

## Provenance

Where each section of this page comes from.

| Section           | Source             |
|-------------------|--------------------|
| Battery reporting | Session 2026-09-20 |
EOF_1
cat > kb/_inbox.md <<'EOF_2'
---
title: Knowledge base inbox
cfsync-plugin: ignore-push
last_verified: 2026-09-01
---

# Knowledge base inbox
EOF_2
