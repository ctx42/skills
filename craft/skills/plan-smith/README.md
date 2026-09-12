# plan-smith

Writes a trackable implementation plan — numbered checkbox items plus a status
table (Y implemented, N not yet, X rejected) — and refreshes it as work lands.

## Usage

```
/plan-smith <request>           (default) infer write vs. update from the request; asks if ambiguous
/plan-smith write <brief>       create a tracked plan from a brief or a grill-me summary
/plan-smith update <plan-file>  re-read the plan and refresh each item's checkbox and status
```

The plan format itself (summary table, item sections, checkbox-to-status
mapping, table alignment) is specified once, in `SKILL.md` → Format.

## When to Use

- You've settled what to build and want it captured as a checklist with status.

- You have a plan in chat and want it persisted and trackable.

- You're returning to a plan and want its status table brought up to date.

## Evaluations

### 1. Write a plan from a brief

Request: `/plan-smith` then "plan the work to add SSO: provider config, login
flow, session storage, and docs."

Expected behavior:

- Produces one numbered checkbox section per item and a `## Summary` table with
  the `Y / N / X` legend.

- All items start `N` and unchecked; each carries acceptance criteria.

- Summary table columns align: separator dashes flush to the pipes, every row
  the same character width, no Item cell longer than ~30 chars.

- Confirms the file path before writing; does not overwrite silently.

### 2. Update an existing plan

Request: `/plan-smith update tmp/sso-plan.md` then "login flow and session
storage are done; we're dropping the separate docs item."

Expected behavior:

- Flips login flow and session storage to `[x]` / `Y`; marks docs `X` with a
  one-line reason; leaves provider config `N`.

- Rewrites the summary table to match; preserves all other prose; renumbers
  nothing and drops nothing.

- Reports the deltas and the new counts (e.g. `2 Y / 1 N / 1 X`).

### 3. Hand off from grill-me

Request: After a `grill-me` session reaches alignment, "turn this into a plan."

Expected behavior:

- Reuses the resolved branches as plan items without re-interviewing.

- Carries each branch's acceptance criteria into its section.

### 4. Ambiguous request

Request: `/plan-smith` then "the SSO plan" with no further context.

Expected behavior:

- Asks exactly one question — write a new plan or update an existing one — and
  proceeds on the answer.

### 5. Terse output

Request: Any write or update run.

Expected behavior:

- After writing, gives a one-line pointer and the status counts (e.g. `wrote
  tmp/sso-plan.md — 0 Y / 4 N / 0 X`), not the whole plan pasted back.

- No preamble or narration.

## Relationship to other skills

- `grill-me` — run first to align on what to build; plan-smith persists the
  result as a tracked plan.

- `skill-smith` — audits this skill against the authoring standard.
