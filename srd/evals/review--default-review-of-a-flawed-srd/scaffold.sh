#!/usr/bin/env bash
set -euo pipefail
cat > project-config.md <<'EOF_PC'
---
mcp-server: srd
kb: kb
initiatives: initiatives
srd-standard: docs/srd-standard.md
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
cat > specs/login.md <<'EOF_F0'
# Login Lockout

| Field      | Value                                                                     |
|------------|---------------------------------------------------------------------------|
| Summary    | Define how the system locks a user account after repeated failed log-ins. |
| Maintainer | @alice                                                                    |
| Reviewers  | @bob                                                                      |
| Tracking   | [WORK-412](https://tracker.example.com/WORK-412)                          |
| Lifecycle  | DRAFT                                                                     |
| Mockups    | none                                                                      |

## Introduction

This document specifies how the system protects user accounts against
repeated failed log-in attempts: counting failed attempts, locking an
account, and releasing it again. It does not change how users reset a
password.

## Conventions

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Boundaries

### Included

- Counting failed log-in attempts per user account.
- Emailing the account owner when the account enters Lockout.
- Releasing an account from Lockout.

### Excluded

- Password reset.

## Terms

### Lockout

The state of a user account that cannot log in until it is released.

## Requirements

---

### Lockout (LCK)

- `LCK-1` The system MUST count each failed log-in attempt against the user
  account it names.
- `LCK-2` The system MUST reset an account's failed-attempt count to zero
  after a successful log-in.
- `LCK-3` The system MUST put an account into Lockout after five consecutive
  failed log-in attempts.
- `LCK-4` The system SHALL validate the token and log the attempt.
- `LCK-5` The system MUST reject every log-in attempt for an account in
  Lockout.
- `LCK-6` The system MUST release an account from Lockout 30 minutes after
  the account entered Lockout.
- `LCK-7` The system MUST apply the same Lockout behaviour to administrator
  accounts as to all other accounts.

---
EOF_F0
