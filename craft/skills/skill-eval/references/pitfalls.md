# Eval pitfalls

Mistakes that cost a run before. Read before writing or fixing a probe, a
native case, a grader, a generator, or a contract, and before a long eval run.
Add a line when a run teaches a new one.

## Fixtures and mocks

- Give every folder a scaffold must show a file (`.gitkeep`): Glob lists files
  only, so an empty folder reads as missing.
- Write a fixture that is clean under today's rules; a rule change can turn an
  expected file into an offense, and the model then "fixes" it and fails.
- A fan-out case can pass on a fixture that is not clean: each worker sees one
  slice and misses what a single reader finds. Check the clean parts against
  every current rule, not only against past passes.
- Define a mock's content where the mock is defined; a later patch in a
  generator misses every case written before it.
- End a model-played mock page on body text, never a bare heading; the mock
  model carries a dangling heading into its next answer.

## Graders

- Grade the outcome, not the attempt: count commits in `.git/logs/HEAD`, not
  `git commit` calls in the trace (refused calls are in the trace too).
- Accept every wording the skill allows (`per-request` and `each request`,
  `has 2` and `: 2`), and reject the wrong answers; test both on real traces.
- Judge only real tokens: a count grader must match group prefixes the written
  file holds, or a word like `SRD` reads as a group.
- Exclude negations from a "says X" regex (`is not set up` must not pass).
- A trace holds the reply twice (assistant text and `result`); test a grader
  edit with `replaceAll`, never `replace`.
- Keep an LLM grader's rule equal to the skill's, exceptions included.
- A fail regex must not match a pass answer by prefix: `LOCAL\b` matches
  `LOCAL-AND-…`.

## Contracts and probes

- Contract `must` phrases are regexes: write a line break as `\s+`, escape `.`.
- Measure a new probe with `--baseline`; drop a `prior` one (the bare model
  already agrees), keep `load-bearing` or `redundant`, record with `--write`.
- Run a new probe against the base with `--against HEAD`; it should fail there
  when it pins new behaviour.
- A probe that splits at the base too is flaky, not broken: confirm with one
  uncached rerun on both sides before changing text.

## Editing skill text

- Rewrap only the changed paragraph; a section-wide reflow can swallow the next
  heading.
- Edit a block every skill shares with a script over all copies, matching
  across line breaks; verify each copy changed once on whitespace-joined text.
- Scope a shared sentence to the skills it fits (one target, free-text briefs,
  delegated runs) before adding it everywhere; run the hunt on all copies.
- When the user decides a reading, pin it in the contract and, where it can be
  load-bearing, in a probe.

## Running

- Run the cheap tiers first (lint, probes, hunt, triggers); run agent cases
  only for what the diff reaches, and let the ledger skip passes.
- Lint while no other process edits skill files; a half-written file makes
  one-off lint errors.
- Give a long run a stall watchdog and a memory cap; record cost per run.
- An account that appends a notice to every reply can break line-sensitive
  graders: set `EVAL_STRIP_NOTICE` (see `native-cases.md`).
- Batch the decisions a run needs before editing, so one eval round covers all.
