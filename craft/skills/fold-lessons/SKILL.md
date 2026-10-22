---
name: fold-lessons
description: >
  Folds the lessons skills recorded in LESSONS.md, and pending edits to skill
  files, into the skills, keeping only rules that generalize past the task
  that taught them; validates each against the skill and the repo's authoring
  rules, then lints and evals it. Use to fold, absorb, or bake in skill
  lessons, or to vet uncommitted skill edits.
argument-hint: "[<skill>...] [--base <ref>]"
license: MIT
---

# fold-lessons

## Usage

```
/fold-lessons                 every LESSONS.md and every uncommitted skill edit
/fold-lessons <skill>...      only the named skills (name or path)
/fold-lessons --base <ref>    also vet skill edits committed since <ref>
```

Two inputs, one gate. A `LESSONS.md` is a holding area every run of its skill
reads; folding moves each rule into the step it governs. A pending edit is a
diff hunk under `<group>/skills/` against the base (default `HEAD`, working
tree included); vetting judges what it adds. Lessons arrive through each
skill's `## Self-learning` block and `../enhance-skills/`; this skill consumes
them. Work in a writable source checkout only — never under
`.../plugins/cache/`. A store under `~/.agent-data/` is the user's own: fold it
only when the user names it.

## Generic or not

Judge each lesson and each rule an edit adds by one test: would it change a run
on an unrelated input the skill will meet tomorrow? Then give one verdict:

- Keep: it already holds for any input. Names the skill's domain gives every
  input — its standard's rule ids and sections, its modes, its tools — are
  generic there.
- Generalize: a true rule wrapped in one task's nouns. Strip project and
  product names, file names, ticket numbers, ids local to one document (its
  own requirement numbers), and sample values; keep the behaviour. If nothing
  survives the strip, it is a Drop.
- Drop: true only for one target — a project fact, a one-off preference, a
  value. Its home is that project's instructions, not the skill. For an edit,
  Drop reverts the hunk.
- Reword: the skill already carries the rule and a run missed it. Sharpen that
  line instead of adding a second; a missed rule was not clear enough.
- Merge: two items that are one rule restated, or a rule a sibling skill's
  shared reference already carries, become one line.
- Hold: the item overrules the body, contradicts another item or a
  `contract.json` rule, or its intent is unclear. Change nothing for it; it is
  a question for the user, and a held lesson stays in `LESSONS.md`. Narrowing
  what the body or its standard permits is not overruling.

When in doubt between Generalize and Drop, Drop: a narrow rule in the body
costs every future run context and misleads runs it does not fit.

## Validate

Check every Keep, Generalize, Reword, and Merge before proposing it; a failed
check changes the verdict, never passes silently:

- Carried: grep the rule's key terms across the skill's `SKILL.md`, its
  references, and the shared references it loads; a hit is Reword or Merge.
- Consistent: no conflict with the body, another item, or `contract.json`.
- Placed: one step governs it; a rule that fits no step is not yet a rule.
- Written to the authoring rules: one dense imperative line, stated once, in
  the surrounding text's terms, no hedging; wrapped at ~80 columns; never a
  dollar-digit positional in a body.
- Budget: `SKILL.md` aims at ~5000 tokens and ~500 lines. Never cut a settled
  rule to make room; move condition-triggered prose (a mode, a case type) to
  `references/`, leaving a pointer and the one-line rule. A reference over
  ~100 lines starts with a Contents list.
- Guarded: a high-stakes rule gets an `evals/contract.json` phrase, and a probe
  in `evals/probes.json` when it is likely to regress. A new probe must FAIL
  at the base (`./dev/eval-probe.py --probe <group>/<skill>:<id> --against
  <base>`) and pass on the result; then class it with `--baseline --write`.
  One that passes at the base proves nothing — sharpen its situation; one
  that classes `prior`, rewrite or delete.
- Triggers: an item that changes the description adds its requests to
  `dev/eval/triggers.json`.

## Procedure

1. Scope: the `LESSONS.md` files and the skill-file diff against the base,
   narrowed to the named skills. Per skill, read the lessons, the diff, its
   `SKILL.md`, and every reference the governed step loads.

2. Gate each item per [Generic or not](#generic-or-not) and
   [Validate](#validate) it.

3. Propose once, for all skills: per item its verdict, the final line, and its
   target (`file` and section); per Drop the reason, flagging each reverted
   hunk, since it undoes the user's own work; per Hold the question in plain
   terms — the situation, the options, a recommendation. Wait for the answer,
   then work unattended to the report; ask again only for what that answer
   left open.

4. Fold, one skill at a time, as a self-contained edit so each commits alone:
   put each rule into the step it governs, in `SKILL.md` or the reference that
   step loads, never a loose list of notes; apply each Drop's revert and each
   Generalize rewrite to the edited line in place; add the guards. Delete
   `LESSONS.md` once no lesson is held; a Hold keeps the file with only its
   held lines. Keep `## Self-learning`.

5. Test: `./dev/lint-skills.sh` until it reports no error and no warning the
   fold caused, then `./dev/eval-routine.sh --base <base>`. A missing script
   is reported, never replaced by an improvised check.

6. Evaluate per CONTRIBUTING.md's eval loop:
   - A probe FAIL or SPLIT on a changed skill gets one fix and one re-run; a
     second failure goes to the user as a design question.
   - A hunt split on folded lines may drive one fix; a split on lines that fix
     added goes to `tmp/eval-backlog.md`, not another edit.
   - Agent-run cases and blind rounds only on the user's request, after
     stating scope and rough cost.
   - Probes and the hunt read no `LESSONS.md` and show nothing broke, not that
     a folded rule works; say so.

## Output

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. The proposal is the full ledger; the final
report is per skill: counts per verdict, read off the finished files, not
carried from the proposal; the files touched; whether `LESSONS.md` was
deleted; the lint and routine result with its cost. End with what is still
open — held items, second failures — each as a plain-terms question. A run
with nothing in scope is one line.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/fold-lessons.md` (pass `~`
as is, the file tools expand it; no environment probe; `$AGENT_DATA_DIR`
replaces `~/.agent-data` only when you are told it is set). The sibling wins a
conflict; the fallback, which a read-only install writes, still counts once the
checkout is writable. A missing file needs no comment. On a correction or
self-caught mistake, append a one-line rule — general, naming nothing from the
project at hand (its files, tests, tickets) — to the sibling when this directory
is writable, else to the fallback, creating it, and report where.
