#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd-doc
kb: kb
initiatives: initiatives
srd-standard: confluence/example/guidelines_for_software_requirements_documents.md
glossary: confluence/example/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd-doc/fixtures/srd-standard.md` stands in for the
`get_doc` result of `srd-standard` — see `dev/eval/blind-runner-prompt.md`.
EOF_PC
mkdir -p kb
cat > kb/_inbox.md <<'EOF_INBOX'
---
title: Knowledge base inbox
cfsync-plugin: ignore-push
last_verified: 2026-09-30
---

# Knowledge base inbox

## Battery-low alarm threshold for ORTOMAT loggers

> Not in the platform docs. Attested `initiatives/int366-battery/srd.md`
> interview 2026-09-25.

An ORTOMAT logger raises a battery-low alarm when its remaining battery falls
below 15 %.

## Project time zone is fixed when the Project is created

> Not in the platform docs. Attested session 2026-09-30.

A Project's time zone is set when the Project is created. It cannot be changed
afterward.

## Provenance

Where each section of this inbox comes from.

| Section                                                | Source                                                   |
|--------------------------------------------------------|----------------------------------------------------------|
| Battery-low alarm threshold for ORTOMAT loggers        | `initiatives/int366-battery/srd.md` interview 2026-09-25 |
| Project time zone is fixed when the Project is created | Session 2026-09-30                                       |
EOF_INBOX
cat > kb/_open-questions.md <<'EOF_OQ'
---
title: Knowledge base open questions
cfsync-plugin: ignore-push
---

# Knowledge base open questions

Every open question the knowledge base tracks, one row each.

| Question | Kind | Raised | Hits | Lives in |
|----------|------|--------|------|----------|

## Closed

Questions answered or found moot.

| Question | Answer | Closed | Now stated in |
|----------|--------|--------|---------------|
EOF_OQ
cat > kb/logger-battery.md <<'EOF_PAGE'
---
title: Logger Battery and Power
aliases: [battery, battery status, battery level]
cfsync-plugin: ignore-push
attested: 2026-09-18
srd_ref: initiatives/int366-battery/srd.md
last_verified: 2026-09-18
---

# Logger Battery and Power

How EXAMPLE reports a logger's battery and what the battery figures mean.

## Battery status is reported in percent

> Not in the platform docs. Attested `initiatives/int366-battery/srd.md`
> interview 2026-09-18.

A logger reports its battery status as a percentage of remaining capacity with
each daily transfer.

## Provenance

Where each section of this page comes from.

| Section                               | Source                                                   |
|---------------------------------------|----------------------------------------------------------|
| Battery status is reported in percent | `initiatives/int366-battery/srd.md` interview 2026-09-18 |
EOF_PAGE
cat > kb/projects.md <<'EOF_PAGE'
---
title: Projects and Project Settings
aliases: [project, project settings]
cfsync-plugin: ignore-push
attested: 2026-09-12
srd_ref: initiatives/int248-licensing/srd.md
last_verified: 2026-09-12
---

# Projects and Project Settings

What a Project is in EXAMPLE and which settings belong to it.

## Feature flags are set per Project

> Not in the platform docs. Attested `initiatives/int248-licensing/srd.md`
> interview 2026-09-12.

Feature flags are always set per Project, never per Customer.

## Provenance

Where each section of this page comes from.

| Section                           | Source                                                     |
|-----------------------------------|------------------------------------------------------------|
| Feature flags are set per Project | `initiatives/int248-licensing/srd.md` interview 2026-09-12 |
EOF_PAGE
