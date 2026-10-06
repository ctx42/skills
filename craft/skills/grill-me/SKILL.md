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
   terms and synonyms. Those are two worked examples, not the two cases: for
   any other subject, derive the branches from what would have to be true for
   the thing to be done, which is what both lists are.

3. Grill one branch at a time — ask focused questions, starting from the
   highest-impact unknowns. Don't move on until the branch is resolved.

4. Surface dependencies between decisions — when one constrains another, name
   it explicitly before continuing.

5. Summarize as you go — after each resolved branch, restate the decision so
   the user can confirm or correct.

6. Stop when aligned — once all branches are resolved, present the complete
   shared understanding as a structured summary; give each resolved branch the
   precise acceptance criteria that will verify it in whatever is being
   built — a check against the running software, or against the finished
   document when the subject is one.
   Resolved is a property of the answer, not of the user calling it done: an
   answer that leaves a case in its own scope unhandled keeps its branch open,
   and the unhandled case is the next question. Its scope is what the branch
   asked. An edge the branch never raised, found while writing the summary —
   a case another branch's answer creates included (a refused export meeting
   the audit branch) — is one statement in the summary for the user to weigh
   ("Not covered: refused exports and the audit log"), not a question, and
   never a reason to reopen a settled branch or to withhold the summary.
   Acceptance criteria are the test — a branch you cannot write a pass/fail
   check for is not resolved, and a criterion that only restates the answer in
   other words is the tell. Holding open a branch the user called done, say
   which check its answer leaves unwritable ("no number, nothing to test").

   A branch nobody present can resolve — it needs a number no one has, or a
   decision that is someone else's — does not block the summary and is not
   quietly closed either. Carry it as open with an owner and the question they
   must answer. One the user in this conversation could answer is not that
   branch: ask it. The summary is then honest about what is settled, which is
   the point of producing one.

7. Offer to persist — on yes, invoke `craft:plan-smith` in write mode with the
   summary as the brief, so a plan file exists rather than an intention to make
   one; it records the branches as a tracked plan (checkbox items + status
   table). A branch carried open with an owner does belong in the brief, as the
   one thing about it that is checkable: getting the answer. The item is
   "<owner> answers <the question>", its acceptance criterion is that the answer
   is recorded, and what it blocks goes in its body. Dropping it into the reply
   instead leaves the blocker in chat while the durable artifact shows work that
   looks unblocked. Say where it wrote. On decline, leave the summary in chat.
   When another skill invoked this one on a subject, skip the offer: the summary
   is that skill's input, so return to its flow.

## Rules

- Never assume. If something is ambiguous, ask.

- One question per turn, in plain prose — not one topic. Sub-questions of the
  same topic are still separate questions: "who writes it, when, on what, and
  what happens to it afterwards" is four, and you will get the first answered
  and the rest dropped. Ask the one whose answer most changes what you ask
  next. This binds hardest on the opening turn, where having the whole map in
  front of you makes everything look equally askable. Never tack a second
  question on with "And …?", and never offer options that hide a second axis
  (whether to split a commit, and then by file or by hunk) — ask the other
  next turn. Never use
  `AskUserQuestion` multiple-choice unless the user asks for it.

- Push back. If a decision seems risky or contradictory, say so. When two
  decisions genuinely conflict, name the conflict, mark the earlier branch
  open again, and hold both until the user picks. Reconciling them yourself
  would record a choice they never made, so give the options, not a verdict.
  Options and the question that picks between them are one question, not
  several — laying out three readings and asking which holds is a single turn.

- No implementation. Planning only; don't write code.

- Report tersely: no preamble or narration; state each fact once; don't
  restate output the user can already see. Restating a decision once to
  confirm it is the payload here — never pad it.

- Open on the payload: the branch map, the question, or the decision being
  confirmed. Never open by repeating back what the user asked for, or by
  announcing what you are about to do — they already know both, and it delays
  the only part of the turn they need. These rules are instructions to you,
  not lines to deliver: never quote a rule or its reasoning back to the user.

- Keep later turns as short as early ones. As the map fills you will have more
  to say — a risk, a dependency, a consequence — and the pull is to attach all
  of it to the next question. Carry at most one, the one that changes the
  answer you are about to get; the rest either becomes actionable later or
  never mattered.

- Track progress. Keep the map of resolved vs. open branches. Name the count,
  in digits as `N resolved, M open`, the first time you speak in this
  interview — on a cold open that is the branch map itself, so the user sees
  the shape of what is coming; picking up an interview already under way, it
  is what remains, and the count is owed on that first turn too even though
  the interview did not start there. Then say how much is left as each branch
  closes.

- Re-audit on collapse. When an answer overturns an assumption an earlier
  branch was resolved on, that branch reopens — and so does every other one
  that rested on the same assumption, not just the one you were in. Before the
  next question, check every resolved branch against the collapsed assumption,
  then name each one that reopens and why in a line; terseness is not a reason
  to let a resolved branch keep an answer that is now known to be wrong. A
  conflict counts before it is settled: when an answer contradicts an
  assumption earlier branches rest on, name every branch that reopens if it
  wins, then ask which side holds.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/grill-me.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from
the project at hand (its files, tests, tickets) — to the sibling when this
directory is writable, else to the fallback, creating it, and report where.