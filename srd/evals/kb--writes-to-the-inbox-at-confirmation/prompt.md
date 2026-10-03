---
tags: [case:kb--writes-to-the-inbox-at-confirmation, skill:kb, skill:create, sec:kb:boundaries, sec:kb:the-kb-folder, sec:kb:invocation, sec:kb:workflow, sec:kb:page-anatomy, sec:kb:output, ref:kb/retrieval-authoring, sec:create:documentation-corpus, sec:create:workflow, ref:create/project-config, ref:create/doc-corpus, ref:create/srd-procedures, ref:create/authoring-guide]
runs: 1
max_turns: 80
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.
  Before taking a scripted answer, write out in full, as your reply text, the
  message you would send the user at that point.

  Scripted answers (pick the one that fits the question):
  1. Objective: "Per-client request rate limiting at the API Gateway for
     external API clients. Put the SRD at specs/gateway.md."
  2. UI change: "No."
  3. In Scope: "Defer it; derive it from the requirements."
  4. Out of Scope: "Per-endpoint limits, billing and quotas, and internal
     clients (the front-end application and the mobile apps), which do not use
     API keys."
  5. Requirements: "Each external API client gets at most 600 requests per
     rolling 60-second window, counted per API key. The API Gateway already
     identifies each external API client by its API key, sent in the X-Api-Key
     request header, and each external client has exactly one active API key.
     Over the limit, the gateway rejects the request with HTTP 429 and a
     Retry-After header in whole seconds. A Super Admin can set a different
     limit per API key, from 1 to 6000 requests per minute."
  6. Requests with no API key or an unknown one: "Not in this SRD."
  7. Any restatement or summary to confirm: "Yes, correct."
  8. A proposed requirement grouping or prefixes: "Fine, use those."
  9. A self-check blocker: "Leave it."
  10. An offer to file documentation gaps: "File it."
---

/srd:create
