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
cat > kb/_inbox.md <<'EOF_INBOX'
---
title: Knowledge base inbox
cfsync-plugin: ignore-push
last_verified: 2026-09-29
---

# Knowledge base inbox

## Correlation uses a per-material propagation speed

> Not in the platform docs. Attested `initiatives/leak-correlation/srd.md`
> interview 2026-09-29.

Correlation uses a per-material propagation speed. When EXAMPLE correlates
two recordings, the speed of sound it uses for each pipe segment between the
two loggers is the speed for that segment's pipe material, not one speed for
the whole network.

## Provenance

Where each section of this inbox comes from.

| Section                                           | Source                                                     |
|---------------------------------------------------|------------------------------------------------------------|
| Correlation uses a per-material propagation speed | `initiatives/leak-correlation/srd.md` interview 2026-09-29 |
EOF_INBOX
cat > kb/_open-questions.md <<'EOF_OQ'
---
title: Knowledge base open questions
cfsync-plugin: ignore-push
---

# Knowledge base open questions

Every open question the knowledge base tracks, one row each.

| Question                            | Kind    | Raised     | Hits | Lives in                                        |
|-------------------------------------|---------|------------|------|-------------------------------------------------|
| Correlation result retention period | unknown | 2026-09-20 | 2    | [correlation.md](correlation.md#open-questions) |

## Closed

Questions answered or found moot.

| Question | Answer | Closed | Now stated in |
|----------|--------|--------|---------------|
EOF_OQ
cat > kb/correlation.md <<'EOF_CORR'
---
title: Leak Noise Correlation
aliases: [cross-correlation, correlator, AUTOCO correlation]
cfsync-plugin: ignore-push
attested: 2026-09-10
srd_ref: initiatives/autoco/srd.md
last_verified: 2026-09-20
---

# Leak Noise Correlation

How EXAMPLE correlates the recordings of two loggers to place a leak: which
loggers pair, which recordings are used, what a result carries, and how results
are shown and handled.

## What correlation is in EXAMPLE

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

Correlation compares the recordings of two loggers that sit on the same pipe
network and estimates where between them a leak noise originates. EXAMPLE
runs it on the recordings the loggers transfer each day. A correlation result
names the logger pair, the estimated leak position along the pipe path, and a
quality value.

## Logger pairs eligible for correlation

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

Only loggers of the same Project are paired. A pair must be joined by mapped
pipe; loggers with no mapped pipe between them are never paired. A logger may
belong to several pairs at once.

## Recording window used for correlation

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

Correlation uses the recordings both loggers made in the same nightly recording
window. Recordings from different nights are never correlated against each
other.

## Correlation quality value

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

Every correlation result carries a quality value from 0 to 100. The value
expresses how clearly one peak stands out in the cross-correlation function. A
result below 30 is shown greyed out in the result list.

## Correlation result position along the pipe path

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

The leak position is stated as a distance from the first logger of the pair,
measured along the mapped pipe path between the two loggers, not as a straight-
line distance.

## Correlation results on the map

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

A correlation result is drawn on the map as a marker on the pipe path at its
estimated position. Selecting the marker opens the result's details, including
both loggers and the quality value.

## Manual correlation from the device picker

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

A user can start a correlation by hand by picking two loggers on the map. A
manual correlation uses the most recent common recording window of the two
loggers. Its result is stored beside the automated results and marked as
manual.

## Correlation of stereo recordings

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

A stereo recording from a correlator such as LOG3000 BT is correlated channel
against channel within the one file. That correlation is separate from the
logger-pair correlation described above.

## Correlation and pipe data quality

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

Correlation depends on the mapped pipe network. Pipe length and pipe material
come from the Project's network data; a pipe segment with no material set is
shown in violet on the map and must be corrected before results along it can be
trusted.

## Correlation result statuses

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

A correlation result is New when it is produced. A user can set it to To check,
Confirmed, or Dismissed. Setting an AUTOCO detection to To check is what
creates a Leak Instance.

## Correlation re-runs after network edits

> Not in the platform docs. Attested `initiatives/autoco/srd.md` interview
> 2026-09-10.

Editing pipe length or pipe material does not re-run past correlations. Only
recordings correlated after the edit use the changed network data.

## Open questions

- How long is a correlation result kept before it is deleted?

## Provenance

Where each section of this page comes from.

| Section                                         | Source                                           |
|-------------------------------------------------|--------------------------------------------------|
| What correlation is in EXAMPLE                | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Logger pairs eligible for correlation           | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Recording window used for correlation           | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation quality value                       | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation result position along the pipe path | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation results on the map                  | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Manual correlation from the device picker       | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation of stereo recordings                | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation and pipe data quality               | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation result statuses                     | `initiatives/autoco/srd.md` interview 2026-09-10 |
| Correlation re-runs after network edits         | `initiatives/autoco/srd.md` interview 2026-09-10 |
EOF_CORR
