---
name: review
description: >
  Done-time review of a Vue 3 + TypeScript frontend: checks finished code —
  the current diff, a directory, a file, or the whole frontend — against the
  project style rules and for correctness (reactivity, leaks, async races,
  router and PrimeVue pitfalls, tests that cannot fail), and checks the API
  client's types against the JSON the Go server sends. Use after edits or a
  feature are complete, and to add, change, or learn frontend style rules.
license: MIT
argument-hint: "[TARGET* | add|change|remove RULE | learn] [dirs=a,b] [max=N]
  [depth=light|standard*|full] [plan_first] [fix]"
---

# review

## Usage

```
/web:review                                  check (default): review the current git diff
/web:review src/pages                        review one directory
/web:review src/pages/DevicesPage.vue        review one file
/web:review src/pages/DevicesPage.vue:42     review the unit enclosing that line
/web:review component=DeviceTable            one component; func=<name> for one function
/web:review all                              review the whole frontend and its API contract
/web:review all max=15 depth=light           cap findings; set review depth
/web:review all dirs=pages,stores            restrict to these directories
/web:review all plan_first                   propose the budget, then stop for approval
/web:review src/pages fix                    review, then apply the findings
/web:review add "never export a default"     add a style rule
/web:review change "the boolean naming rule" refine an existing style rule
/web:review remove "the px rule"             remove a style rule
/web:review learn                            mine this session's feedback into rules
```

Done-time review for the frontend. Read the tokens in any order: a reserved word
is a mode or flag, `key=value` is a control, and anything else is the target.
`func=` and `component=` name the target, not a control. A `key=value` that
names no control here, or a word left over once the modes, the target, and any
text the skill takes are read: say it was not recognized, name the ones that
exist, and run with the defaults as if it were absent — unless dropping it would
widen what the run changes; then ask. A target that resolves to nothing: say so
and ask — never guess what to work on. Pick the mode:

- Check (default) — no mode word; audit the target, then offer the rules this
  session taught (Session rules).
- Rule edit — `add`/`change`/`remove`, the rest being the rule text, reserved
  words included, or the input is a plain style preference.
- Learn — `learn`; mines the current editing session (since the last /clear)
  for convention feedback and proposes rules.

Sources of truth:
- `web:style` (on-demand: Check mode) — owns the style rules, the reference
  Biome config, and their detection; the whole style dimension is delegated to
  it.
- `../style/references/production.md`, `../style/references/test.md`,
  `../style/references/biome.json` (on-demand: Rule-edit/Learn) — the prose
  Production and Test rules and the reference config; those modes write
  here.
- [references/correctness.md](references/correctness.md) (on-demand: Check
  mode) — what to look for beyond style.
- [references/contract.md](references/contract.md) (on-demand: Check mode,
  when the contract is in scope) — the API contract check.

In every mode, report tersely: no preamble or narration; state each fact once;
don't restate output the user can already see.

## Check mode

### Target

Resolve the frontend root and the target — empty, a directory, a file,
`FILE:LINE`, `func=`, `component=`, or `all` — exactly as
`../style/references/checking.md` (Frontend root, Target) does: the empty
target runs the diff that file names, and a named target runs no diff. One
difference for the empty target: once this session has made fixes, by this
skill or any other, committed or not, it is the diff from the commit before
the first fix (`git diff <commit>`, restricted the same way), since a fix
regresses the code beside it. State the resolved
root, target, and file set before reviewing.

The API contract is in scope for `all`, for the root, and for any target or
diff touching the API client module or a Go file that serves its paths.

### Budget & scope

Controls and flags: `dirs=a,b`, `max=N` (default 25, highest severity first),
`depth=light|standard|full` (default `standard`; `light` reports Blockers and
Should-fix only, saying how many it left out), `plan_first`, and `fix` (apply
the findings after reviewing; it neither triggers plan-first nor skips a stop
the target triggers). Default to plan-first when the target is broad — more
than ~40 files or ~3000 lines of `.vue`/`.ts` — and no `dirs=` or `max=` was
given: propose the budget and the directory list, then stop for the user's
answer, reviewing nothing until it comes. The threshold is `web:style`'s, so
the two agree on one target.

### Workflow

1. Resolve the target and budget and list the files in scope.
2. Style dimension — invoke `web:style` with the resolved target and budget,
   saying it is delegated for offenses only; a delegated `web:style` never stops
   for plan-first, so the review relays no stop. Take its offense list as the
   style findings; never re-derive style rules here. Reviewing in this context,
   invoke `web:style` with the Skill tool all the same and let its pass read the
   rule files; never read them here as well. The rules its pass reads land in
   this context: do not consult them again while judging correctness. One defect
   that is both (a listener `onMounted` adds and nothing removes) is reported
   once, under correctness, with the higher grade, naming the style rule id it
   also breaks.
3. Correctness — read [references/correctness.md](references/correctness.md)
   and review each file against it, highest-risk first (stores, the API
   client, pages, then components and tests).
4. API contract, when in scope — read
   [references/contract.md](references/contract.md) and follow it.
5. Before a finding that reaches beyond the file (a symbol is unused, every
   caller guards a value, a branch is reachable), confirm it with the `LSP`
   tool or grep across the root; skip at `depth=light`. No answer → say the
   finding is grep-confident.
6. Judge by reading: run no Biome, `vue-tsc`, Vitest, Playwright, or Go
   tooling while reviewing; judge test coverage by grepping the symbol in the
   tests. `grep` and the style pass's read-only width measure are allowed.
   Name every command this pass ran, as run, in one report line ("none" when
   nothing ran), and say the style dimension came from `web:style`.
7. Merge the style offenses with the correctness and contract findings and
   report (below). Change no code unless asked.

### Scale

Up to ~40 files or ~3000 lines: review in this context. Larger: fan out one
subagent per directory (`components`, `pages`, `stores`, top-level `src`,
`e2e`), each invoking `web:style` for its own directory with the rule-id and
severity list the parent derived once (per `../style/references/checking.md`),
and reviewing correctness itself. The parent runs the contract check. Workers
get no share of `max`; the merge applies it once, regrades every worker
Blocker against the rubric below, and checks every `file:line` against the
file.

### Output

Group by severity: Blocker / Should-fix / Nit. Style offenses keep the tier
`web:style` gave them. Grade a correctness or contract finding by the worst
consequence a reachable input or state produces, naming it — one you cannot
tie to an input or a user action is at most Should-fix. First match wins:

1. Blocker — a reachable input or action gives a wrong or missing value on
   screen, an exception, lost or corrupted state, a leak, a stale answer shown
   as current, a security exposure, or a swallowed error a caller depends on;
   or a test passes while the code is wrong.
2. Should-fix — correct for every current path but fragile: a case no path
   reaches yet, a type that promises what the server does not (a field marked
   always present that it may omit), an error too vague to act on, an API easy
   to misuse, a reachable branch with no test.
3. Nit — no behavioural consequence: clarity, dead code.

Each finding:
- `file:line` — the problem in one line.
- the rule id or dimension: a style offense keeps the bare id `web:style`
  gave it; correctness is `correctness`, the contract `api-contract`; a
  finding that is both names both
  (`correctness`, `undo-onbeforeunmount-everything`).
- a minimal fix, checked to do what it claims, opening with one of `insert`,
  `delete`, `rename`, `move`, `replace`, `reword`.

End with a one-line verdict (ship / fix-first) and the per-severity counts,
then the budget: `depth`, files reviewed — counted off the step-1 listing,
never estimated — and how many findings went unreported past `max`.

### Applying fixes

When asked to change code (apply findings, fix, refactor), read
[references/fixing.md](references/fixing.md) first and follow it.

### Session rules

Close every completed Check run with Learn mode's scan, so the session's
corrections become rules without a separate `learn` call: below the finished
report (its verdict and budget line stay put), and after the fixes when `fix`
applies them, if this session holds the user's feedback on `.vue`/`.ts` code,
read [references/rule-editing.md](references/rule-editing.md) and run its Learn
steps 1–4 under the heading `Rules this session taught`, then write only what
the user picks; a code-style correction, one given during this run included, is
a rule candidate, never a `LESSONS.md` line as well; a correction of how the
review ran stays a lesson. No feedback, or none surviving step 2, adds nothing
to the report. A `plan_first` stop is not a completed run, and a fan-out worker
never runs it; the session is not its own.

### Delegated by web:audit

Delegation is recognized from the invocation, never guessed: `web:audit` says it
is invoking for findings only and passes the target, `depth`, and, when it
splits the review across workers, the pinned `web:style` rule-id and severity
list to use. Run Check on the whole target in this context, never fanning out,
even past Scale's threshold; invoke `web:style` with the target, `depth`, and
the pinned list when the brief gives one, never `max`, whatever Workflow step 2
says; and run the contract check yourself only when your brief says so, whatever
Check mode's scope rule says: the audit gives it to exactly one worker, so no
parent runs it for you, and a silent brief means another worker runs it, or it
is out of scope. Return the findings grouped and written as Output says,
uncapped (the audit applies `max` once, at its merge), plus every command run,
and how many Nits `depth=light` left out, but no verdict or budget line (the
audit writes its own), then stop: no `plan_first` stop (the audit agreed the
budget), no `fix`, no Session rules, and no fan-out (the audit already split the
work, and a worker cannot dispatch one).

## Rule-edit and Learn modes

When either mode triggers, read
[references/rule-editing.md](references/rule-editing.md) first and follow it;
never write a rule without confirmation.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/review.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable; this block never moves or merges lessons. A missing file needs no
comment. On a correction or self-caught mistake, append a one-line rule —
general, naming nothing from the project at hand (its files, tests, tickets) —
to the sibling when this directory is writable (creating it even when only the
fallback holds lessons so far; both stay read), else to the fallback, creating
it, and report where. A lesson write is not a project write: a read-only or
no-change run still makes it.
