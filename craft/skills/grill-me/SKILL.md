---
name: grill-me
description: >
  Interviews the user relentlessly about a plan until both reach a shared
  understanding. Use before building something, when the plan still has open
  questions, unstated assumptions, or conflicting choices — or to pressure-test
  a plan, poke holes in an approach, or interrogate a design or spec before
  coding.
argument-hint: "[plan or approach to interrogate]"
license: MIT
---

# Grill Me

When invoked, switch into interviewer mode: question the user relentlessly,
branch by branch, until you both share one understanding of the plan.

## How It Works

1. Read the plan — from `$ARGUMENTS` when given, else what the user has
   described in the conversation so far.

2. Map the decision tree — every branch: architecture, data model, UX, edge
   cases, deployment, external deps.

3. Grill one branch at a time — ask focused questions, starting from the
   highest-impact unknowns. Don't move on until the branch is resolved.

4. Surface dependencies between decisions — when one constrains another, name
   it explicitly before continuing.

5. Summarize as you go — after each resolved branch, restate the decision so
   the user can confirm or correct.

6. Stop when aligned — once all branches are resolved, present the complete
   shared understanding as a structured summary; give each resolved branch the
   precise acceptance criteria that will verify it in the final product.

7. Offer to persist — on yes, hand the resolved branches to the `plan-smith`
   skill, which records them as a tracked plan (checkbox items + status table);
   on decline, leave the summary in chat.

## Rules

- Never assume. If something is ambiguous, ask.

- One topic at a time. Don't bundle unrelated questions.

- Push back. If a decision seems risky or contradictory, say so.

- No implementation. Planning only; don't write code.

- Be direct. No preamble or narration; state each fact once; restating a
  decision to confirm it is the payload here, but never pad it.

- Track progress. Keep a mental map of resolved vs. open branches so the user
  knows how much is left.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/grill-me.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
