---
name: plan-smith
description: >
  Writes an implementation plan as numbered checkbox items with a status
  summary table (Y implemented, N not yet, X rejected), and updates that table
  over time. Use when asked to write, draft, structure, track, or update a
  plan, task list, or implementation checklist.
argument-hint: "[write <brief> | update <plan-file>]"
license: MIT
---

# plan-smith

## Usage

```
/plan-smith <request>           infer write vs. update from the request (default)
/plan-smith write <brief>       write a tracked plan from a brief or a grill-me summary
/plan-smith update <plan-file>  refresh each item's checkbox and status
```

Turn a brief into a tracked plan, and keep its status current. `$1` is the
mode when given — `write` (the rest of `$ARGUMENTS` is the brief) or `update`
(the rest is the plan-file path); else infer the mode from the request:

- Write — a new plan from a description, a spec, or a shared understanding
  reached with `grill-me`.

- Update — re-read an existing plan and refresh each item's checkbox and status
  from what has since happened.

If the request is ambiguous, ask one question: write a new plan or update an
existing one?

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. After writing, point to the file and give the
status counts (e.g. `wrote tmp/sso-plan.md — 0 Y / 4 N / 0 X`); never paste
the plan back, and don't narrate it either — the item names and the order you
chose are in the file the user is about to open.

What you deliberately left out of the file belongs here, and only here: an
unpinned decision, a suggestion the brief didn't ask for. Give each a name and
at most a half-line of why it matters. They are there so nothing is hidden, not
to be argued — a paragraph defending one has made the reply longer than the
part of the plan it is about.

## Format

Every plan is one Markdown file with two parts — and only those two. No
assumptions preamble, no open-questions section, no risks or rollout matrix:
a reader has to be able to trust that everything in the file is agreed work.
Anything else worth saying goes in the reply, where it stays a suggestion
instead of hardening into a decision nobody made.

A summary table first, so status is visible at a glance:

```
## Summary

| #  | Item              | Status |
|----|-------------------|--------|
| 1  | <short item name> | Y      |
| 2  | <short item name> | N      |
| 3  | <short item name> | X      |

Legend: Y implemented · N not yet · X rejected
```

Keep the `Item` cell to a short name (≤ ~30 chars); the item's own section
carries the detail. Align the table so the `|` delimiters line up vertically:

- Each column's width is its widest cell's content.
- Header and body cells: one leading and one trailing space around the content,
  then pad the trailing side with spaces to the column width.
- Separator row: fill each cell with dashes flush to the pipes, no surrounding
  spaces (`|----|`, never `| -- |`), exactly as many dashes as the cell is wide.

Compute the widths from the widest cell — don't eyeball it — then verify the
header, separator, and every body row have identical character width.

Then one section per item, numbered to match the table, each led by a checkbox:

```
## 1. <item name> — [x]

<what it is, why, acceptance criteria>

## 3. <item name> — [ ]  (X: rejected — <one-line reason>)

<kept for the record; not deleted>
```

Checkbox to status: `[x]` = `Y` (implemented), `[ ]` = `N` (not yet). A rejected
item keeps `[ ]`, is tagged `X`, and states why in one line — never delete it,
so the record stays honest.

## Write mode

1. Gather the items. From the brief (or a `grill-me` summary), list the
   distinct, independently-checkable pieces of work — one item = one outcome;
   split bundled work into the outcomes it actually needs.

2. Keep the items the brief's. Splitting a named problem into its real parts is
   the job; adding work nobody raised — tests, monitoring, retention, rollout,
   a guard so it can't recur — is not, however sensible it looks. Those are
   suggestions: name them in the reply, one line each, and let the user turn
   one into an item. Written in unasked, they sit at `N` forever and make the
   counts lie about what was agreed.

3. Settle what the brief left open before writing, not inside the file. An
   outcome nobody has chosen has no acceptance criteria, so it can never be
   honestly checked off, and a guess written down reads afterwards as a
   decision the user made. Ask the one open question that most changes what the
   items are; a detail inside an already-decided outcome is not that question —
   the item's acceptance criteria absorb it. When several are open and the
   shape is still moving, say so and offer `grill-me` rather than dripping
   questions one per turn.

4. Order by dependency and impact — blocking and highest-impact items first.

5. Write the file to the format above: summary table (every item starts `N`,
   unchecked) then one section per item. Give each item acceptance criteria —
   what proves it done — so `Y` is verifiable, not asserted. Path: the name the
   user gives, else `tmp/<slug>-plan.md`; no need to ask, the report names it.
   If something is already there, say so and ask before overwriting.

## Update mode

1. Read the existing plan. Take its item list and current statuses as ground
   truth; never renumber or drop items.

2. Set each item's new status from evidence the user gives or the repo shows:
   implemented → `[x]` / `Y`; dropped → `X` + one-line reason; untouched → leave
   `N`.

3. Rewrite the summary table and the changed items' checkboxes/tags only, so
   table and sections keep the same numbering and statuses; leave all other
   prose intact.

4. Report the deltas and the new counts.

## Self-learning

Obey this skill's lessons when it has any: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/plan-smith.md` when this
directory is read-only. Most runs have none; absence is the normal case and
needs no comment. On a correction or self-caught mistake, append a one-line
rule to whichever path is writable, creating it, and report where.
