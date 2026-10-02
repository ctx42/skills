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

Turn a brief into a tracked plan, and keep its status current. The first token
of the invocation is the mode when given — `write` (the rest is the brief) or
`update` (the rest is the plan-file path); else infer the mode from the
request:

- Write — a new plan from a description, a spec, or a shared understanding
  reached with `grill-me`.

- Update — re-read an existing plan and refresh each item's checkbox and status
  from what has since happened.

If the request is ambiguous, ask one question: write a new plan or update an
existing one?

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see. After writing, point to the file and give the
status counts (e.g. `wrote tmp/sso-plan.md — 0 Y / 5 N / 0 X`); never paste
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

The file opens with `# <Title>`, then a blank line, then the summary table, so
status is visible at a glance:

```
# <Title>

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

- Each column's width is its widest cell's content, counting the header as a
  cell — except `#`, which is never narrower than two, so single-digit plans
  still read `| #  |` as the template and both bundled plans do, and reaching
  item 10 changes nothing.
- Widening is required, narrowing is not. When editing an existing plan whose
  columns are already wider than the content needs, keep its widths and pad the
  new row to match: a plan is edited far more often than it is written, and
  re-padding a whole table to shave a space rewrites lines nobody changed.
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
so the record stays honest. That heading stays on one physical line however
long the reason makes it: a wrapped heading is not a heading, and it is the one
place the file is exempt from the prose wrap. Keep the reason short enough that
the exemption barely shows.

The last item is always the closing one, worded exactly so:

```
## <n>. Remove this plan — [ ]

When every other item is `Y` or `X`, ask the user whether to delete this file.

Done when: the user has answered — yes deletes the file, no marks this item `X`.
```

It is the only item the skill adds on its own and the only one whose number may
change: it moves down when work is appended, so it stays last. A finished plan
left on disk reads as live work; asking once, at the end, keeps that the user's
call.

## Write mode

1. Gather the items. From the brief (or a `grill-me` summary), list the
   distinct, independently-checkable pieces of work — one item = one outcome;
   split bundled work into the outcomes it actually needs.

2. Keep the items the brief's. Splitting a named problem into its real parts is
   the job; adding work nobody raised — tests, monitoring, retention, rollout,
   a guard so it can't recur — is not, however sensible it looks. Those are
   suggestions: name them in the reply, one line each, and let the user turn
   one into an item. Written in unasked, they sit at `N` forever and make the
   counts lie about what was agreed. The closing item is the one exception.

3. Settle what the brief left open before writing, not inside the file. An
   outcome nobody has chosen has no acceptance criteria, so it can never be
   honestly checked off, and a guess written down reads afterwards as a
   decision the user made. Ask the one open question that most changes what the
   items are; a detail inside an already-decided outcome is not that question —
   the item's acceptance criteria absorb it. When several are open and the
   shape is still moving, say so and offer `grill-me` rather than dripping
   questions one per turn. Several open but the shape firm is not that case:
   ask the one that most changes the items, and name the rest in the reply's
   leave-outs, where they stay the user's to decide.

4. Order by dependency and impact — blocking and highest-impact items first.

5. Write the file to the format above: summary table (every item starts `N`,
   unchecked) then one section per item, closing item last. Give each item
   acceptance criteria — what proves it done — so `Y` is verifiable, not
   asserted. Path: the name the user gives, else `tmp/<slug>-plan.md` relative
   to the working directory; no need to ask, the report names it.
   If something is already there, say so and ask before overwriting.

## Update mode

1. Read the existing plan. Take its item list and current statuses as ground
   truth; never renumber or drop items.

2. Set each item's new status from evidence: implemented → `[x]` / `Y`;
   dropped → `X` + one-line reason; untouched → leave `N`.

   Evidence is what the repo shows. "I did that one" is a claim, and a claim is
   where to look, not what to record — go and see: the code, the test, the
   command's output. A plan's whole value is that its table can be trusted
   without re-reading the code, which survives exactly as long as nothing is
   marked `Y` on someone's say-so. What you could not verify stays `N` and is
   named in the report as unverified, not silently promoted or silently left.

   Judge an item against its own acceptance criteria, not against how finished
   the area looks: an item asking for 429 *with* `Retry-After` is not done by a
   429 alone. Part-done stays `N` — there is no half status, and inventing one
   would make the table unreadable — but the report says what landed and what
   is missing, so the gap is visible without re-reading the code.

   Some criteria the repo cannot settle either way: a staging round trip, a
   thing only a human has seen work. Those stay `N` too, named as unverifiable
   *here* rather than unmet, which tells the user it needs their eyes and not
   more code.

   A brief may carry an item that is a question for a named person rather than
   work in the repo — `grill-me` hands over open branches that way. Its
   criterion is that the answer is recorded, and only the user can settle it;
   the repo never can, so it is never promoted here.

   So `Y` needs every criterion settled in the repo. One unmet, one only a
   human can settle, one the user says is done but nothing in the repo shows —
   any single one holds the item at `N`. An item half checkable and half
   staging-only is not a third case needing its own rule: it is an item with a
   criterion that did not settle.

3. Append work the plan does not carry yet that the user or the repo names —
   a need the user reports, a `TODO` in the code: new items after the last
   work item with fresh numbers, status `N`, and the same shape as the rest;
   the closing item moves down one number per new item and stays last. Take
   their acceptance criteria from what was stated; an open choice inside one
   goes to the report's leave-outs, as in write step 3. Never renumber
   anything else to slot one into the middle — the numbers are how the table
   and the sections stay married. A plan with no closing item (written before
   it existed) gets one appended.

4. Rewrite the summary table and the changed items' checkboxes/tags only, so
   table and sections keep the same numbering and statuses; leave all other
   prose intact.

5. Report the deltas, the new counts, and anything left `N` for want of
   evidence.

6. When every item but the closing one is now `Y` or `X`, end the report by
   asking whether to delete the plan file — after the rewrite, so the update
   is on disk whatever the answer; never delete unasked. Yes: delete it and
   say so. No: tag the closing item `(X: rejected — the user kept the plan)`
   and fix its table row, so the question is not asked again.

## Self-learning

Obey this skill's lessons when it has any: read both a sibling `LESSONS.md` and
`${AGENT_DATA_DIR:-$HOME/.agent-data}/ctx42-skills/lessons/craft/plan-smith.md`,
the sibling winning a conflict — a read-only install writes the second, and what
it learned there stays true once the checkout is writable again. Most runs have
none; absence is the normal case and needs no comment. On a correction or
self-caught mistake, append a one-line rule to the sibling when this directory
is writable, else to the fallback, creating it, and report where.