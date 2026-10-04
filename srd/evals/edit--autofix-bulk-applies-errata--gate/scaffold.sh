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
mkdir -p specs
cat > specs/login.md <<'EOF_0'
# Login Token Validation

|                |                                                       |
|----------------|-------------------------------------------------------|
| **Objective**  | Specify how the API Gateway validates Login Tokens.   |
| **Initiative** | [INT-512](https://tickets.example.com/browse/INT-512) |
| **Owners**     | @anna.keller, @marco.rossi                            |
| **Status**     | [[!IN PROGRESS\|color=blue;style=bold]]               |
| **Designs**    | N/A                                                   |

[[TOC]]

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the API Gateway authorises each API request by
checking the Login Token that accompanies each API request, and how it locks a
user account after repeated failed sign-in attempts. It does not cover how Login
Tokens are issued or refreshed.

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

**GR-2:** The system MUST reject an API request whose Login Token has expired
with HTTP status 401.

**GR-3:** The system MUST reject an API request whose Login Token can not be
verified with HTTP status 401.

### Account Lockout

**LCK-1:** The system MUST lock a user account after 5 consecutive failed
sign-in attempts.

**LCK-2:** The system MUST unlock a locked user account after a short while.
EOF_0
cat > specs/login.review.md <<'EOF_1'
---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: specs/login.md
cfsync-plugin: ignore-push
---

# SRD Review — Login Token Validation

## Errata

- [ ] #4 [minor, linguistic] GR-1 uses British spelling: `unauthorised` →
  `unauthorized`. (SRD:house)

- [ ] #7 [minor, linguistic] GR-3 uses an open form: `can not` → `cannot`.
  (SRD:LANG-2)

- [ ] #9 [minor, linguistic] GR-2 misspells a word: `recieves` → `receives`.
  (SRD:LANG-2)

---

## Requirements

- [ ] #5 [major, verifiability] LCK-2: "after a short while" is vague — state
  the unlock delay. (SRD:REQ-6)
EOF_1
