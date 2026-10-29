---
name: skill-eval
description: >
  Evaluates the skills of a skills repo: lints them against the authoring
  standard, checks their contracts, asks cached probe questions, hunts
  ambiguous wording, tests trigger routing, runs agent cases under a cost cap,
  and measures token cost. Use to test, evaluate, or audit a skill, to check
  what a skill edit broke, or to improve a skill behind the eval gate.
argument-hint: "[audit* | run | fix] [<target>] [base=<ref>] [max=N]"
license: MIT
---

# skill-eval

## Usage

```
/craft:skill-eval [<target>]       audit: read-only graded report (default)
/craft:skill-eval run [<target>]   cheap tiers, then the agent cases the user approves
/craft:skill-eval fix [<target>]   one improvement at a time behind the eval gate, each its own commit
  base=<ref>                       compare against <ref> (default HEAD, working tree included)
  max=N                            stop agent cases once they have cost N dollars
```

Read the tokens in any order: a reserved word is a mode, `key=value` is a
control, and anything else is the target. No target is every skill the diff
against the base touches; `all` is every skill; a group (`go`) its skills; a
skill is `go:style`, `go/style`, or its path. For `all` or a group, propose the
budget — skills, tiers, estimated cost — and stop until the user confirms,
before any tier runs, the cheap ones included.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

## Setup

The tools are in `${CLAUDE_SKILL_DIR}/scripts/` (`scripts/` below). Run them
from the root of the repo under test; they take it from the working directory,
and `SKILL_EVAL_ROOT` overrides it. Before any eval work read
[running.md](references/running.md) and [pitfalls.md](references/pitfalls.md).
The tiers, their costs, and the eval loop are in [tiers.md](references/tiers.md);
the agent-case format in [native-cases.md](references/native-cases.md); the
skill standard in [authoring.md](references/authoring.md).

The tools expect `<group>/skills/<name>/SKILL.md`. A repo without that layout
gets a read-only review of each `SKILL.md` against
[authoring.md](references/authoring.md), whatever the mode; say so first. A
missing tool (`python3`, `node`, `git`, and `claude` for the paid tiers) is
reported with the tier it blocks, never replaced by an improvised check.

## Audit

Read-only: edits nothing, commits nothing. Per target skill, find and grade
each finding Blocker, Should-fix, or Nit:

1. Mechanical: the target's lines from `scripts/lint-skills.sh` (it runs
   `scripts/eval-check.py`); an error is a Blocker, a warning a Nit.
2. Conflicts: read `SKILL.md` and the references it loads. Two rules that
   cannot both hold, or one against a `contract.json` phrase, is a Blocker.
3. Probes: `scripts/eval-probe.py --skill <group>/<skill>`. A FAIL or SPLIT is
   a Blocker (a `prior` probe fails lint, step 1); a high-stakes rule with a
   contract phrase and no probe is a Should-fix.
4. Ambiguity: `scripts/eval-hunt.py --skill <group>/<skill>`, with `--full`
   when the diff does not touch the skill. Each split is a Should-fix, with its
   draft probe.
5. Triggers: `scripts/eval-triggers.py` when the description differs from the
   base; a miss is a Should-fix.
6. Tokens: `scripts/token-report.sh`. A description past ~350 characters is a
   Nit, past 500 a Should-fix; a body past ~5000 tokens or ~500 lines is a
   Should-fix. When a run's results exist under `tmp/eval-changed/<run>/`, add
   each case's dollars and tokens from `scripts/case-cost.py <run dir>`.

Audit runs no agent case. Report one line per finding, most severe first:
severity, `file:line`, the finding, and the command that fixes it — `fix` on
the skill, a script line, `/craft:skill-enhance` for a correction to record,
`/craft:skill-fold-lessons` for a `LESSONS.md` to fold. Then each skill's
token surface in one line.

## Run

The eval loop of [tiers.md](references/tiers.md), cheapest first; edits no
skill text:

1. `scripts/lint-skills.sh`, its output read unfiltered; an error stops the
   run.
2. `scripts/eval-routine.sh --base <base>`: probes, hunt, and triggers in
   parallel. For a target the diff does not touch, run the probes and the hunt
   with `--skill <group>/<skill>` (hunt `--full`) instead.
3. Agent cases: `scripts/eval-changed.sh` lists the cases the diff reaches
   (`--skill <group>/<skill>` for a named skill) with an estimate. Once the
   target is confirmed or needs no confirmation, run probes, hunt, and triggers
   without asking — they cost cents; before any agent case, state the case list,
   the count, and the estimate, and ask — whatever the size. On a yes, run
   `scripts/eval-changed.sh --audit --model default -j 4 --max-usd <cap>` (the
   cap is `max=` or the one agreed) under the memory cap and stall watchdog of
   [running.md](references/running.md). The yes covers the round end to end, its
   re-runs included, within the cap. At the cap, stop: report the cases and
   re-runs not run as open; running them needs a new yes.
4. Re-run each failed case once. One that then passes runs twice more before
   it counts as fixed; one that also fails at the base is flaky, not broken.

Blind rounds only when the user asks, after stating scope and rough cost.
Report per tier its counts and cost, each FAIL and SPLIT with its evidence
line, and per agent case its dollars and tokens (`scripts/case-cost.py <run
dir>`; a passing case keeps its trace, and so its tokens, only with `--keep`).

## Fix

One improvement at a time, each its own commit:

1. Findings: those in the conversation, else an Audit's. Collect every
   decision they need (a rule's reading, a contract change, a trade-off) and
   ask them one by one, each with a recommendation, before the first edit;
   then work unattended to the report.
2. Per improvement, Blockers first: write the test first — a contract phrase,
   or a probe that FAILS at the base (`scripts/eval-probe.py --probe
   <group>/<skill>:<id> --against <base>`), classed with `--baseline --write`
   (delete or rewrite a `prior` one). Then edit, re-wrapping only the changed
   paragraph. Cut token cost by moving condition-triggered prose (a mode, a
   case type) to `references/` with a pointer and its one-line rule, never by
   dropping a rule.
3. Gate: `scripts/lint-skills.sh`, then the probes and the hunt on the changed
   skill. One fix and one rerun per FAIL; a second FAIL reverts the improvement
   with an inverse edit and goes to the user as a question. A hunt split on
   lines the fix added goes to `tmp/eval-backlog.md`, not another edit.
4. Commit: stage only the files this improvement changed (`git add -- <paths>`,
   regenerated cases included), invoke `craft:cm` on the staged diff for the
   message, and `git commit -F -`. Group style-only wording fixes into one
   commit. Never push. Leave the user's own changes unstaged. Without
   `craft:cm` in the skill list, stop and name the craft plugin.

Report per commit its hash and summary.

## Rules

- Never write a target skill's `LESSONS.md` or lessons store. Name each
  correction the user gives about a target skill for `/craft:skill-enhance`.
- Never fork an agent; give a fresh agent only independent work on disjoint
  files, and lint after it finishes.
- Read every count and cost in a report off the tool output, never carry it.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. Name script output by its summary line, not
its full text. End with what is still open — held decisions, second failures,
backlog splits — each as a plain-terms question.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/skill-eval.md` (pass `~` as
is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
