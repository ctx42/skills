# plan-smith

Writes an implementation plan you can track: numbered items, each a checkbox
section with acceptance criteria, plus a summary table that rolls up status —
Y implemented, N not yet, X rejected. Re-run it to refresh the table as work
lands or gets dropped.

Pairs with `grill-me`: grill-me reaches a shared understanding, plan-smith turns
it into the tracked plan.

## When to Use

- You've settled what to build and want it captured as a checklist with status.

- You have a plan in chat and want it persisted and trackable.

- You're returning to a plan and want its status table brought up to date.

## Usage

```
/plan-smith write a plan for <thing>      # create mode
/plan-smith update tmp/x-plan.md          # refresh statuses
```

It writes to a file you name (or `tmp/<slug>-plan.md`) and confirms before
overwriting.

## Format

- A `## Summary` table: one row per item, a Status column, and the legend
  `Y implemented · N not yet · X rejected`.

- One numbered `## N. <item>` section per row, led by a checkbox (`[x]` done,
  `[ ]` not), with acceptance criteria. Rejected items stay, tagged `X` with a
  reason.

## Evaluations

### 1. Create a plan from a brief

Request: `/plan-smith` then "plan the work to add SSO: provider config, login
flow, session storage, and docs."

Expected behavior:

- Produces one numbered checkbox section per item and a `## Summary` table with
  the `Y / N / X` legend.

- All items start `N` and unchecked; each carries acceptance criteria.

- Confirms the file path before writing; does not overwrite silently.

### 2. Update an existing plan

Request: `/plan-smith update tmp/sso-plan.md` then "login flow and session
storage are done; we're dropping the separate docs item."

Expected behavior:

- Flips login flow and session storage to `[x]` / `Y`; marks docs `X` with a
  one-line reason; leaves provider config `N`.

- Rewrites the summary table to match; preserves all other prose; renumbers
  nothing and drops nothing.

- Reports the new counts (e.g. `2 Y / 1 N / 1 X`).

### 3. Hand off from grill-me

Request: After a `grill-me` session reaches alignment, "turn this into a plan."

Expected behavior:

- Reuses the resolved branches as plan items without re-interviewing.

- Carries each branch's acceptance criteria into its section.

### 4. Terse output

Request: Any create or update run.

Expected behavior:

- After writing, gives a one-line pointer and the status counts (e.g. `wrote
  tmp/sso-plan.md — 0 Y / 4 N / 0 X`), not the whole plan pasted back.

- No preamble or narration.

## Relationship to other skills

- `grill-me` — run first to align on what to build; plan-smith persists the
  result as a tracked plan.

- `skill-smith` — authored and audits this skill.
