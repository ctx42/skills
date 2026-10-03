---
tags: [case:style--test-rules-inherit-production, skill:style, sec:style:production, sec:style:test, sec:style:self-learning]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, LSP, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
  This project's Go conventions live in the go:style skill; load it
  before editing any .go file.
  Earlier in this session you added Service.Close. The user wants the
  tests to include a table test and a small test helper, and the helper
  itself tested too.
---

Write tests for Service.Close in service_test.go
