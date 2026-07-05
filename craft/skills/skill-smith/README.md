# skill-smith

Forge new skills and repair existing ones in this repo. One skill, two modes,
chosen from how you ask:

- **Create** — describe a capability and it scaffolds the whole skill: directory,
  `SKILL.md`, `README.md` (with evals), catalog-doc updates, and the sync.
- **Improve** — name an existing skill and it audits against the authoring
  standard, reports findings by severity, then fixes them on your confirmation.

**The rule it lives by:** every skill must be valid in *both* Claude and Grok,
so frontmatter is strict-portable — `name` + `description` only (plus standard
optional fields). It enforces [standards.md](standards.md), and defers to
[CONTRIBUTING.md](../CONTRIBUTING.md) for repo mechanics.

## Usage

```
/skill-smith create a skill that lints Markdown tables   # create mode
/skill-smith improve cover                               # improve, one skill
/skill-smith review cm                                   # audit by name
```

You don't need a mode keyword — it infers create vs improve from the request.
Create new capability → CREATE. Name an existing skill → IMPROVE.

- **Create** asks only what it can't infer (name, group, triggers), then
  scaffolds under the group's `skills/` dir and reminds you to `/reload-plugins`.
- **Improve** defaults to the single skill you name, deep. It reports before it
  edits.

## Evaluations

### 1. Create a new skill from a description

**Request:** `/skill-smith create a skill that converts CSV files to Markdown
tables`

**Expected behavior:**
- Asks for / proposes a portable name equal to the dir name (e.g.
  `csv-to-markdown`), no reserved words.
- Writes `SKILL.md` with strict-portable frontmatter (`name` + `description`
  only) and a third-person, what + when description.
- Writes `README.md` including an `## Evaluations` section with ≥ 3 scenarios.
- Lists the catalog-doc updates per CONTRIBUTING.md and reminds you to run
  `/reload-plugins`.

### 2. Improve an existing skill with a portability violation

**Request:** `/skill-smith improve cm`

**Expected behavior:**
- Reports `user_invocable: true` as a Blocker: non-portable platform field and
  misspelled (`user-invocable`); recommends removing it.
- Confirms `name` equals the dir name and the description is well-formed.
- Reports the missing `## Evaluations` section in the README as a Should-fix.
- Reports findings by severity first, then offers to apply fixes — no edits
  before confirmation.

### 3. Disambiguate an unclear request

**Request:** `/skill-smith help me with skills`

**Expected behavior:**
- Recognizes the request is ambiguous between create and improve.
- Asks exactly one question: create a new skill, or improve an existing one?
- Does not scaffold or edit anything until the mode is known.

### 4. Enforce output discipline

**Request:** `/skill-smith improve a skill whose report re-lists every finding in
a closing summary`

**Expected behavior:**
- Flags the duplicate closing summary against the Output discipline rule.
- Confirms the body carries the canonical terse-output line; adds it if missing.
- Checks the README has ≥ 1 eval asserting terse output.
- Its own audit report opens with the payload — no preamble or narration, no
  restating of findings already shown.

### 5. Audit reference content and preloading

**Request:** `/skill-smith improve` a skill whose keyed reference restates its own
terse rules and whose workflow reads that reference whole every run.

**Expected behavior:**
- Reads the reference's content, not just its structure (one hop, ToC, naming).
- Flags entries that restate the rule they key to, or that collapse to one shared
  principle, as redundant reference bloat.
- Flags the workflow step that preloads the whole reference — on-demand saves
  tokens only if the read is deferred.
- Reports findings by severity; makes no edits before confirmation.

## Relationship to other skills

- `grill-me` — use it first when a new skill's purpose or triggers are fuzzy;
  `skill-smith` create mode assumes the scope is already clear.
- `standards.md` — the ruleset; edit it as the authoring standard evolves.
- `CONTRIBUTING.md` — authoritative for catalog updates, naming, syncing,
  retiring. `skill-smith` follows it rather than restating it.
