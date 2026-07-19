# Measuring a skill

On-demand playbook for proving a skill works: does loading it actually improve
outcomes, and does its description trigger when it should? Run from
`skill-smith`'s Measure step. Author-time tooling — it uses subagents in the
author's environment and does not change what the measured skill ships.

## Contents

- Rubric
- A/B protocol
- Grading
- Trigger test
- Discipline skills
- Verdict
- Degrade gracefully
- Templates

## Rubric

Turn the target skill's `README.md` `## Evaluations` into a checkable rubric:
each scenario's request is the task; each expected-behavior bullet is one
assertion, phrased so a grader can mark it pass/fail from the output alone. Drop
or split any bullet that isn't objectively verifiable. Add the terse-output
assertion if the scenarios lack one. Record each scenario in the shape
Anthropic's tooling uses — `{skills, query, files, expected_behavior[]}` — so
runs are reproducible.

## A/B protocol

Per scenario, run two fresh subagents on the identical request:

- Baseline — the skill NOT loaded.
- Treatment — the skill loaded.

Isolate the legs: each gets only the request (and any scenario files), no prior
turns, so the delta measures the skill, not the conversation. Capture each final
output verbatim.

Run every leg on each model the skill targets — guidance that suits a strong
model can under-serve a smaller one. Record each leg's tokens and wall-clock; a
treatment that wins but costs far more tokens may not earn its place.

Overfitting guard: run the README scenarios plus at least one held-out request
the author did not write the skill against, so a delta reflects generalization,
not a skill tuned to its own examples.

## Grading

A separate grader subagent scores every rubric assertion against each captured
output — pass/fail plus a one-line evidence quote. Grade blind where possible:
present the two outputs as A/B without saying which loaded the skill, so the
grader can't favor the treatment. Never let a subagent grade its own output.
Grade the transcript, not just the final answer — a skill can reach the right
result by the wrong path, which won't generalize.

## Trigger test

The description, not the body, decides whether the skill loads, and triggering
is the most common real-world failure. Build a labelled query set: ~8–10
should-fire prompts (real tasks the skill targets, including oblique phrasings
and cases that never name the domain) and ~8–10 should-not-fire near-misses —
adjacent tasks that share keywords but need something else (the valuable
negatives). Split ~60/40 into tune and validation sets.

For each query ask a router subagent — given only the skill's `name` +
`description` and the query — whether it would load the skill. Triggering is
nondeterministic, so run each query 3× and take the fire rate; count ≥ ~0.5 as
fired. Score on the validation set:

- recall = should-fire that fired / should-fire — undertriggering is the common
  failure, so target recall first.
- precision = should-fire that fired / all that fired.

Tune the description against the tune set, then confirm on validation. Never
paste literal keywords from a failed query into the description — generalize the
concept, or you overfit to phrasings and lose the next one.

## Discipline skills

For a skill whose job is to *stop* a behavior rather than add a capability, a
calm request won't expose the failure. Pressure-test instead: one scenario
stacking 3+ simultaneous pressures (deadline, sunk cost, authority, fatigue) and
a forced choice. It passes only if the agent makes the right call under pressure
*and* cites the skill's rule. Each new excuse the baseline invents becomes an
explicit counter in the skill; repeat until no excuse survives.

## Verdict

Report one table, most-to-least decisive:

| Scenario | Baseline | With skill | Δ  |
|----------|----------|------------|----|
| <name>   | 2/4      | 4/4        | +2 |

Then trigger recall/precision and a one-line call:

- The skill earns its tokens when treatment beats baseline on the targeted
  assertions with no regressions, and trigger recall is high.
- Flag scenarios where baseline already passes — the skill adds nothing there;
  consider narrowing scope.
- A zero or negative delta means the body isn't teaching what the evals test —
  fix the skill, not the rubric.
- A treatment that passes more assertions but costs far more tokens hasn't
  clearly won — judge by tokens-to-outcome, not pass count alone.

## Degrade gracefully

No subagents (some claude.ai / restricted runtimes): run each leg sequentially
in a fresh context, skip blinding, and say so in the report. A stated smaller
run beats a silent full-coverage claim.

## Templates

Copy and fill these; they keep runs consistent across skills.

Rubric — one object per scenario (the shape Anthropic's tooling uses):

```json
[
  {
    "skill": "grill-me",
    "query": "I want to add caching to the API.",
    "files": [],
    "expected_behavior": [
      "Maps the decision tree (what to cache, invalidation, store, TTL, keys)",
      "Asks the highest-impact unknown first, one topic at a time — no bundling",
      "Does not start designing or writing code",
      "Opens with the question — no preamble or narration"
    ]
  }
]
```

Grader (spawn per assertion, or one grader over the set):

```
You grade skill evals. Given one rubric assertion and a candidate's OUTPUT
plus its transcript, answer PASS or FAIL and quote the single line of evidence.
Judge only the assertion; ignore style unless the assertion is about style.
The two outputs for a task are labelled A and B — you are NOT told which used
the skill; do not guess or favour either.
```

Trigger query set (label each; ~8–10 per side; 60/40 tune/validation):

```
should-fire:
- <a real task the skill targets>
- <an oblique phrasing that never names the domain>
should-not-fire (near-miss):
- <an adjacent task that shares keywords but needs something else>
```
