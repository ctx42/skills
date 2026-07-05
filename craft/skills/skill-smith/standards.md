# Skill Authoring Standards

The canonical ruleset `skill-smith` writes and audits against. Fuses Anthropic's
[skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
with this repo's house rules. Terse by design: every rule is one enforceable
line. Repo mechanics (catalog updates, naming, syncing, retiring) live in
[CONTRIBUTING.md](../CONTRIBUTING.md) — this doc references it, never
duplicates it.

## Contents

- Frontmatter (strict-portable)
- Description quality
- Token performance
- Body: conciseness
- Output discipline
- Progressive disclosure
- Degrees of freedom
- Workflows & feedback loops
- Content hygiene
- Scripts & bundled files
- Evaluations
- Anti-patterns
- Authoring checklist

## Frontmatter (strict-portable)

This repo's skills ship as Claude Code plugins and run in **both** Claude and
Grok (Grok reads Claude marketplaces and plugins directly). Both read the
[agentskills.io](https://agentskills.io/specification) open standard, so write
only standard fields.

- **Required:** `name`, `description`.
- `name` — lowercase, hyphens/numbers only, ≤ 64 chars, **must equal the parent
  directory name**. No reserved words (`anthropic`, `claude`). No org or
  vendor prefix. Prefer gerund (`writing-x`) or a short verb; match repo terseness.
- `description` — see next section. ≤ 1024 chars.
- **Allowed optional** (standard, portable): `license`, `version`, `tags`,
  `author`, `metadata`. Use sparingly.
- **Forbidden** (platform extensions — break portability): `user-invocable`,
  `user_invocable`, `disable-model-invocation`, `when_to_use`, `arguments`,
  `argument-hint`, `context`, `agent`, `allowed-tools`, `disallowed-tools`.
- **Forbidden in body:** dynamic injection (`` !`cmd` ``), `$ARGUMENTS` / `$N`
  substitution. Detect mode and arguments by reading the user's prose instead.
- Side-effecting skills (commit, deploy, edits, sync) cannot use
  `disable-model-invocation` here — rely on permission prompts and explicit
  confirmation in the body before any irreversible step.

## Description quality

The description is how the agent decides to load the skill. It is the single
highest-leverage field.

- **Third person.** "Reviews X", not "I review X" or "You can review X".
- State **what it does AND when to use it** — include concrete trigger terms.
- Specific, not vague. ✗ "Helps with documents" ✓ "Extracts text and tables
  from PDFs. Use when the user mentions PDFs, forms, or extraction."
- Put the key use case first (listing text is truncated downstream).
- Include triggers **naturally** — Grok's validator penalizes keyword-stuffed
  descriptions. Write a real sentence, not a tag dump.
- **YAML scalar safety.** A plain scalar breaks on `: ` (colon-space) or a
  leading `>`/`<`. Use a folded block scalar (`description: >`) for multi-line
  or any description containing a colon — it is valid YAML, supported by both
  Claude and Grok, and is the repo default. Never "fix" a colon by deleting the
  block scalar.

## Token performance

Conciseness and output discipline both serve one metric: **tokens spent per unit
of outcome**. Treat it as a hard budget the skill must earn against, not a nicety.

- Every token must earn its place. If cutting a word, line, or example does not
  lower the skill's success rate, cut it.
- Optimize the always-loaded surface first: the `description` and the `SKILL.md`
  body cost tokens on **every** trigger. Push anything not needed each run into
  on-demand references (see Progressive disclosure).
- On-demand saves tokens **only if the workflow defers the read**. A step that
  eagerly loads a whole reference every run (`read rules.md once`) makes it
  always-loaded in practice — consult a keyed or large reference per-need, never
  preload it wholesale.
- Shortest phrasing that stays unambiguous wins. Terse-but-precise beats verbose;
  it also beats cryptic — do not compress past the point of clarity.
- Judge by tokens-to-outcome, not line count — a padded 400-line body can cost
  more than a lean 500-line one.

## Body: conciseness

- **Assume the model is already smart.** Add only what it does not know. Cut any
  sentence that explains a common concept.
- **These tests apply to every loaded file, not just the body.** A reference must
  also cut what the model already knows: a keyed reference that restates the terse
  rule it keys to, or whose entries collapse to one shared principle, is
  duplication dressed as detail — trim each entry to the non-obvious (exemption,
  detection heuristic) or drop it.
- Once loaded, body content persists across turns — every line is a recurring
  token cost. Keep the body **under ~500 lines**; split sooner if it sprawls.
- Imperative and dense. State what to do, not why — **unless the why lets the
  agent generalize** to cases the skill did not spell out; then state the rule,
  then the reason. Keep bare imperatives for fragile, one-right-way steps.
- One consistent term per concept throughout (don't mix "field/box/element").
- **Model-agnostic.** Write for "the agent", never a named product. No "ask
  Claude", "in Grok", "Claude will…". Naming a runtime breaks portability and
  wastes tokens for the other.

## Output discipline

Conciseness above governs the static body. This governs what a running skill
**says back** each turn — a recurring, per-run token cost that the body rules
never touch. Every skill this repo ships must make its agent report tersely.

- **Cut framing.** No preamble ("I'll now review…"), no step narration ("Let me
  read the file"), no closing filler ("Hope this helps"). Open with the payload.
- **State each fact once.** Don't restate output the user can already see. No
  closing summary that repeats findings, a diff, or an artifact just shown. A
  short pointer ("wrote `x.md`") is fine; re-listing its contents is not.
- **Never cut the payload.** Terseness applies to framing and restating only.
  The substantive result — findings, diffs, the written artifact, a required
  status table — is always stated in full. A review still lists every finding.
- **Every skill carries the rule in its body.** A produced `SKILL.md` must
  contain an explicit output-discipline line so the rule bites at runtime, not
  only when skill-smith is authoring. Canonical wording: *Report tersely: no
  preamble or narration; state each fact once; don't restate output the user can
  already see.* Place it where the skill describes its output.

## Progressive disclosure

Three load levels: metadata (always) → `SKILL.md` body (on trigger) → bundled
files (on demand). Exploit it:

- `SKILL.md` is a table of contents that points to detail; move large reference
  material, schemas, and long examples into sibling files. Conventional layout
  (agentskills.io): `scripts/` (executable code), `references/` (docs loaded on
  demand), `assets/` (templates, examples). Use these names; avoid deep nesting.
- **References one level deep.** Every bundled file links directly from
  `SKILL.md`. Never chain `SKILL.md` → a.md → b.md — the agent may only preview
  nested files.
- Name bundled files for their content (`standards.md`, `rules.md`), not
  `doc2.md`. Use forward slashes always.
- Any reference file over ~100 lines starts with a Contents list.
- Structure is necessary, not sufficient: a well-formed reference (one hop, ToC,
  named for content) can still bloat with restated or duplicated content — audit
  the content by the conciseness tests, and confirm the workflow reads it on
  demand rather than preloading it whole.

## Degrees of freedom

Match specificity to task fragility:

- **High** (prose steps) — many valid approaches, context decides. e.g. reviews.
- **Medium** (templates/pseudocode with parameters) — a preferred pattern, some
  variation ok.
- **Low** (exact commands, no improvisation) — fragile, must-be-consistent,
  ordered operations. e.g. migrations.

## Workflows & feedback loops

- Break multi-step tasks into clear numbered steps; for long ones, give a
  checklist the agent copies and ticks off.
- Build in validate → fix → repeat loops for quality-critical output. The
  "validator" can be a script or a reference doc the agent checks against.
- For risky/batch work, emit a verifiable intermediate plan and validate it
  before executing.

## Content hygiene

- **No time-sensitive info** ("after August 2025…"). Put superseded guidance in
  an "Old patterns" section instead.
- Concrete examples beat abstract description — show input/output pairs when
  output quality depends on format.
- Provide one default with an escape hatch, not a menu of options.

## Scripts & bundled files

Scripts are portable, so allowed. When you include them:

- **Solve, don't punt** — handle errors in the script rather than failing to the
  agent.
- No voodoo constants — justify every magic value in a comment.
- Make intent explicit: "Run `x.py`…" (execute) vs "See `x.py` for the
  algorithm" (read as reference).
- Don't assume packages are installed — state dependencies.

## Evaluations

Mandatory and written before finalizing (eval-driven development):

- Every skill's `README.md` has an `## Evaluations` section with **at least 3
  scenarios**. Each scenario: a representative request + the expected behavior
  (2–4 bullet checks).
- **At least one scenario asserts terse output** per the output-discipline rule:
  no preamble or narration, payload stated once, no closing summary that repeats
  shown content.
- Build evals from real gaps: run the task without the skill, note what failed,
  encode that as a scenario.
- Develop iteratively — author the skill, run it on the scenarios, observe where
  it struggles, refine. Strengthen the description first when it fails to
  trigger.

## Anti-patterns

- Windows paths (`scripts\x.py`) — always forward slashes.
- Offering too many options — pick a default.
- Vague names (`helper`, `utils`) or vague descriptions.
- Deeply nested references.
- Preloading a whole reference each run — negates the on-demand saving; consult
  keyed references per-need.
- A reference that restates the rule or file it keys to, or repeats itself — bloat
  dressed as detail.
- Chatty runtime output — preamble, narration, or a closing summary that restates
  what the user already sees.
- Frontmatter beyond the strict-portable set.
- Restating CONTRIBUTING.md mechanics here — reference it.

## Authoring checklist

- [ ] `name` equals dir name; lowercase-hyphen; no reserved words / org prefix.
- [ ] Frontmatter is `name` + `description` (+ allowed optional only).
- [ ] Description: third person, what + when, specific triggers, key use first.
- [ ] Token performance: always-loaded surface (description + body) carries only
      what raises success rate; on-demand detail pushed to references.
- [ ] Body under ~500 lines, dense, consistent terms, no time-sensitive info.
- [ ] Output discipline: body carries the terse-output line; no framing or
      restating mandated; payload always stated in full.
- [ ] References one level deep; files named for content; ToC if > ~100 lines.
- [ ] References earn their tokens too: no restating the model's knowledge or the
      rule they key to; entries don't collapse to one shared principle.
- [ ] On-demand references are consulted per-need, not preloaded whole each run.
- [ ] Degrees of freedom match task fragility.
- [ ] Multi-step work has clear steps / checklist; quality work has a feedback
      loop.
- [ ] Scripts (if any) solve-not-punt, no voodoo constants, deps stated.
- [ ] `README.md` exists with usage and `## Evaluations` (≥ 3 scenarios, ≥ 1
      asserting terse output).
- [ ] Skill lives under a plugin group's `skills/` dir; catalog docs updated and
      `dev/lint-skills.sh` passes — per CONTRIBUTING.md.
