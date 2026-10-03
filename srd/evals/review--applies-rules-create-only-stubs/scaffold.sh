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
cat > specs/api.md <<'EOF_F0'
# API Key Management

|                |                                                                                     |
|----------------|-------------------------------------------------------------------------------------|
| **Objective**  | Let Project Admins manage their Project's API keys in the web application.          |
| **Initiative** | N/A                                                                                 |
| **Owners**     | @carol                                                                              |
| **Status**     | ACCEPTED                                                                            |
| **Designs**    | [API Keys page — draft, not approved](https://figma.example.com/file/apikeys-draft) |

> [!INFO]
> The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
> "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
> document are to be interpreted as described in
> [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
> [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
> appear in all capitals, as shown here.

## Introduction

This document specifies the API Keys page of the web application, where a
Project Admin creates and revokes the API keys of a Project.

## Glossary

### Project Admin

A user who administers one Project.

### API Key

A secret string that identifies one external client of a Project.

## Scope

### In Scope

**SC-1:** Creating an API Key on the API Keys page.

**SC-2:** Revoking an API Key on the API Keys page.

### Out of Scope

**OSC-1:** Automatic rotation of API Keys.

## Requirements

### API Keys Page (KEY)

**KEY-1:** The system MUST show an API Keys page in the Project settings.

**KEY-2:** The system MUST let a Project Admin create an API Key on the API
Keys page.

**KEY-3:** The system MUST let a Project Admin revoke an API Key on the API
Keys page.

**KEY-4:** The system MUST reject a request that carries a revoked API Key
with HTTP 401.
EOF_F0
