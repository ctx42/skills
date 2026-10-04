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
| **Status**     | [[!ACCEPTED\|color=green;style=bold]]                 |
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

**GR-1:** The system MUST reject an API request that carries no Login Token with
HTTP status 401.

**GR-2:** The system MUST reject an API request whose Login Token has expired
with HTTP status 401.

**GR-3:** The system MUST reject an API request whose Login Token signature is
invalid with HTTP status 401.

**GR-4:** The system MUST reject an API request whose Login Token was revoked
with HTTP status 401.

**GR-5:** The system MUST reject an API request whose Login Token was issued for
another API Gateway with HTTP status 401.

**GR-6:** The system MUST answer an API request that carries an expired Login
Token with HTTP status 401.

**GR-7:** The system MUST log each rejected API request with its HTTP status.

**GR-8:** The system MUST NOT log the Login Token itself.

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

## Requirements

- [ ] #3 [major, redundancy] GR-6 states the same rule as GR-2 (an expired
  Login Token gets HTTP status 401) — remove GR-6. (SRD:consistency)
EOF_1
