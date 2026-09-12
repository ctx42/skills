# Skill Authoring Standards

The canonical ruleset `skill-smith` writes and audits against. Fuses Anthropic's
[skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
with this repo's house rules. Terse by design: every rule is one enforceable
line. Repo mechanics (catalog updates, naming, syncing, retiring) live in
[CONTRIBUTING.md](../../../CONTRIBUTING.md) — this doc references it, never
duplicates it.

## Contents

- Scope
- Frontmatter
- Claude-native frontmatter
- Description quality
- Token performance
- Body: conciseness
- Output discipline
- Progressive disclosure
- Degrees of freedom
- Workflows & feedback loops
- Instruction prominence
- Gotchas
- Content hygiene
- Scripts & bundled files
- Usage block
- Evaluations
- Observing real use

## Scope

One skill covers one coherent unit of work — size it like a function.

- Scoped too narrow, a single task drags in several skills, each paying
  metadata and each able to contradict the others.
- Scoped too broad, no description can trigger it precisely.
- Split a skill that needs two unrelated trigger sets; merge two that always
  fire together.

## Frontmatter

This repo's skills ship as Claude Code plugins and target **Claude Code only**.
Write for the Claude Code feature set; the native affordances below are
encouraged where they earn their place.

- Required: `name`, `description`.
- `name` — lowercase letters, digits, and hyphens only; ≤ 64 chars; no leading,
  trailing, or doubled hyphen; **must equal the parent directory name**. No
  reserved words (`anthropic`, `claude`), no org/vendor prefix, no vague names
  (`helper`, `utils`). Prefer a gerund (`writing-x`) or a short verb.
- `description` — see next section. ≤ 1024 chars.
- `compatibility` — one line, ≤ 500 chars, only when the skill has a real
  environment requirement (a host product, a system package, network access).
- Optional metadata: `license`, `version`, `tags`, `author`, `metadata`.
  Use sparingly.
- Claude-native affordances (allowed): `argument-hint` (surface a skill's
  arguments in the invocation UI), `$ARGUMENTS` / `$N` body substitution, and
  dynamic injection (`` !`cmd` ``). See "Claude-native frontmatter" below.
- Other Claude Code keys (`allowed-tools`, `disable-model-invocation`, `model`,
  `agent`, …) are permitted when a skill genuinely needs them; default to
  omitting them.
- `user_invocable` is not a Claude Code key, and is a common invention —
  invocation is gated by `disable-model-invocation`. Flag any invented key.
- No XML angle brackets anywhere in frontmatter. It is injected verbatim into
  the system prompt, so markup there is an instruction-injection surface, not a
  formatting choice. (A leading `>` opening a folded scalar is YAML, not a tag,
  and stays.)

## Claude-native frontmatter

Adopt these where they raise success rate or clarity; skip them when prose
already suffices.

- `argument-hint` — declare the argument shape so it shows in the invocation UI,
  e.g. `argument-hint: "[micro|mini*|full] [apply] [<hash>]"`. Add it to every
  skill that takes arguments; omit it for an arg-less skill. Suffix the default
  option in a mutually-exclusive group with `*` (`mini*`) — the one used when
  that choice is omitted; add it only when a listed option is genuinely the
  default. The hint is display-only, never parsed: the default is still defined
  in the body, and `*` only surfaces it.
- `$ARGUMENTS` / `$N` — read invocation arguments in the body directly instead
  of "detect from the user's prose": `$ARGUMENTS` for the whole string, `$1`/`$2`
  for positional tokens. Keep a prose fallback only for genuinely free-form input.
- Dynamic injection `` !`cmd` `` — fold command output into context at load time
  for a skill whose input is repo or tool state, e.g. `` !`git diff --cached` ``
  for a commit-message skill, so the body works from real data instead of telling
  the agent to fetch it. Keep injected commands read-only and cheap.

## Description quality

The description is how the agent decides to load the skill — its single
highest-leverage field.

- Third person: "Reviews X", not "I review X" or "You can review X".
- State **what it does AND when to use it** — include concrete trigger terms.
- No workflow leak: say *when to use it*, never how it works — no mode lists,
  control/flag names, file paths, or step summaries. An agent acts on a leaked
  summary and skips the body — the very steps the skill exists to enforce. Every
  clause serves discovery.
- Lean pushy on when: agents tend to under-trigger, so make the use-cases
  assertive ("Use when…") and cover oblique phrasings — while still never
  leaking *how* (above).
- Size: aim ≤ ~350 chars (hard limit 1024) — the description is paid in every
  session, for every skill, whether or not it fires.
- Specific, not vague. ✗ "Helps with documents" ✓ "Extracts text and tables
  from PDFs. Use when the user mentions PDFs, forms, or extraction."
- Put the key use case first (listing text is truncated downstream).
- Name the boundary when a near neighbor exists: *Do NOT use for X — use the
  `y` skill.* Adjacent tasks that share the vocabulary then stop false-firing.
- Tune from the symptom. Undertriggering (never loads, users invoke it by hand)
  — add nuance and the domain's technical keywords. Overtriggering (fires on
  unrelated work) — add the negative trigger above and narrow the scope clause.
- Include triggers **naturally** — write a real sentence, not a keyword-stuffed
  tag dump.
- YAML scalar safety: a plain scalar breaks on `: ` (colon-space) or a leading
  `>`/`<`. Use a folded block scalar (`description: >`) for multi-line or any
  description containing a colon — it is valid YAML and the repo default. Never
  "fix" a colon by deleting the block scalar.

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
- A bundled file costs nothing until it is read, so a long reference is fine
  when the workflow genuinely defers it. Cut the always-loaded surface hard;
  do not cut a deferred file just for being large.
- Judge by tokens-to-outcome, not line count — a padded 400-line body can cost
  more than a lean 500-line one.

## Body: conciseness

- Assume the model is already smart. Add only what it does not know. Cut any
  sentence that explains a common concept.
- One rule = one dense imperative line in the body or style list. Expand in a
  reference only when the line alone is not enough to enforce.
- Keyed / reference entries stay short: Why + Detect in ≤2 sentences; no
  multi-paragraph rationale. Prefer no example; a code fence only when the rule
  is ambiguous without one (fragile format, non-obvious shape). Drop the entry
  when the body line is enough.
- These tests apply to every loaded file, not just the body. A reference must
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
- Teach the method, not the answer. The skill must generalize to the next task,
  so write the procedure ("read the schema, join on the `_id` convention"), not
  one instance's result ("join orders to customers on customer_id").
- One consistent term per concept throughout (don't mix "field/box/element").
- Address the agent: write for "the agent"; you may name Claude Code features
  where a skill relies on them.
- Every `SKILL.md` ends with the `## Self-learning` block; `enhance-skills`
  owns its wording and `dev/lint-skills.sh` warns when it is missing.

## Output discipline

Conciseness governs the static body; this governs what a running skill **says
back** each turn — a per-run cost the body rules never touch. Every skill must
make its agent report tersely.

- Cut framing: no preamble ("I'll now review…"), no step narration ("Let me
  read the file"), no closing filler ("Hope this helps"). Open with the payload.
- State each fact once: don't restate output the user can already see. No
  closing summary that repeats findings, a diff, or an artifact just shown. A
  short pointer ("wrote `x.md`") is fine; re-listing its contents is not.
- Never cut the payload: terseness applies to framing and restating only. The
  substantive result — findings, diffs, the written artifact, a required
  status table — is always stated in full. A review still lists every finding.
- Every skill carries the rule in its body: a produced `SKILL.md` must
  contain an explicit output-discipline line so the rule bites at runtime, not
  only when skill-smith is authoring. Canonical wording: *Report tersely: no
  preamble or narration; state each fact once; don't restate output the user can
  already see.* Place it where the skill describes its output.

## Progressive disclosure

Three load levels: metadata (always) → `SKILL.md` body (on trigger) → bundled
files (on demand). Exploit it:

- `SKILL.md` is a table of contents that points to detail; move large reference
  material, schemas, and long examples into sibling files. Conventional layout:
  `scripts/` (executable code), `references/` (docs loaded on demand),
  `assets/` (templates, examples), `evals/` (eval data). Use these names; avoid
  deep nesting.
- References one level deep: every bundled file links directly from
  `SKILL.md`. Never chain `SKILL.md` → a.md → b.md — the agent may only preview
  nested files.
- Name bundled files for their content (`standards.md`, `rules.md`), not
  `doc2.md`. Use forward slashes always.
- Any reference file over ~100 lines starts with a Contents list.
- Split a multi-domain reference by domain (`references/finance.md`,
  `references/sales.md`) so a task loads only its own domain, never all of them.
- Point at the section, not the file, when a reference is large: tell the agent
  to grep it or read the named heading. "See `rules.md`" invites a whole-file
  read and quietly undoes the deferral.
- Label every Sources-of-truth entry `(eager)` or `(on-demand: <when>)`,
  so a workflow step cannot silently preload a file meant for per-need reads.
- Structure is necessary, not sufficient — a one-hop, ToC'd, well-named
  reference can still bloat with restated content or be preloaded whole. Apply
  the Token-performance and Body-conciseness tests to it too.

## Degrees of freedom

Match specificity to task fragility:

- High (prose steps) — many valid approaches, context decides. e.g. reviews.
- Medium (templates/pseudocode with parameters) — a preferred pattern, some
  variation ok.
- Low (exact commands, no improvisation) — fragile, must-be-consistent,
  ordered operations. e.g. migrations.

## Workflows & feedback loops

- Break multi-step tasks into clear numbered steps; for long ones, give a
  checklist the agent copies and ticks off.
- Route at decision points instead of describing every branch inline: name the
  condition, then send the agent to the one path that applies.
- Build in validate → fix → repeat loops for quality-critical output. The
  "validator" can be a script or a reference doc the agent checks against.
- For risky/batch work, emit a verifiable intermediate plan and validate it
  before executing.
- Don't hand-roll a plan as a deliverable. When a skill's output is a
  multi-step plan the user will keep and track, defer to the `plan-smith` skill
  (checkbox items + a Y/N/X status table) instead of inventing a format.
  Internal progress checklists the agent ticks off mid-run are exempt.

## Instruction prominence

A skill can load and still be ignored. When that happens the cause is placement
or phrasing, not the trigger:

- Put what must not be skipped at the top of its section, never buried mid-list
  behind setup detail. Ordering is what the agent reads as priority.
- Mark the few genuinely load-bearing steps (`## Important`, `CRITICAL:`) and
  spend that weight sparingly — mark everything and it marks nothing.
- Replace ambiguous directions with checkable ones. ✗ "validate properly"
  ✓ "verify the name is non-empty and the start date is not in the past".
- A skill the agent keeps disobeying is usually too verbose. Cut before you
  emphasize.

## Gotchas

A gotchas list is often a skill's highest-value content: the environment facts
that defy a reasonable assumption, which the agent gets wrong unless told.

- A gotcha is a concrete correction, never general advice. ✗ "handle errors
  properly" ✓ "`/health` returns 200 while the database is down — use `/ready`".
- Keep gotchas in the body, not a reference: the agent cannot know to load a
  file about a trap it does not know exists.
- Grow the list from real corrections — every mistake a user has to correct is
  a candidate line (this is what `## Self-learning` feeds).

## Content hygiene

- No time-sensitive info ("after August 2025…"). Put superseded guidance in
  an "Old patterns" section instead.
- Concrete examples beat abstract description — show input/output pairs when
  output quality depends on format.
- Give a template when the output has a required shape; agents match a concrete
  structure better than a described one. Say which kind it is: an exact
  template ("use this structure") or a starting point ("adapt as the task
  needs") — an unmarked template gets followed too rigidly or ignored.
- Provide one default with an escape hatch, not a menu of options.
- Wrap Markdown prose at ~80 columns: reflow every edited paragraph so no
  line exceeds 80; exempt code fences, table rows, and unbreakable tokens (URLs,
  paths, links). `dev/lint-skills.sh` warns on breakable over-width lines.
- Align table columns — pad cells so `|` delimiters line up in the source;
  re-pad the whole table when adding a row.
- Plain, spaced lists: write list items as plain sentences — no bold-label
  lead-ins — and reserve `**bold**` for genuine emphasis in prose. Space items
  with a blank line when they are prose steps; keep them tight and unspaced
  when they are dense enumerations (type/flag/option lists, short spec fields,
  reference entries), where a value per line scans better and token economy
  wins. Applies to `SKILL.md` bodies and bundled references alike.
- US English: write skill files and any content a skill authors in US
  English spelling and conventions ("color", "canceled", "-ize"). When a skill
  edits a target that consistently uses another variety, match it and flag
  mixed usage rather than convert wholesale.

## Scripts & bundled files

Scripts are allowed. Reach for one when a check must hold every time: code is
deterministic, language interpretation is not, so a validation the skill cannot
afford to have skipped belongs in a script rather than in prose. When you
include them:

- Solve, don't punt — handle errors in the script rather than failing to the
  agent.
- No voodoo constants — justify every magic value in a comment.
- Make intent explicit: "Run `x.py`…" (execute) vs "See `x.py` for the
  algorithm" (read as reference).
- Don't assume packages are installed — state dependencies.
- Name MCP tools fully qualified (`ServerName:tool_name`); a bare tool name can
  fail to resolve when several servers are connected.
- Never block on input: agents run non-interactive shells. Take every input as
  a flag, env var, or stdin, and exit with a usage line instead of prompting.
- Document the interface in `--help` — flags, defaults, one example — since
  that output is how the agent learns to call the script.
- Data to stdout (JSON/CSV, not aligned columns), diagnostics to stderr, a
  distinct exit code per failure kind.
- Make errors actionable: what was wrong, what was expected, what to try.
- Stay idempotent and cap output size — agents retry, and harnesses truncate.

## Usage block

- Skills ship no `README.md`. Everything a user or agent needs is in `SKILL.md`,
  its bundled files, and `evals/evals.json`. Project-level READMEs are
  `readme-smith`'s job, not a skill's.
- Usage section, near the top: every `SKILL.md` MUST carry a `## Usage` section
  immediately after the H1 title, before any other `##` section. It holds a
  single fenced code block showcasing invocation examples — one line per mode:
  the invocation with representative arguments, then a terse description. The
  no-argument / default invocation comes first, marked `(default)`. Align the
  description column with padding so the block reads as a table. Model it on
  `srd/skills/review`:

  ```
  /review path/to/srd.md             review (default): resolve fixed + append new
  /review path/to/srd.md walk        interactive, section by section
  /review path/to/srd.md check       re-verify open findings vs the current SRD
  /review path/to/srd.md check #4,6  re-verify only findings #4 and #6
  /review path/to/srd.md errata      re-sort existing findings into ## Errata
  /review path/to/srd.md feedback    terse plain-text list of open tasks
  ```

## Evaluations

Mandatory and written before finalizing (eval-driven development):

- Evals are data, not prose: every skill carries `evals/evals.json` with **at
  least 3 scenarios** in the shape Anthropic's tooling uses — `{id, name,
  skills, query, files, expected_behavior[]}`, plus `setup` when the scenario
  needs a fixture. Measure mode then runs the file instead of re-deriving a
  rubric from prose.
- Each scenario: a representative query + the expected behavior (2–4 checks).
- Each check must be gradeable from the output alone: "names the rule it
  breaks", not "handles it well". Drop a check the skill-less baseline also
  passes — it measures the model, not the skill.
- At least one scenario asserts terse output per the output-discipline rule:
  no preamble or narration, payload stated once, no closing summary that repeats
  shown content.
- Build evals from real gaps: run the task without the skill, note what failed,
  encode that as a scenario.
- Start with one hard task, not broad coverage. Push a single challenging case
  until it succeeds unaided, extract what you had to supply, and only then add
  scenarios — the single case gives faster signal than a wide first sweep.
- Develop iteratively — author the skill, run it on the scenarios, observe where
  it struggles, refine. Strengthen the description first when it fails to
  trigger.
- Test across the models the skill targets, asking each its own question: does
  a smaller model get enough guidance, and does a stronger one get over-
  explained? Guidance tuned to one end under-serves the other.
- Test in a fresh context, never in the session that wrote the skill. The
  authoring conversation already holds the intent, the corrections, and the
  reasoning the skill is supposed to supply on its own, so a dry-run there
  passes on context the real user will not have. Author in one session, test in
  another (a subagent counts).
- To measure a skill empirically (baseline A/B, trigger test), use
  `skill-smith`'s Measure mode (`references/measuring.md`).

## Observing real use

Watch how the agent moves through the skill, not just whether it got the answer.
Four signals, each with its own fix:

- It reads files in an order you did not expect — the structure is not as
  obvious as it looked; re-order or re-signpost.
- It skips a reference it needed — the pointer is too weak or too buried; make
  the link explicit and say when to follow it.
- It reads the same reference on every run — that content belongs in the body.
- It never opens a bundled file — the file is dead weight or badly signposted.
  Delete it or point at it properly.
