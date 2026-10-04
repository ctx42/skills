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
mkdir -p specs kb
cat > specs/labeling.md <<'EOF_SRD'
# Sound File Labeling

|                |                                                                         |
|----------------|-------------------------------------------------------------------------|
| **Objective**  | Let users attach labels to recordings and record who attached each one. |
| **Initiative** | [INT-512](https://jira.example.com/browse/INT-512)                      |
| **Owners**     | @anna.keller, @marek.nowak                                              |
| **Status**     | IN PROGRESS                                                             |
| **Designs**    | N/A                                                                     |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the platform stores
[Labels](<../docs/glossary/machine_learning_glossary.md#Label>)
on a [Sound File](<../docs/glossary/main_glossary.md#Sound-File-(SND)>).
The system will let a user assign Labels to a Sound File, remove them, and look
them up. Each Label is kept as a
[Tag](<../docs/glossary/main_glossary.md#Tag-(TAG)>), and every
assignment records who made it and when.

## Glossary

### Label Assignment

The association of one Label with one Sound File.

## Scope

### In Scope

**SC-1:** Assigning Labels to Sound Files.

**SC-2:** Removing Label Assignments.

**SC-3:** Recording who made each Label Assignment and when.

**SC-4:** Looking up the Label Assignments of a Sound File.

### Out of Scope

**OSC-1:** Training machine learning models on labeled Sound Files.

**OSC-2:** Managing the set of Labels a Project defines.

## Requirements

### General (GR)

**GR-1:** The system MUST allow a user to assign a Label to a Sound File in a
[Project](<../docs/glossary/main_glossary.md#Project-(PRJ)>) the
user belongs to.

**GR-2:** The system MUST store each Label as a Tag.

**GR-3:** The system MUST reject a Label Assignment whose Label the Sound File's
Project does not define.

**GR-4:** The system MUST write each Tag name as a dot-separated series of Tag
node names.

**GR-5:** The system MUST allow a user to remove a Label Assignment.

**GR-6:** The system MUST record the user and the
[Date](<../docs/glossary/main_glossary.md#Date>) of each Label
Assignment.

**GR-7:** The system MUST answer a Tag lookup within 300 ms at the 95th
percentile for a Project holding up to 100 000 Tags.

**GR-8:** The system MUST let a user list every Label Assignment of a Sound
File.

**GR-9:** The system MUST place each Label's Tag in a Namespace of the Sound
File's Project.
EOF_SRD
cat > specs/labeling.questions.md <<'EOF_Q'
---
cfsync-plugin: ignore-push
---

# SRD Questions — Sound File Labeling

Source: `specs/labeling.md`

Open questions only. Resolved items are removed; durable facts are banked.

**Q1** GR-9 puts each Label's Tag in a "Namespace", but the SRD never says what
a Namespace is. Is that a term the platform already defines, or do we need to
define it here?
<!-- review: #1 -->

**Q2** GR-2 stores each Label as a Tag, and a Tag on the platform needs a Tag
Kind besides its name. What Tag Kind should a Label Tag carry?
EOF_Q
cat > specs/labeling.review.md <<'EOF_R'
---
prepared: 2026-09-30 09:20
updated: 2026-09-30 09:20
source: specs/labeling.md
cfsync-plugin: ignore-push
---

# SRD Review — Sound File Labeling

## Requirements

- [ ] #1 [blocker, terminology] GR-9: "Namespace" is used but defined neither
  in the Glossary nor in the Company Glossary — define it. (SRD:GLO-3)
EOF_R
