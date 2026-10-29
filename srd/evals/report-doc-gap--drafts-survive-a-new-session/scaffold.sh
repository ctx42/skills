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
cat > specs/gateway.md <<'EOF_SRD'
# Gateway Failure Reporting

| Field      | Value                                                               |
|------------|---------------------------------------------------------------------|
| Summary    | Define how the system reports failed upstream calls to API clients. |
| Maintainer | @dana                                                               |
| Reviewers  | @erik                                                               |
| Tracking   | [ABC-530](https://tickets.example.com/browse/ABC-530)               |
| Lifecycle  | DRAFT                                                               |
| Mockups    | none                                                                |

## Introduction

This document specifies how the system answers an API client when the
upstream service behind the API Gateway fails or does not answer. It does not
change the API Gateway's retry policy.

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in RFC 2119 and RFC 8174 when, and only when, they
appear in all capitals, as shown here.

## Boundaries

### Included

- Answering an API client when its upstream call fails.
- Logging failed upstream calls.

### Excluded

- Changing the API Gateway's retry policy.

## Terms

### Request ID

The identifier the API Gateway assigns to one client request.

## Requirements

### Gateway (GW)

- `GW-1` The system MUST answer HTTP 502 when an upstream call fails after the
  API Gateway's retries.
- `GW-2` The system MUST log each of the API Gateway's 3× retries of a failed
  upstream call.
- `GW-3` The system MUST log each failed upstream call with the host name of
  the upstream service.
- `GW-4` The system MUST put the request's Request ID in the body of each HTTP
  502 answer.
EOF_SRD
