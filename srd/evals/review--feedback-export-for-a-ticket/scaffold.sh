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
cat > specs/login.md <<'EOF_F0'
# Login Lockout

|                |                                                                           |
|----------------|---------------------------------------------------------------------------|
| **Objective**  | Define how the system locks a user account after repeated failed log-ins. |
| **Initiative** | [INT-412](https://jira.example.com/browse/INT-412)                        |
| **Owners**     | @alice                                                                    |
| **Status**     | IN PROGRESS                                                               |
| **Designs**    | N/A                                                                       |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the system protects user accounts against
repeated failed log-in attempts: counting failed attempts, locking an
account, and releasing it again.

## Glossary

### Lockout

The state of a user account that cannot log in until it is released.

## Scope

### In Scope

**SC-1:** Counting failed log-in attempts per user account.

**SC-2:** Emailing the account owner when the account enters Lockout.

**SC-3:** Releasing an account from Lockout.

### Out of Scope

**OSC-1:** Password reset.

## Requirements

### General (GR)

**GR-1:** The system MUST count each failed log-in attempt against the user
account it names.

**GR-2:** The system MUST reset an account's failed-attempt count to zero
after a successful log-in.

**GR-3:** The system MUST put an account into Lockout after five consecutive
failed log-in attempts.

**GR-3a:** The system SHALL validate the token and log the attempt.

**GR-4:** The system MUST reject every log-in attempt for an account in
Lockout.

**GR-5:** The system MUST quickly release an account from Lockout.

**GR-6:** The system MUST apply the same Lockout behaviour to administrator
accounts as to all other accounts.

**GR-7:** The system MUST email the account owner when the account enters
Lockout.

**GR-8:** The system MUST show a red colour on the Lockout banner.
EOF_F0
mkdir -p specs
cat > specs/login.review.md <<'EOF_F1'
---
prepared: 2026-09-20 10:00
updated: 2026-09-22 15:30
source: specs/login.md
cfsync-plugin: ignore-push
---

# SRD Review — Login Lockout

## Errata

- [ ] #6 [minor, linguistic] GR-6 uses British spelling: `behaviour` →
  `behavior`. (SRD:house)

- [ ] #7 [minor, linguistic] GR-8 uses British spelling: `colour` → `color`.
  (SRD:house)

---

## Metadata

- [ ] #2 [blocker, structure] Metadata (Owners): only one owner is listed —
  add a secondary owner. (SRD:STR-2)

## Requirements

- [ ] #4 [blocker, atomicity] GR-3a: states two rules ("validate ... and log
  ...") — split into one rule each. (SRD:REQ-1)

- [ ] #5 [major, verifiability] GR-5: "quickly" is a vague quality — state a
  measurable limit. (SRD:REQ-6)

---

## Resolved

- [x] #1 [blocker, coverage] SC-2: no requirement covered this In Scope item —
  added GR-7. (SRD:SCO-2)

---

## Withdrawn

- #3 [major, redundancy] GR-2 seemed to overlap GR-4 (withdrawn: distinct
  triggers, confirmed by author).
EOF_F1
