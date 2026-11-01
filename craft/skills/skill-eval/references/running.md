# Running evals

How to test and fix skills here with the fewest tokens and dollars at full
quality. Tiers and their tools: [tiers.md](tiers.md); mistakes past runs paid for:
[pitfalls.md](pitfalls.md).

## Order of work

1. Collect every decision the change needs, ask the user them one by one with
   a recommendation, then edit: an answer applied alone forces another round.
2. After every edit: `scripts/lint-skills.sh` and `scripts/eval-check.py` (free,
   seconds). Lint only while nothing else edits skill files.
3. Once per batch: `scripts/eval-routine.sh` (probes, hunt, triggers; about
   \$0.15 per changed skill). Fix a hunt split in text the batch changed, at
   most two rounds per skill; list the rest for the user.
4. Agent-run cases only for what the diff reaches, on the default model:
   `scripts/eval-changed.sh --audit --model default -j 4 --max-usd <cap>`. The
   pass ledger (`tmp/eval-ledger.json`) skips cases passed on unchanged inputs,
   and the listing names a case whose last ten runs there both passed and
   failed (`flaky: <case> (1 of 3 failed)`), even when it will not run. That
   mark is history only: step 5 labels a repeat FAIL by the base run.
   Its key holds the model ID but not the CLI version. In the first round
   after a CLI upgrade, add `--fresh` to both of the round's commands: the
   listing whose case list and estimate you ask about, and the `--audit`
   run. A case costs \$0.25–0.80, a fan-out case \$3–9; ~50 cases ran about
   \$20.
5. Rerun a fixed case once. A case that has failed and passed gets two more
   runs before it counts as fixed. One whose re-run fails again is reported
   as a FAIL with its trace and not re-run further. Never run a case at the
   base unasked. Label the FAIL by the user's base run: flaky when it fails
   there too, a break the change caused when it passes there, cause unknown
   without one (offer it).

## Long runs

- Cap memory: `systemd-run --user --scope -q -p MemoryMax=8G -p
  MemorySwapMax=2G -- <cmd>` (Linux).
- Stalls: `eval-changed.sh` stops a run whose results dir and every
  `claude-eval-*` workspace had no write for 10 minutes
  (`EVAL_STALL_SECONDS`), saving the process tree to
  `<results>/stall-ps.txt`. Give any other run that can last over 10
  minutes (a blind round, a long test suite) the same watchdog; the cheap
  tiers need none.
- Keep logs in the repo's git-ignored `tmp/`; print only fail and summary
  lines.
- A `--keep` workspace holds a read-only Go module cache: `chmod -R u+w`
  before deleting it.

## Agents and tokens

- Never fork an agent in a long session: a fork copies the whole conversation
  (130K–420K tokens each). Work inline, or give a fresh agent a short,
  self-contained brief.
- Delegate only independent work on disjoint files; never let two writers
  share a file, and lint after they finish.
- When the context grows large, write a handoff file in `tmp/` (state, changes
  per file, decisions, open items) and continue in a new session from it.

## Session state

Keep it in `tmp/`, which git ignores: the handoff notes, the questions asked
and their answers, the pass ledger, run logs (`tmp/eval-changed/`), and hunt
output (`tmp/eval-hunt/`). Copy what matters before deleting a clone.
