# Skill Authoring Standards

The canonical ruleset `skill-smith` writes and audits against. Fuses Anthropic's
[skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
with this repo's house rules. Terse by design: every rule is one enforceable
line. Repo mechanics (catalog updates, naming, syncing, retiring) live in
[CONTRIBUTING.md](../../../CONTRIBUTING.md) — this doc references it, never
duplicates it.

## Contents

- Frontmatter
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

## Frontmatter

This repo's skills ship as Claude Code plugins and run in **both** Claude and
Grok (Grok reads Claude marketplaces and plugins directly). Both read the
[agentskills.io](https://agentskills.io/specification) open standard, so write
only standard fields.

- **Required:** `name`, `description`.
- `name` — lowercase, hyphens/numbers only, ≤ 64 chars, **must equal the parent
  directory name**. No reserved words (`anthropic`, `claude`), no org/vendor
  prefix, no vague names (`helper`, `utils`). Prefer a gerund (`writing-x`) or
  short verb.
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

The description is how the agent decides to load the skill — its single
highest-leverage field.

- **Third person.** "Reviews X", not "I review X" or "You can review X".
- State **what it does AND when to use it** — include concrete trigger terms.
- **No workflow leak.** Say *when to use it*, never how it works: no mode
  lists, control/flag names, file paths, or step summaries. An agent acts on a
  leaked summary and skips the body — the very steps the skill exists to
  enforce. Every clause serves discovery.
- **Lean pushy on *when*.** Agents tend to under-trigger, so make the use-cases
  assertive ("Use when…") and cover oblique phrasings — while still never
  leaking *how* (above).
- **Size.** Aim ≤ ~350 chars (hard limit 1024) — the description is paid in
  every session, for every skill, whether or not it fires.
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
- Shortest phrasing that stays unambiguous wins — terse-but-precise, never
  cryptic; don't compress past clarity.
- Judge by tokens-to-outcome, not line count — a padded 400-line body can cost
  more than a lean 500-line one.

## Body: conciseness

- **Assume the model is already smart.** Add only what it does not know. Cut any
  sentence that explains a common concept.
- **One rule = one dense imperative line** in the body or style list. Expand in a
  reference only when the line alone is not enough to enforce.
- **Keyed / reference entries stay short.** Why + Detect in ≤2 sentences; no
  multi-paragraph rationale. Prefer no example; a code fence only when the rule
  is ambiguous without one (fragile format, non-obvious shape). Drop the entry
  when the body line is enough.
- **These tests apply to every loaded file, not just the body.** A reference must
  also cut what the model already knows: a keyed reference that restates the terse
  rule it keys to, or whose entries collapse to one shared principle, is
  duplication dressed as detail — trim each entry to the non-obvious (exemption,
  detection heuristic) or drop it.
- Once loaded, body content persists across turns — every line is a recurring
  token cost. Keep the body **under ~500 lines**; split sooner if it sprawls.
- Imperative and dense. State what to do, not why — **unless the why lets the
  agent generalize** to cases the skill did not spell out; then state the rule,
  then the reason in one short clause. Keep bare imperatives for fragile,
  one-right-way steps.
- One consistent term per concept throughout (don't mix "field/box/element").
- **Model-agnostic.** Write for "the agent", never a named product. No "ask
  Claude", "in Grok", "Claude will…". Naming a runtime breaks portability and
  wastes tokens for the other.

## Output discipline

Conciseness governs the static body; this governs what a running skill **says
back** each turn — a per-run cost the body rules never touch. Every skill must
make its agent report tersely.

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
- **Label every Sources-of-truth entry** `(eager)` or `(on-demand: <when>)`,
  so a workflow step cannot silently preload a file meant for per-need reads.
- Structure is necessary, not sufficient — a one-hop, ToC'd, well-named
  reference can still bloat with restated content or be preloaded whole. Apply
  the Token-performance and Body-conciseness tests to it too.

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
- Don't hand-roll a plan as a deliverable. When a skill's output is a
  multi-step plan the user will keep and track, defer to the `plan-smith` skill
  (checkbox items + a Y/N/X status table) instead of inventing a format.
  Internal progress checklists the agent ticks off mid-run are exempt.

## Content hygiene

- **No time-sensitive info** ("after August 2025…"). Put superseded guidance in
  an "Old patterns" section instead.
- Concrete examples beat abstract description — show input/output pairs when
  output quality depends on format.
- Provide one default with an escape hatch, not a menu of options.
- **Wrap Markdown prose at ~80 columns.** Reflow every edited paragraph so no
  line exceeds 80; exempt code fences, table rows, and unbreakable tokens (URLs,
  paths, links). `dev/lint-skills.sh` warns on breakable over-width lines.
- **Align table columns** — pad cells so `|` delimiters line up in the source;
  re-pad the whole table when adding a row.
- **Plain, spaced lists.** Write list items as plain sentences — no bold-label
  lead-ins — and reserve `**bold**` for genuine emphasis in prose. Space items
  with a blank line when they are prose steps; keep them tight and unspaced
  when they are dense enumerations (type/flag/option lists, short spec fields,
  reference entries), where a value per line scans better and token economy
  wins. Applies to `SKILL.md` bodies, READMEs, and references alike.
- **US English.** Write skill files and any content a skill authors in US
  English spelling and conventions ("color", "canceled", "-ize"). When a skill
  edits a target that consistently uses another variety, match it and flag
  mixed usage rather than convert wholesale.

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
- Test across the models the skill targets — guidance that suits a strong model
  can under-serve a smaller one.
- To measure a skill empirically (baseline A/B, trigger test), use the Measure
  step — `references/evals.md`.
