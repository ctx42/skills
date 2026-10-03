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
mkdir -p specs kb
cat > specs/labeling.md <<'EOF_SRD'
# Sound File Labeling

|                  |                                                                           |
|------------------|---------------------------------------------------------------------------|
| **Objective**    | Let API clients label Sound Files with Tags and find Sound Files by Tag.  |
| **Initiative**   | [INT-512](https://jira.example.com/browse/INT-512)                        |
| **Owners**       | @anna.keller (primary), @marek.nowak (secondary)                          |
| **Status**       | IN PROGRESS                                                               |
| **Designs**      | N/A                                                                       |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document defines how API clients label a
[Sound File](../confluence/infraport/glossary/main_glossary.md#Sound-File-(SND))
with existing [Tags](../confluence/infraport/glossary/main_glossary.md#Tag-(TAG))
and how they find Sound Files by Tag. The system will let an API client attach
a Tag to a Sound File, remove it again, and look up the Sound Files of a
[Project](../confluence/infraport/glossary/main_glossary.md#Project-(PRJ)) that
carry a given Tag.

## Scope

### In Scope

**SC-1:** Attaching a Tag to a Sound File through the API.

**SC-2:** Removing a Tag from a Sound File through the API.

**SC-3:** Looking up the Sound Files that carry a Tag through the API.

**SC-4:** Exporting the Tags of a Sound File as a CSV file.

### Out of Scope

**OSC-1:** Changes to the web user interface.

**OSC-2:** Creating, renaming, or deleting Tags.

## Requirements

### General (GR)

**GR-1:** The system MUST let an API client attach an existing Tag to a Sound
File of the same Project and MUST record which API client attached it.

**GR-2:** The system MUST create a Tag in the Sound File's Project when an API
client attaches a Tag name that does not exist there.

**GR-3:** The system MUST let an API client remove a Tag from a Sound File.

**GR-4:** The system MUST treat Tag names as case-sensitive.

**GR-5:** The system MUST return, for a lookup by Tag name, every Sound File in
the Project that carries that Tag.

**GR-6:** The system MUST let an API client attach every Tag of a Label Group
to a Sound File in one request.

**GR-7:** The system MUST answer Tag lookups fast.
EOF_SRD
