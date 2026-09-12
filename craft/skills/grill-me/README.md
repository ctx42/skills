# grill-me

A planning interview: the agent questions you relentlessly, one branch of the
decision tree at a time, until you both share the same understanding.

## Usage

```
/grill-me                             interview about the plan described so far in the conversation (default)
/grill-me <plan, approach, or topic>  interrogate the subject given as the argument
```

Other skills invoke it the same way, passing the subject as the argument —
`srd:report-doc-gap` (heavy-mode gap extraction) and `srd:backlog` (filling a
gap cluster) hand over a documentation gap and get the structured summary back
in their own flow, with no plan-smith handoff.

## When to Use

- Starting a non-trivial feature, refactor, or new tool.

- You have a rough idea but the details are not pinned down.

- You want risky or contradictory decisions surfaced early.

- You know something a document must state and want it drawn out completely
  before it is written.

## How It Works

1. Reads the subject — the argument when given, else the plan from the
   conversation — and maps the decision tree: architecture, data model, UX,
   edge cases, deployment, dependencies for a build plan; the claim, its
   boundaries, reader context, and terminology for a topic to document.

2. Grills one branch at a time, starting with the highest-impact unknowns.

3. Names dependencies between decisions explicitly.

4. Restates each resolved decision so you can confirm or correct it, and says
   how many branches remain.

5. Stops when everything is aligned and presents a structured summary with
   acceptance criteria per decision, then offers to hand it to `plan-smith` as a
   tracked plan (skipped when another skill invoked it).

## What to Expect

- Direct, focused questions — one topic at a time, no bundling.

- Pushback when a choice looks risky or inconsistent.

- No code and no design work — planning only.

## Evaluations

### 1. Vague plan

Request: `/grill-me` then "I want to add caching to the API."

Expected behavior:

- Maps the decision tree (what to cache, invalidation, store, TTL, keys).

- Asks the highest-impact unknown first, one topic at a time — no bundled
  questions.

- Does not start designing or writing code.

### 2. Subject supplied by a caller

Request: `srd:report-doc-gap`, in heavy mode, invokes `craft:grill-me` with
the gap "the docs don't say what happens to an in-flight order when a station
goes offline" as the argument.

Expected behavior:

- Takes the subject from the argument, not from the surrounding conversation.

- Maps topic branches — the claim itself, its boundaries and exceptions, the
  context a reader needs, terms and synonyms — not build-plan branches such as
  deployment or UX.

- Ends with the structured summary and returns to the caller's flow; no
  `plan-smith` offer, no file written.

### 3. Contradictory choices

Request: Earlier in the interview the user set "the app must work fully
offline," and now, on a later branch, says "every save syncs to the server
immediately for real-time collaboration."

Expected behavior:

- Connects the two separately-stated decisions and names the conflict
  (offline-first vs. immediate server sync) — not just an obvious oxymoron.

- Does not silently pick one; holds both branches open until the user resolves
  the tension.

### 4. Alignment reached

Request: All branches have been answered.

Expected behavior:

- Stops interviewing.

- Presents the complete shared understanding as a single structured summary,
  each resolved branch carrying its acceptance criteria.

- Offers to hand the result to `plan-smith` as a tracked plan; writes nothing
  without a yes.

- Writes no implementation code.

### 5. Terse output

Request: Any point during the interview.

Expected behavior:

- No pleasantries, preamble, or narration; each turn opens with the question or
  the decision.

- Restating a resolved decision to confirm it is allowed (that is the payload
  here), but it is never padded or repeated once confirmed.
