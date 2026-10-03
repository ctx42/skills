---
tags: [case:kb--writes-to-the-inbox-at-confirmation--gate, skill:kb, skill:create, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, sec:create:documentation-corpus, sec:create:workflow, ref:create/project-config, ref:create/doc-corpus, ref:create/srd-procedures, ref:create/authoring-guide]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/srd:create Per-client request rate limiting at the API Gateway for external API clients, written to specs/gateway.md. The API Gateway already identifies each external API client by its API key, sent in the X-Api-Key request header, and each external client has exactly one active API key.
