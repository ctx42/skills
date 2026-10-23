#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/guidelines_for_software_requirements_documents.md
glossary: docs/glossary
precedence:
  - kb
  - docs/concepts
  - docs/api-gateway
  - docs/operations
  - docs/glossary
---

# Project configuration (eval fixture)

EVAL TEST DATA ONLY. Copy this file to the root of a scenario's workspace so
the srd skills' gate finds a project; a scenario's `setup` overrides any key.
In an eval run, `srd/evals/mocks/srd/fixtures/srd-standard.md` stands in for the
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

**GR-2:** The system MUST reject an API request whose Login Token expired more
than 30 seconds ago with HTTP status 401.

**GR-3:** The system MUST reject an API request whose Login Token signature is
invalid with HTTP status 401.

### Account Lockout

**LCK-1:** The system MUST lock a user account after 5 consecutive failed
sign-in attempts.

**LCK-2:** The system MUST unlock a locked user account 15 minutes after it was
locked.
EOF_0
cat > specs/login.decisions.md <<'EOF_1'
# Changes — Login Token Validation

## 2026-09-30 15:20

### Requirements

LCK-2 now unlocks a locked user account 15 minutes after it was locked,
instead of "after a short while".
Reason: "a tester can wait 15 minutes and check."

GR-2 now rejects a Login Token that expired more than 30 seconds ago, instead
of 60 seconds.
Reason: "security asked for a shorter grace."

GR-3 now has the system as its subject: "The system MUST reject …" instead of
"An API request … MUST be rejected".
Reason: "this makes the system the subject."

## 2026-09-30 09:10

### Requirements

GR-1 now rejects an API request that carries no Login Token, instead of "an
unauthorised API request".
Reason: "names a condition a tester can create."

GR-2 now rejects a Login Token only once it expired more than 60 seconds ago.
Reason: "client clocks drift."

## 2026-09-29

### Requirements

LCK-2 was added: the system unlocks a locked user account after a short while.
Reason: "accounts must not stay locked forever."
EOF_1
cat > specs/login.review.md <<'EOF_2'
---
prepared: 2026-09-28 10:00
updated: 2026-09-28 10:00
source: specs/login.md
---

# SRD Review — Login Token Validation

## Requirements

- [ ] #12 [major, verifiability] LCK-1: "consecutive" does not say whether a
  successful sign-in resets the count — state it. (SRD:REQ-5)

---

## Resolved

- [x] #3 [blocker, coverage] SC-2: no requirement says when a locked account
  unlocks — add one. (SRD:SCO-2) — added LCK-2.

- [x] #5 [blocker, verifiability] GR-1: "unauthorised" names no condition a
  tester can create — state it. (SRD:REQ-5) — GR-1 now names a request with no
  Login Token.

- [x] #6 [major, logical] GR-2: a client whose clock runs behind sees fresh
  Login Tokens rejected — state the tolerance. (SRD:consistency) — GR-2 now
  allows a grace period after expiry.

- [x] #8 [major, verifiability] LCK-2: "after a short while" is vague — state
  the unlock delay. (SRD:REQ-6) — LCK-2 now unlocks after 15 minutes.

- [x] #10 [major, linguistic] GR-3: "MUST be rejected" is passive — rewrite with
  "the system" as subject. (SRD:LANG-1) — GR-3 now has the system as subject.

---

## Withdrawn

- #2 [minor, terminology] Login Token is defined twice (withdrawn: one entry,
  confirmed by author).

- #4 [major, redundancy] GR-1 and GR-2 overlap (withdrawn 2026-09-30 09:30:
  distinct conditions, confirmed by author).

- #9 [minor, format] LCK-1: a trailing space after the word "attempts"
  (withdrawn 2026-09-30 15:40: the sync restores it).
EOF_2
