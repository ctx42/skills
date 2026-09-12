# skill-smith

Forges new skills, repairs existing ones, and measures whether they work.

## Usage

```
/skill-smith                  (default) infer create/improve/measure from the request; asks if ambiguous
/skill-smith create <desc>    scaffold a whole new standard-compliant skill with evals
/skill-smith improve <skill>  audit a skill against the standard, report, fix on confirmation
/skill-smith measure <skill>  A/B-benchmark the skill's README scenarios and test triggering
```

## Modes

- Create is evals-first. It settles the scope and name with you, writes the
  evaluation scenarios before the body, then produces the directory,
  `SKILL.md`, `README.md`, and the catalog-doc updates.

- Improve reports before it touches anything. Findings come back grouped
  Blocker / Should-fix / Nit, each naming the rule it breaks and the minimal
  fix; nothing is edited until you approve.

- Measure runs each README scenario twice — with the skill and without — in
  fresh subagents, grades both legs blind, and scores how reliably the
  description triggers. It reports; it never edits.

It targets Claude Code only: skills carry `name` + `description` plus the
Claude-native affordances (`argument-hint`, `$ARGUMENTS`/`$N`, dynamic
injection) wherever they earn their place. It enforces
[standards.md](standards.md) and defers to
[CONTRIBUTING.md](../../../CONTRIBUTING.md) for repo mechanics.

## Evaluations

### 1. Create a new skill from a description

Request: `/skill-smith create a skill that converts CSV files to Markdown
tables`

Expected behavior:

- Asks for / proposes a name equal to the dir name (e.g. `csv-to-markdown`),
  no reserved words.

- Writes `SKILL.md` with valid frontmatter (`name` + `description`, plus
  `argument-hint` if it takes arguments), a third-person, what + when
  description, the output-discipline line, and a closing `## Self-learning`
  block.

- Writes `README.md` with `## Usage` right after the intro and an
  `## Evaluations` section with ≥ 3 scenarios.

- Lists the catalog-doc updates per CONTRIBUTING.md and reminds you to run
  `/reload-plugins`.

### 2. Improve an existing skill with an invalid frontmatter field

Request: `/skill-smith improve` a skill that declares `user_invocable: true` and
whose README has no `## Evaluations` section.

Expected behavior:

- Reports `user_invocable: true` as a Blocker: not a valid Claude Code
  frontmatter key (Claude Code gates invocation with
  `disable-model-invocation`); recommends removing it.

- Confirms `name` equals the dir name and the description is well-formed.

- Reports the missing `## Evaluations` section in the README as a Should-fix.

- Reports findings by severity first, then offers to apply fixes — no edits
  before confirmation.

### 3. Disambiguate an unclear request

Request: `/skill-smith help me with skills`

Expected behavior:

- Recognizes the request names no mode.

- Asks exactly one question: create, improve, or measure?

- Does not scaffold, edit, or benchmark anything until the mode is known.

### 4. Enforce output discipline

Request: `/skill-smith improve a skill whose report re-lists every finding in a
closing summary`

Expected behavior:

- Flags the duplicate closing summary against the Output discipline rule.

- Confirms the body carries the canonical terse-output line; adds it if missing.

- Checks the README has ≥ 1 eval asserting terse output.

- Its own audit report opens with the payload — no preamble or narration, no
  restating of findings already shown.

### 5. Audit reference content and preloading

Request: `/skill-smith improve` a skill whose keyed reference restates its own
terse rules and whose workflow reads that reference whole every run.

Expected behavior:

- Reads the reference's content, not just its structure (one hop, ToC, naming).

- Flags entries that restate the rule they key to, or that collapse to one
  shared principle, as redundant reference bloat.

- Flags the workflow step that preloads the whole reference — on-demand saves
  tokens only if the read is deferred.

- Reports findings by severity; makes no edits before confirmation.

### 6. Measure a skill's real effect

Request: `/skill-smith measure cm`

Expected behavior:

- Builds a rubric from the skill's README scenarios and runs each with and
  without the skill loaded in fresh subagents, per `references/evals.md`.

- Grades the delta and reports a per-scenario table plus a trigger
  recall/precision score.

- States a verdict (earns its tokens / no measurable effect) and makes no edits
  from the run without confirmation.

- Opens with the result table — no preamble or narration.

### 7. Audit a skill's scope and its gotchas

Request: `/skill-smith improve` a skill that covers both querying a database
and administering it, and whose only non-obvious rule sits in a reference file
as "handle errors appropriately".

Expected behavior:

- Flags the double scope against the Scope rule — two unrelated trigger sets
  belong in two skills.

- Flags "handle errors appropriately" as general advice, not a gotcha, and asks
  for the concrete correction it stands in for.

- Flags that gotcha living in a reference: the agent cannot know to load a file
  about a trap it does not know exists.

- Reports by severity; makes no edit before confirmation.

## Relationship to other skills

- `grill-me` — use it first when a new skill's purpose or triggers are fuzzy;
  `skill-smith` create mode assumes the scope is already clear.

- `enhance-skills` — owns the `## Self-learning` block create mode installs
  and records lessons into skills after a run.

- `standards.md` — the ruleset; edit it as the authoring standard evolves.

- `CONTRIBUTING.md` — authoritative for catalog updates, naming, syncing,
  retiring. `skill-smith` follows it rather than restating it.
