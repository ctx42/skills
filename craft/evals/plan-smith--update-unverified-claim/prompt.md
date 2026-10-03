---
tags: [case:plan-smith--update-unverified-claim, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning, sec:plan-smith:format, sec:plan-smith:summary, sec:plan-smith:1-item-name-x, sec:plan-smith:3-item-name-x-rejected-one-line-reason, sec:plan-smith:n-remove-this-plan, sec:plan-smith:update-mode]
runs: 1
max_turns: 40
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:plan-smith update rate-limit-plan.md — the Redis counters and the 429 responses both landed, mark them done.
