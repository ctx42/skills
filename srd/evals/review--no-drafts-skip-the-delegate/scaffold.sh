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

**SC-2:** Putting an account into Lockout.

**SC-3:** Releasing an account from Lockout.

### Out of Scope

**OSC-1:** Password reset.

## Requirements

### General (GR)

**GR-1:** The system MUST count each failed log-in attempt against the user
account it names.

**GR-2:** The system MUST reset an account's failed-attempt count to zero
after a successful log-in.

**GR-2:** The system MUST put an account into Lockout after five consecutive
failed log-in attempts.

**GR-3:** Every log-in attempt for an account in Lockout MUST be rejected
without counting it as a failed log-in attempt.

**GR-4:** An account in Lockout MUST be released 30 minutes after it entered
Lockout.

**GR-5:** The system MUST reset an account's failed-attempt count to zero
when it releases the account from Lockout.
EOF_F0
