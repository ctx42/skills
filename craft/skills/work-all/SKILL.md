---
name: work-all
description: >
  Works off every agent work file (plans, handoffs, bugs, features, todos,
  debt) in the repositories under a root folder with up to five subagents, one
  per repository, each item committed; this session orchestrates and asks the
  user every question. Use when asked to work through, execute, or clear all
  the agent files, plans, and handoffs across repos.
argument-hint: "[root]"
license: MIT
---

# work-all

## Usage

```
/craft:work-all          work off every work file under the current folder
/craft:work-all <root>   the same under <root>
```

This session becomes the orchestrator: it finds the work, asks the user
everything it can foresee up front, runs one worker subagent per unit, relays
every later question, and reports. Workers do the work; only the orchestrator
talks to the user. Report tersely: no preamble or narration; state each fact
once.

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

## Work files

A work file is `agent-plan-*.md`, `agent-handoff-*.md`, `agent-bug-*.md`,
`agent-feature-*.md`, `agent-todo.md`, or `agent-dept-*.md` (dept is debt).
Every other `agent-*` file (`agent-decisions.md`, a script, an image) is seen,
reported, and never changed. The work in each:

- plan: each N item of its status table, in plan order; X items stay
  untouched. A plan without a status table is scoped by the user up front.
- handoff: its in-progress and open-items lines.
- bug, feature: the whole file, built test-first.
- todo: each item, sorted up front by what it waits for.
- dept: the entries under `## Open`; "None." there is no work.

A unit is one git repository (the top level of the file's folder) or, for a
file outside any repository, its folder: a no-repo unit, worked without
commits.

## 1. Discover

1. The root is the target, else the current folder. Find the run file
   (section 5). One with unfinished items: offer to resume it. On yes, load
   its selection, answers, order, and status, and go on at section 3 with
   what is left; never ask again a question it records an answer to.
2. Find every `agent-*` file under the root at any depth, outside `.git/`,
   `node_modules/`, and `vendor/`, and group each into its unit
   (`git -C <dir> rev-parse --show-toplevel`).
3. Skip every path the user's loaded instructions (`CLAUDE.md`, `AGENTS.md`,
   rules files) mark read-only or forbid editing; record each with the rule
   that skips it.
4. Read every work file. Record each unit's start commit and branch.

## 2. Plan and ask — before any dispatch

1. Class each item: **runs** (nothing blocks it), **asks** (it needs a choice
   only the user has: a plan without a status table, a todo that waits on a
   design or a decision), or **waiting** (its condition cannot be met now: a
   todo that waits for a second failure or for an event nobody can cause) —
   reported and left alone. A todo whose condition is met now (a release
   exists, a fix landed) runs.
2. Order units by dependency: a unit whose manifest (`go.mod`,
   `package.json`) requires a module another selected unit holds goes after
   that unit; a handoff that names another unit's work goes after it; else
   path order.
3. Show one list: the units in order, each with its items and their class;
   then the skipped paths with their rule, the no-repo units, and the
   seen-not-work files. Then ask, one question per message, most blocking
   first, saying how many remain: which units or files to skip; every asks
   item; every other decision the files let you foresee; and, when
   `systemd-run` is missing, how many workers to run. Write each answer to the
   run file as it comes.
4. Edit nothing, commit nothing, and start no agent before the last answer.

## 3. Dispatch

Run at most five agents at once, workers and the agents this session starts
for a skill together; never two on one unit. A worker's `go-change-reviewer`
reads code and builds nothing: it counts toward neither the five nor the
budget and starts at once, even as a sixth agent.

Before each dispatch, budget the machine: read `nproc`, `uptime`, and `free`;
the budget is available memory minus 4 GB minus the caps of the running
workers. A new worker gets a cap of min(4 GB, budget); none starts while the
budget is under 1.5 GB. Log the reading and the cap in the run file.

Dispatch the next unit in order whose dependencies are done, as a background
general-purpose agent whose prompt is the brief in
[references/worker.md](references/worker.md), filled in. A worker knows only
its brief. Put only what its items name in a brief; before adding a step of
your own, check that it changes something in that unit. `craft:cm` owns the
commit message, so add no trailer instruction, and never mention trailers or
their absence in the report.

## 4. While workers run

A worker ends each turn with one status line (see the brief). Act on it:

- **DONE**: record its commits and file changes in the run file. For each
  `new-file:` line (work it wrote into another unit), show the file and its
  source item and ask: approve or skip. Approved: the item joins the
  selection and counts in M; queue its unit in dependency order. A finished
  unit runs again with a fresh brief and a budgeted dispatch, and still
  counts once in U. Then dispatch the next unit.
- **QUESTION**: queue it. Ask queued questions one at a time, most blocking
  first, saying how many remain; resume that worker (`SendMessage`) with the
  answer. The other workers keep going.
- **FAILED** (a test it cannot fix, a broken build, a stall, a kill at its
  memory cap): ask the user to pick: retry with guidance; park — the worker
  records the item in the unit's `agent-todo.md` with what it waits for and
  undoes its own edits by inverse edit; or stop the unit — its edits stay
  uncommitted and it writes `tmp/agent/agent-handoff-<topic>.md`. Hold every
  unit that depends on it.
- **NEEDS-SKILL**: the item needs a looping or fan-out skill. Run it yourself
  within the five, or ask the user, then resume the worker.

Release pause: once every selected item of a library unit is done and a later
unit needs its new code, tell the user "release and push <module>, then reply
with the tag", and keep the other workers busy. On the tag, the consumer's
worker raises its requirement to exactly that tag (`go get <module>@<tag>`
and `go mod tidy`; the package manager's equivalent elsewhere) as its first
commit. That is the only dependency bump this skill makes; starting it
allows that one. Never tag, release, push, bump a version, or edit a
`CHANGELOG.md` or `VER` file.

## 5. Run file

`agent-run-<root folder name>.md`: in `<repo>/tmp/agent/` when started
inside a repository; else in `<start>/tmp/agent/` when `<start>/tmp/` exists;
else in the start folder. Rewrite it as work moves, keeping these sections:
`## Selection`, `## Answers`, `## Order`, `## Status` (unit, item, status,
commits), `## Budget`, and, at the end, `## Report`. Write it with the file
tools (Write, Edit), never through the shell.

## 6. Report

Once no worker runs and nothing is queued. Read every count and hash off
`git log <start>..HEAD` in each unit and off the run file, never from memory.
Print exactly this shape, the count line first:

```
worked 9 of 14 items in 11 commits across 4 units

| Unit | Done | Commits | Open |
|------|------|---------|------|
| lib  | 3/3  | 4       | 0    |

Open
- release: example.com/lib — release and push, then reply with the tag
- parked: app agent-plan-x.md #4 — go test ./api fails (handoff written)
- waiting: tools agent-todo.md — waits for a second failure
- uncommitted: notes/ — 2 files changed (no repository)
```

`worked N of M items in K commits across U units`: M counts the selected items,
mid-run approvals included; N the finished ones — a plan item a worker found
already done and marked Y counts toward N though it has no commit; K every
commit the workers made; U the units worked. Align the table. Omit an empty
section. Then write `## Report` into the run file: each item with its commit
hashes, the files deleted, the files written into other units, the seen-not-work
files, the skipped paths with their rule, and the Open list exactly as the chat
shows it. End the reply with the run file's path.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/craft/work-all.md` (pass `~` as
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
