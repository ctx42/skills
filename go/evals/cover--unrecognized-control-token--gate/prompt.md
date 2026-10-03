---
tags: [case:cover--unrecognized-control-token--gate, skill:cover, sec:cover:target, sec:cover:controls, sec:cover:plan-file-package-module, needs-shell]
runs: 1
max_turns: 80
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(go:*), Bash(gofmt:*), Bash(mkdir:*), Bash(awk:*), Bash(rm:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:cover ./pkg/svc only=exported max_tests=4
