---
tags: [case:cover--missing-test-family-is-not-zero-percent, skill:cover, sec:cover:target, sec:cover:per-function-loop, sec:cover:classify-each-uncovered-line, sec:cover:write, sec:cover:verify, sec:cover:output, skill:style, sec:style:test, sec:style:production, needs-shell]
runs: 1
max_turns: 80
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash(go:*), Bash(gofmt:*), Bash(mkdir:*), Bash(awk:*), Bash(rm:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/go:cover func=Normalize
