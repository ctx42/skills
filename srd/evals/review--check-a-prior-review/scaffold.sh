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
cat > specs/login.md <<'EOF_F0'
# Login Lockout

|                |                                                                           |
|----------------|---------------------------------------------------------------------------|
| **Objective**  | Define how the system locks a user account after repeated failed log-ins. |
| **Initiative** | [INT-412](https://jira.example.com/browse/INT-412)                        |
| **Owners**     | @alice, @bob                                                              |
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

**GR-3a:** The system MUST validate the session token of each log-in attempt.

**GR-3b:** The system MUST log each log-in attempt.

**GR-4:** The system MUST reject every log-in attempt for an account in Lockout, whatever the password entered.

**GR-5:** An account in Lockout is released by the system 30 minutes after
the account entered Lockout.

**GR-6:** The system MUST apply the same Lockout behavior to administrator
accounts as to all other accounts.

**GR-7:** The system MUST email the account owner when the account enters
Lockout.

**GR-8:** The system MUST keep the Lockout behaviour of an account when an
administrator changes its password.
EOF_F0
mkdir -p specs
cat > specs/login.review.md <<'EOF_F1'
---
prepared: 2026-09-20 10:00
updated: 2026-09-20 10:00
source: specs/login.md
cfsync-plugin: ignore-push
---

# SRD Review — Login Lockout

## Errata

- [ ] #3 [minor, linguistic] GR-6 and GR-8 use British spelling:
  `behaviour` → `behavior`. (SRD:house)

---

## Scope

- [ ] #1 [blocker, coverage] SC-2: no requirement covers this In Scope item —
  add a requirement that emails the account owner. (SRD:SCO-2)

## Requirements

- [ ] #2 [blocker, atomicity] GR-3a: states two rules ("validate ... and log
  ...") — split into one rule each. (SRD:REQ-1)

- [ ] #4 [major, linguistic] GR-5: passive voice ("is released by the
  system") — restate with the system as subject. (SRD:LANG-1)

- [ ] #5 [minor, format] GR-4 runs past 80 columns — wrap the line. (SRD:MD-2)
EOF_F1
