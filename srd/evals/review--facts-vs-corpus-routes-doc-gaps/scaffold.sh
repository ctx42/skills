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
mkdir -p specs
cat > specs/gateway.md <<'EOF_F0'
# Gateway Failure Reporting

|                |                                                                     |
|----------------|---------------------------------------------------------------------|
| **Objective**  | Define how the system reports failed upstream calls to API clients. |
| **Initiative** | [INT-530](https://jira.example.com/browse/INT-530)                  |
| **Owners**     | @dana, @erik                                                        |
| **Status**     | IN PROGRESS                                                         |
| **Designs**    | N/A                                                                 |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies how the system answers an API client when the
upstream service behind the API Gateway fails or does not answer.

## Glossary

### Correlation ID

The identifier the API Gateway assigns to one client request.

## Scope

### In Scope

**SC-1:** Answering an API client when its upstream call fails.

**SC-2:** Answering an API client when its upstream call times out.

### Out of Scope

**OSC-1:** Changing the API Gateway's retry policy.

## Requirements

### Gateway (GW)

**GW-1:** The system MUST answer HTTP 502 when an upstream call fails after
the API Gateway's retries.

**GW-2:** The system MUST log each of the API Gateway's 3× retries of a
failed upstream call.

**GW-3:** The system MUST log each failed upstream call with the host name
of the upstream service.

**GW-4:** The system MUST put the request's Correlation ID in the body of
each HTTP 502 answer.

**GW-5:** The system MUST answer HTTP 504 when the upstream service does not
answer within the API Gateway's upstream timeout of 10 seconds.
EOF_F0
