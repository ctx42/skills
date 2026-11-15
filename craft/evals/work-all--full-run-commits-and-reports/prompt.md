---
tags: [case:work-all--full-run-commits-and-reports, skill:work-all, needs-shell, sec:work-all:usage, sec:work-all:work-files, sec:work-all:1-discover, sec:work-all:2-plan-and-ask-before-any-dispatch, fan-out, long, sec:work-all:3-dispatch, sec:work-all:4-while-workers-run, sec:work-all:5-run-file, sec:work-all:6-report, ref:work-all/worker]
runs: 1
max_turns: 80
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Edit, Write, Agent, SendMessage, Bash(git:*), Bash(go:*), Bash(gofmt:*), Bash(find:*), Bash(ls:*), Bash(mkdir:*), Bash(rm:*), Bash(nproc:*), Bash(uptime:*), Bash(free:*), Bash(systemd-run:*), Bash(command:*), Bash(date:*), Bash(exit:*)]
append_system_prompt: |
  The user writes English; reply in English.

  Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue.

  1. Skip nothing; run every unit and item as you propose.
  2. For any other question, take your own recommendation.
---

/craft:work-all
