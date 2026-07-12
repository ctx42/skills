---
name: plan-smith
description: >
  Writes an implementation plan as numbered checkbox items with a status
  summary table (Y implemented, N not yet, X rejected), and updates that table
  over time. Use when asked to write, draft, structure, track, or update a
  plan, task list, or implementation checklist.
license: MIT
---

# plan-smith

Turn a brief into a tracked plan, and keep its status current. Pick the mode
from the request:

- Create — write a new plan from a description, a spec, or a shared
  understanding reached with `grill-me`.

- Update — re-read an existing plan and refresh each item's checkbox and status
  from what has since happened.

If the request is ambiguous, ask one question: write a new plan or update an
existing one?

Report tersely: no preamble or narration; state each fact once; after writing,
don't paste the plan back — point to the file and give the status counts.

## Format

Every plan is one Markdown file with two parts.

A summary table first, so status is visible at a glance:

```
## Summary

| # | Item              | Status |
| - | ----------------- | ------ |
| 1 | <short item name> | Y      |
| 2 | <short item name> | N      |
| 3 | <short item name> | X      |

Legend: Y implemented · N not yet · X rejected
```

Then one section per item, numbered to match the table, each led by a checkbox:

```
## 1. <item name> — [x]

<what it is, why, acceptance criteria>

## 3. <item name> — [ ]  (X: rejected — <one-line reason>)

<kept for the record; not deleted>
```

Checkbox to status: `[x]` = `Y` (implemented), `[ ]` = `N` (not yet). A rejected
item keeps `[ ]`, is tagged `X`, and states why in one line — never delete it.

## Create mode

1. Gather the items. From the brief (or a `grill-me` summary), list the
   distinct, independently-checkable pieces of work. Don't invent scope; ask if
   a piece is unclear.

2. Order by dependency and impact — blocking and highest-impact items first.

3. Write the file to the format above: summary table (every item starts `N`,
   unchecked) then one section per item with acceptance criteria.

4. Confirm the path before writing; use the name the user gives, else
   `tmp/<slug>-plan.md`. Never overwrite an existing plan without saying so.

## Update mode

1. Read the existing plan. Take its item list and current statuses as ground
   truth; never renumber or drop items.

2. Set each item's new status from evidence the user gives or the repo shows:
   implemented → `[x]` / `Y`; dropped → `X` + one-line reason; untouched → leave
   `N`.

3. Rewrite the summary table and the changed items' checkboxes/tags only; leave
   all other prose intact.

4. Report the deltas and the new counts; don't reprint the whole plan.

## Rules

- One item = one independently-checkable outcome. Split bundled work.

- Never silently drop a rejected item — mark it `X` with a reason so the record
  stays honest.

- Give each item acceptance criteria — state what proves it done, so `Y` is
  verifiable, not asserted.

- Table and sections stay in sync: same numbering, same statuses.

## Self-learning

Read this skill's lessons and obey them: sibling `LESSONS.md`, else
`$HOME/.agent-data/ctx42-skills/lessons/craft/plan-smith.md` when this
directory is read-only. On a correction or self-caught mistake, append a
one-line rule to whichever is writable (creating it) and report where.
