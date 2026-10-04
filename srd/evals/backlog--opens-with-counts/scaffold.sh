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
---

# Knowledge base open questions

Every open question the knowledge base tracks, one row each.

## Open

| Question                                       | Kind     | Raised     | Hits | Lives in |
|------------------------------------------------|----------|------------|------|----------|
| Does a Project archive keep its Tags?          | deferred | 2026-08-11 | 1    |          |
| Which unit does the Infobar use for flow?      | deferred | 2026-08-27 | 4    |          |
| Can a Customer rename an EXAMPLE Instance?     | deferred | 2026-09-14 | 1    |          |
| Is a per-sensor-type propagation speed needed? | unknown  | 2026-08-19 | 4    |          |
| Do LoRa motes keep readings across a reboot?   | unknown  | 2026-09-17 | 1    |          |

## Closed

| Question | Kind | Raised | Hits | Closed | Answer | Lives in |
|----------|------|--------|------|--------|--------|----------|
EOF_0
