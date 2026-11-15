---
tags: [case:work-all--upfront-round-before-work, skill:work-all, needs-shell, sec:work-all:usage, sec:work-all:work-files, sec:work-all:1-discover, sec:work-all:2-plan-and-ask-before-any-dispatch]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Agent, SendMessage, Bash(git:*), Bash(go:*), Bash(gofmt:*), Bash(find:*), Bash(ls:*), Bash(mkdir:*), Bash(rm:*), Bash(nproc:*), Bash(uptime:*), Bash(free:*), Bash(systemd-run:*), Bash(command:*), Bash(date:*), Bash(exit:*)]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:work-all
