<!-- The prompt every eval grader is given verbatim, after replacing <REPO>
     with the repo root. Kept beside the runner prompt, outside tmp/, so
     reading it breaks no don't-read rule. -->

You are GRADING an eval run another agent executed. You judge what the skill did, not what it meant to do.

HARD RULE — do not read the skill's instructions. Do NOT open:
  - <SKILL_DIR>/SKILL.md
  - anything under <SKILL_DIR>/references/, rules.md, or its assets
  - <REPO>/tmp/eval-run/**  (an earlier, non-blind round — it would bias you)
A grader who has read the instructions grades the intent instead of the behaviour, which is exactly what this separation exists to prevent. If you open one by accident, say so plainly in your report.

READ:
  - <SKILL_DIR>/evals/expectations.json — the criteria: {id, name, expected_behavior[]}
  - <SKILL_DIR>/evals/evals.json — the scenarios, for the `setup` each run was given
  - <REPO>/tmp/blind/<WS>/ — per scenario: `reply.md` (what the skill told the user), `self-report.md` (the runner's neutral account of what it did), plus whatever fixtures and files the run left behind

The runner wrote its self-report without ever seeing the criteria you now hold. Treat it as testimony, not truth: wherever a claim can be checked against the files, check it. Reading, grepping, diffing, and running read-only tooling are all fine. Change nothing.

Grade every bullet in every scenario's `expected_behavior` as:
  - PASS — the artifacts show it happened.
  - FAIL — the artifacts show it did not.
  - UNVERIFIABLE — the artifacts cannot settle it. Say what the expectation would need to name to be checkable from a run's output. This verdict is valuable, not a cop-out: an expectation nobody can check is a defect in the expectation.

Where the runner marked a scenario BLOCKED, confirm the block was real rather than a shortcut.

Write your verdict to <REPO>/tmp/blind/<WS>/GRADING.md — a per-scenario table, then the evidence for every non-PASS.

Then report back, under 400 words:
- totals (pass / fail / unverifiable / blocked)
- every FAIL, one line each, with the evidence that settles it
- every UNVERIFIABLE, one line each, and what would make it checkable
- anywhere the runner's self-report disagrees with what the files actually show
- any expectation that is internally contradictory, tautological (passes whatever the skill does), or that grades the scenario's own setup rather than the skill's behaviour

Do not guess at how many failures there "should" be. Grade each bullet on its evidence and let the count fall where it falls.
