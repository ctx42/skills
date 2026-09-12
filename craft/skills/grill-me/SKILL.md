---
name: grill-me
description: >
  Interviews the user relentlessly about a plan until both reach a shared
  understanding. Use before building something, when the plan still has open
  questions, unstated assumptions, or conflicting choices — to pressure-test a
  plan, poke holes in an approach, interrogate a spec before coding, or draw
  out what someone knows about a topic before documenting it.
argument-hint: "[plan, approach, or topic to interrogate]"
license: MIT
---

# Grill Me

## Usage

```
/grill-me                             interview about the plan described so far in the conversation (default)
/grill-me <plan, approach, or topic>  interrogate the subject given as the argument
```

When invoked, switch into interviewer mode: question the user relentlessly,
branch by branch, until you both share one understanding of the subject.

## How It Works

1. Read the subject — from `$ARGUMENTS` when given (a plan, an approach, or a
   topic another skill hands over, such as a documentation gap), else the plan
   the user has described in the conversation so far.

2. Map the decision tree — every branch. For a build plan: architecture, data
   model, UX, edge cases, deployment, external deps. For a topic to document:
   the claim itself, its boundaries and exceptions, the context a reader needs,
   terms and synonyms.

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
   on decline, leave the summary in chat. When another skill invoked this one
   on a subject, skip the offer: the summary is that skill's input, so return
   to its flow.

## Rules

- Never assume. If something is ambiguous, ask.

- One topic at a time, in plain prose. Don't bundle unrelated questions, and
  never use `AskUserQuestion` multiple-choice unless the user asks for it.

- Push back. If a decision seems risky or contradictory, say so. When two
  decisions genuinely conflict, name the conflict, mark the earlier branch
  open again, and hold both until the user picks. Reconciling them yourself
  would record a choice they never made, so give the options, not a verdict.

- No implementation. Planning only; don't write code.

- Report tersely: no preamble or narration; state each fact once; don't
  restate output the user can already see. Restating a decision once to
  confirm it is the payload here — never pad it.

- Open on the payload: the branch map, the question, or the decision being
  confirmed. Never open by repeating back what the user asked for, or by
  announcing what you are about to do — they already know both, and it delays
  the only part of the turn they need. These rules are instructions to you,
  not lines to deliver: never quote a rule or its reasoning back to the user.

- Track progress. Keep the map of resolved vs. open branches and say how much
  is left when a branch closes.

## Self-learning

Obey this skill's lessons when it has any: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/grill-me.md` when this directory
is read-only. Most runs have none; absence is the normal case and needs no
comment. On a correction or self-caught mistake, append a one-line rule to
whichever path is writable, creating it, and report where.
