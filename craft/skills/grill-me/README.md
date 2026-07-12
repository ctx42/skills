# grill-me

A planning interview skill. When invoked, the agent switches into interviewer
mode and questions you relentlessly about every part of your plan until you both
share the same understanding. It walks the design tree one branch at a time
(architecture, data model, UX, edge cases, deployment, dependencies), resolving
the dependencies between decisions before moving on.

Use it before building something, while the plan still has open questions,
unstated assumptions, or choices that might conflict.

## When to Use

- Starting a non-trivial feature, refactor, or new tool.

- You have a rough idea but the details are not pinned down.

- You want risky or contradictory decisions surfaced early.

## How It Works

1. Reads your plan and maps the decision tree.

2. Grills one branch at a time, starting with the highest-impact unknowns.

3. Names dependencies between decisions explicitly.

4. Restates each resolved decision so you can confirm or correct it.

5. Stops when everything is aligned and presents a structured summary with
   acceptance criteria per decision, then offers to hand it to `plan-smith` as a
   tracked plan.

## Usage

```
/grill-me
```

Then describe the plan you want interrogated. The skill does not write code —
it is for planning only.

## What to Expect

- Direct, focused questions — one topic at a time, no bundling.

- Push-back when a choice looks risky or inconsistent.

- A running sense of how many branches are resolved versus still open.

## Evaluations

### 1. Vague plan

Request: `/grill-me` then "I want to add caching to the API."

Expected behavior:

- Maps the decision tree (what to cache, invalidation, store, TTL, keys).

- Asks the highest-impact unknown first, one topic at a time — no bundled
  questions.

- Does not start designing or writing code.

### 2. Contradictory choices

Request: Earlier in the interview the user set "the app must work fully
offline," and now, on a later branch, says "every save syncs to the server
immediately for real-time collaboration."

Expected behavior:

- Connects the two separately-stated decisions and names the conflict
  (offline-first vs. immediate server sync) — not just an obvious oxymoron.

- Does not silently pick one; holds both branches open until the user resolves
  the tension.

### 3. Alignment reached

Request: All branches have been answered.

Expected behavior:

- Stops interviewing.

- Presents the complete shared understanding as a single structured summary,
  each resolved branch carrying its acceptance criteria.

- Offers to hand the result to `plan-smith` as a tracked plan; writes nothing
  without a yes.

- Writes no implementation code.

### 4. Terse output

Request: Any point during the interview.

Expected behavior:

- No pleasantries, preamble, or narration; each turn opens with the question or
  the decision.

- Restating a resolved decision to confirm it is allowed (that is the payload
  here), but it is never padded or repeated once confirmed.
