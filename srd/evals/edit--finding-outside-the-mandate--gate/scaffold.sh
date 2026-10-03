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
mkdir -p specs
cat > specs/login.md <<'EOF_0'
# Login Token Validation

|                |                                                     |
|----------------|-----------------------------------------------------|
| **Objective**  | Specify how the API Gateway validates Login Tokens. |
| **Initiative** | INT-512                                             |
| **Owners**     | @anna.keller, @marco.rossi                          |
| **Status**     | [[!IN PROGRESS\|color=blue;style=bold]]             |
| **Designs**    | N/A                                                 |

[[TOC]]

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the API Gateway checks the Login Token that
accompanies each API request, and how it locks a user account after repeated
failed sign-in attempts. It does not cover how Login Tokens are issued or
refreshed.

## Glossary

### Login Token

A signed credential that identifies a signed-in user for a limited time.

## Scope

### In Scope

**SC-1:** Validation of the Login Token on every API request.

**SC-2:** Lockout of a user account after repeated failed sign-in attempts.

### Out of Scope

**OSC-1:** Issuing and refreshing Login Tokens.

## Requirements

### Gateway Rules

**GR-1:** The system MUST reject an unauthorised API request with HTTP status
401.

**GR-2:** The system MUST validate the Login Token quickly.

**GR-3:** The system must reject an API request whose Login Token has expired
with HTTP status 401.

### Account Lockout

**LCK-1:** The system MUST lock a user account after 5 consecutive failed
sign-in attempts.

**LCK-2:** The system MUST unlock a locked user account 15 minutes after it was
locked.
EOF_0
cat > specs/login.review.md <<'EOF_1'
---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: specs/login.md
cfsync-plugin: ignore-push
---

# SRD Review — Login Token Validation

## Metadata

- [ ] #2 [major, metadata] Initiative: names INT-512 but does not link to the
  initiative in the ticketing system — add the link. (SRD:STR-3)

## Requirements

- [ ] #1 [minor, linguistic] GR-1 uses British spelling ("unauthorised") —
  use US English. (SRD:house)

- [ ] #3 [major, verifiability] GR-2: "quickly" is vague — state a measurable
  limit. (SRD:REQ-6)

- [ ] #4 [minor, style] GR-3: the keyword "must" is lowercase — capitalize it.
  (SRD:LANG-4)
EOF_1
