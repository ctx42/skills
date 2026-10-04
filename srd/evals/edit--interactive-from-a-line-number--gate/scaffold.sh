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

This document specifies how the API Gateway checks the Login Token that
accompanies each API request, and how it locks a user account after repeated
failed sign-in attempts. It does not cover how Login Tokens are issued or
refreshed.

## Glossary

### Login Token

A signed credential that identifies a signed-in user for a limited time.

### Audit Record

A stored entry that describes one sign-in attempt for later inspection.

## Scope

### In Scope

**SC-1:** Validation of the Login Token on every API request.

**SC-2:** Lockout of a user account after repeated failed sign-in attempts.

**SC-3:** An Audit Record for every sign-in attempt.

### Out of Scope

**OSC-1:** Issuing and refreshing Login Tokens.

## Requirements

### Audit

**AUD-1:** The system MUST include the user identifier in the Audit Record of
each sign-in attempt.

**AUD-2:** The system MUST include the time in UTC in the Audit Record of each
sign-in attempt.

**AUD-3:** The system MUST include the source IP address in the Audit Record of
each authorisation attempt.

**AUD-4:** The system MUST include the user agent string in the Audit Record of
each sign-in attempt.

**AUD-5:** The system MUST include the result code in the Audit Record of each
sign-in attempt.

**AUD-6:** The system MUST include the Login Token identifier in the Audit
Record of each sign-in attempt.

**AUD-7:** The system MUST include the request path in the Audit Record of each
sign-in attempt.

**AUD-8:** The system MUST include the HTTP method in the Audit Record of each
sign-in attempt.

**AUD-9:** The system MUST include the response status in the Audit Record of
each sign-in attempt.

**AUD-10:** The system MUST include the client application identifier in the
Audit Record of each sign-in attempt.

**AUD-11:** The system MUST include the API Gateway node name in the Audit
Record of each sign-in attempt.

**AUD-12:** The system MUST include the request identifier in the Audit Record
of each sign-in attempt.

**AUD-13:** The system MUST include the tenant identifier in the Audit Record of
each sign-in attempt.

**AUD-14:** The system MUST include the session identifier in the Audit Record
of each sign-in attempt.

**AUD-15:** The system MUST include the failure reason in the Audit Record of
each sign-in attempt.

**AUD-16:** The system MUST include the token issuer in the Audit Record of each
sign-in attempt.

**AUD-17:** The system MUST include the token audience in the Audit Record of
each sign-in attempt.

**AUD-18:** The system MUST include the token expiry time in the Audit Record of
each sign-in attempt.

**AUD-19:** The system MUST include the signing key identifier in the Audit
Record of each sign-in attempt.

**AUD-20:** The system MUST include the request size in bytes in the Audit
Record of each sign-in attempt.

**AUD-21:** The system MUST include the response time in milliseconds in the
Audit Record of each sign-in attempt.

**AUD-22:** The system MUST include the TLS protocol version in the Audit Record
of each sign-in attempt.

**AUD-23:** The system MUST include the client certificate fingerprint in the
Audit Record of each sign-in attempt.

**AUD-24:** The system MUST include the geographic region of the source IP
address in the Audit Record of each sign-in attempt.

**AUD-25:** The system MUST include the number of the attempt within the current
lockout window in the Audit Record of each sign-in attempt.

**AUD-26:** The system MUST include the API version requested in the Audit
Record of each sign-in attempt.

**AUD-27:** The system MUST include the identity provider name in the Audit
Record of each sign-in attempt.

**AUD-28:** The system MUST include the authentication method in the Audit
Record of each sign-in attempt.

**AUD-29:** The system MUST include the correlation identifier in the Audit
Record of each sign-in attempt.

**AUD-30:** The system MUST include the forwarding proxy address in the Audit
Record of each sign-in attempt.

**AUD-31:** The system MUST include the account lock state in the Audit Record
of each sign-in attempt.

**AUD-32:** The system MUST include the count of prior failures in the Audit
Record of each sign-in attempt.

**AUD-33:** The system MUST include the time the Login Token was issued in the
Audit Record of each sign-in attempt.

**AUD-34:** The system MUST include the scope list of the Login Token in the
Audit Record of each sign-in attempt.

**AUD-35:** The system MUST include the device identifier in the Audit Record of
each sign-in attempt.

**AUD-36:** The system MUST include the operating system name in the Audit
Record of each sign-in attempt.

**AUD-37:** The system MUST include the locale of the request in the Audit
Record of each sign-in attempt.

**AUD-38:** The system MUST include the referring host in the Audit Record of
each sign-in attempt.

**AUD-39:** The system MUST include the retry counter in the Audit Record of
each sign-in attempt.

**AUD-40:** The system MUST include the audit schema version in the Audit Record
of each sign-in attempt.

**AUD-41:** The system MUST include the build number of the API Gateway in the
Audit Record of each sign-in attempt.

**AUD-42:** The system MUST include the data center name in the Audit Record of
each sign-in attempt.

**AUD-43:** The system MUST include the network zone of the source in the Audit
Record of each sign-in attempt.

**AUD-44:** The system MUST include the rate limit bucket in the Audit Record of
each sign-in attempt.

**AUD-45:** The system MUST include the consent version in the Audit Record of
each sign-in attempt.

**AUD-46:** The system MUST include the password age in days in the Audit Record
of each sign-in attempt.

### Gateway Rules

**GR-1:** The system MUST reject an API request that carries no Login Token with
HTTP status 401.

**GR-2:** The system MUST reject an API request whose Login Token has expired
with HTTP status 401.

**GR-3:** The system MUST reject an API request whose Login Token signature is
invalid with HTTP status 401.

**GR-4a:** The system MUST check the Login Token signature against the current
signing key of the identity service.

**GR-4b:** The system MUST fetch a new signing key from the identity service
promptly whenever the identity service publishes one, so that a Login Token
signed with the new key is accepted by the API Gateway from the moment it is
first presented by any client application on any API Gateway node.

**GR-5:** The system must reject an API request whose Login Token was revoked
with HTTP status 401.

### Account Lockout

**LCK-1:** The system MUST lock a user account after 5 consecutive failed
sign-in attempts.

**LCK-2:** The system MUST unlock a locked user account after a reasonable time.
EOF_0
