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
mkdir -p kb initiatives/gw-firmware
cat > kb/_inbox.md <<'EOF_INBOX'
---
title: Knowledge base inbox
cfsync-plugin: ignore-push
last_verified: 2026-10-01
---

# Knowledge base inbox

## Gateway firmware updates run only at night

> Not in the platform docs. Attested `initiatives/gw-firmware/srd.md` interview
> 2026-09-26 · `gap-0042`.

EXAMPLE pushes a firmware update to an ALTECNO LoRa Gateway only between
01:00 and 04:00 in the Project's time zone.

## Feature flags are set per Project

> Not in the platform docs. Attested session 2026-10-01.

Feature flags are always set per Project, never per Customer.

## Provenance

Where each section of this inbox comes from.

| Section                                    | Source                                                          |
|--------------------------------------------|-----------------------------------------------------------------|
| Gateway firmware updates run only at night | `initiatives/gw-firmware/srd.md` interview 2026-09-26, gap-0042 |
| Feature flags are set per Project          | Session 2026-10-01                                              |
EOF_INBOX
cat > kb/_open-questions.md <<'EOF_OQ'
---
title: Knowledge base open questions
cfsync-plugin: ignore-push
---

# Knowledge base open questions

Every open question the knowledge base tracks, one row each.

| Question                                                                                   | Kind     | Raised     | Hits | Lives in                                                          |
|--------------------------------------------------------------------------------------------|----------|------------|------|-------------------------------------------------------------------|
| Does the night-only firmware window also apply to emergency security updates for gateways? | deferred | 2026-09-26 | 1    | [_inbox.md](_inbox.md#gateway-firmware-updates-run-only-at-night) |

## Closed

Questions answered or found moot.

| Question | Answer | Closed | Now stated in |
|----------|--------|--------|---------------|
EOF_OQ
cat > initiatives/gw-firmware/srd.md <<'EOF_SRD'
# Gateway Firmware Rollout

|                |                                                           |
|----------------|-----------------------------------------------------------|
| **Objective**  | Let a user schedule firmware rollouts to LoRa Gateways.   |
| **Initiative** | <TODO: link to the ticketing initiative — must link back> |
| **Owners**     | <TODO: @primary-owner>, <TODO: @secondary-owner>          |
| **Status**     | [[!IN PROGRESS\|color=blue;style=bold]]                   |
| **Designs**    | N/A                                                       |

[[TOC]]

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how a user schedules a firmware rollout to the LoRa
Gateways of a Project. Updates already run only in the nightly update window
([knowledge base](../../kb/_inbox.md#gateway-firmware-updates-run-only-at-night)).

## Scope

### In Scope

--- TODO ---

### Out of Scope

**OSC-1:** Firmware updates for LoRa motes.

## Requirements

### Rollout Scheduling

**ROLL-1:** The system MUST let a user pick the night on which a firmware
rollout to a Project's LoRa Gateways starts.
EOF_SRD
