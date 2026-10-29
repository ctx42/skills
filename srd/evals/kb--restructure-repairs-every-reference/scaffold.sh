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
mkdir -p kb initiatives/hot-fire-scheduler
cat > kb/_inbox.md <<'EOF_INBOX'
---
title: Knowledge base inbox
last_verified: 2026-10-01
---

# Knowledge base inbox

## Hot-fires run only in the daytime test window

> Not in the platform docs. Attested hot-fire-scheduler interview
> 2026-09-26 · `gap-0042`.

> Open: gap-0043.

Starforge runs a hot-fire at the test site only between 08:00 and 18:00 site
time.

## Bay D is the only bay that fits Ember

> Not in the platform docs. Attested session 2026-10-01.

Ember vehicles are assembled only in Bay D; Bays A to C fit Spark only.

## Provenance

Where each section of this inbox comes from.

| Section                                       | Source                                            |
|-----------------------------------------------|---------------------------------------------------|
| Hot-fires run only in the daytime test window | hot-fire-scheduler interview 2026-09-26, gap-0042 |
| Bay D is the only bay that fits Ember         | Session 2026-10-01                                |
EOF_INBOX
cat > initiatives/hot-fire-scheduler/srd.md <<'EOF_SRD'
# Hot-Fire Scheduler

| Field      | Value                                                      |
|------------|------------------------------------------------------------|
| Summary    | Let a test conductor schedule a Stage's hot-fire campaign. |
| Maintainer | <TODO: @maintainer>                                        |
| Reviewers  | <TODO: @reviewer>                                          |
| Tracking   | <TODO: link to the work item — must link back>             |
| Lifecycle  | DRAFT                                                      |
| Mockups    | none                                                       |

## Introduction

This document specifies how a test conductor schedules the hot-fires of a
Stage's hot-fire campaign. Hot-fires already run only in the daytime test
window
([knowledge base](../../kb/_inbox.md#hot-fires-run-only-in-the-daytime-test-window)).

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

--- TODO ---

### Excluded

- Hot-fires of a single Wisp upper-stage engine.

## Requirements

### Hot-Fire Scheduling (HF)

- `HF-1` The system MUST let a test conductor pick the day on which a Stage's
  hot-fire campaign starts.
EOF_SRD
