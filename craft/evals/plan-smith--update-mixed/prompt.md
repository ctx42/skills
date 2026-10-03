---
tags: [case:plan-smith--update-mixed, skill:plan-smith, sec:plan-smith:usage, sec:plan-smith:self-learning, sec:plan-smith:format, sec:plan-smith:summary, sec:plan-smith:1-item-name-x, sec:plan-smith:3-item-name-x-rejected-one-line-reason, sec:plan-smith:n-remove-this-plan, sec:plan-smith:update-mode]
runs: 1
max_turns: 50
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  The user writes English; reply in English.
---

/craft:plan-smith update sso-plan.md — login flow and session storage are both done and merged. We're dropping the operator docs item, the platform team is folding SSO into their own runbook instead. Provider config hasn't been started. Also, staging showed we need a way to force-logout a user across every session, that wasn't in the plan.
