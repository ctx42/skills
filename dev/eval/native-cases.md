# Native eval cases

The audit tier: `claude plugin eval` cases a change selects
(`dev/eval-changed.sh --audit`), run only when the user asks — the routine
check is `dev/eval-check.py` and `dev/eval-probe.py` (CONTRIBUTING.md,
*Tiers*). Each case runs the real skill in a fresh `claude -p` session with
only its plugin loaded. `evals/evals.json` and
`evals/expectations.json` stay the scenario spec; a case is that scenario made
executable.

A skill with a generator in `dev/eval/gen/<skill>/` owns its cases there:
edit the generator, run it from its own directory (`python3 gen.py`; it
rewrites only its `<skill>--*` dirs), commit both. Hand-edit a case only when
its skill has no generator (srd: create, review, kb, system-check). A rerun
must reproduce the committed cases byte for byte; seed anything random.

## Layout

```
<group>/evals/
├── mocks/<server>/<tool>.md       suite-wide MCP stand-ins (srd: srd-doc)
└── <skill>--<scenario-name>/
    ├── prompt.md                  frontmatter + the user's query
    ├── case.yaml                  only when a scaffold is needed
    ├── scaffold.sh                builds the fixture in the run's workspace
    ├── mocks/<server>/<tool>.md   per-case overrides of suite mocks
    └── graders/b<N>-<slug>.md     one grader per expectations bullet
```

## prompt.md

```markdown
---
tags: [case:<dir>, skill:<s>, sec:<s>:<section>, ref:<s>/<ref>]
runs: 1
max_turns: 30
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
append_system_prompt: |
  <scripted answers, interactive skills only>
---

/srd:edit specs/login.md
```

- `case:<dir>` always; `skill:<s>` for every skill the scenario's `skills`
  array names; the `sec:`/`ref:` tags of every section and reference the case
  exercises (`dev/eval-changed.sh --list-tags <group>/<skill>`). An srd case
  also tags the shared references it passes through, at least
  `ref:create/project-config`.
- Body: the scenario's `query`, plugin-namespaced (`/edit x` → `/srd:edit x`).
- `append_system_prompt` always opens with "The user writes English; reply
  in English." — gates included — the runner otherwise inherits an org
  language rule and answers in German, breaking text graders.
- Limits: `max_turns` <= 80, `timeout_seconds` <= 300; a fan-out case tags
  `fan-out`, any other case that needs more (a multi-chunk fix job) `long`,
  and may take 600. The only free tags are `needs-shell`, `fan-out` and
  `long`; never tag a skill of another plugin (no change there reaches
  this group).
- `allowed_tools`: the minimum. Mocked MCP tools are allowed automatically.
  A case needing a shell adds `Bash(<cmd>:*)` and the tag `needs-shell`.
- Interactive skills: `append_system_prompt` carries the persona's replies
  for the bullets graded after them —
  "Automated eval: the user is absent. Whenever the skill would stop and wait
  for the user, take the next scripted answer below as the reply and continue
  in this same run; never end the run to wait. If none fits, give the most
  plausible answer and continue." then the numbered answers. This wires the
  run; it never changes the skill.
- Gates: a bullet about what happens *before* the user answers (proposes
  before writing, asks before acting, stops at a confirmation) never rides on
  scripted answers — self-answering erases the pause it checks. Split it into
  a gate case, `<skill>--<scenario>--gate`, with no scripted answers (the
  English line stays): the run ends where the skill waits, and its graders
  assert that turn (`tool_used` Write/Edit `max: 0`, `arm: both`; the
  proposal in `last_message`). The full case keeps the after-approval
  bullets. An audit-only or never-pausing skill needs no gate.
- A pause after earlier pauses: a stop case, `<skill>--<scenario>--stop`,
  scripts the answers up to it and adds "These are the only scripted answers.
  Once they are used up, end the run at the next point where the skill waits
  for the user." Its `last_message` is that pause. Other suffixes
  (`--gate-signal`) are fine.
- Scripted runs answer silently: the model takes a scripted answer without
  writing its question out, so never grade a proposal or question via `trace`
  text in a full case — use a gate, a stop case, files, or `tool_order`. Never
  add meta-instructions about "visible" output: they trigger
  `reasoning_extraction`.
- Two-invocation scenarios ("/cm micro, then /cm full") run as one prompt with
  both commands.
- A decision deep in a conversation that needs the real earlier turns:
  `context.history_file: history.jsonl`, a session recorded from a prior run
  (`--keep-temp`, then `config/projects/*/<id>.jsonl`); the prompt is the
  user's next reply and the scaffold rebuilds the files those turns left.
  Use it only where a gate or stop case cannot express the bullet. A
  hand-built JSONL works: `type`, `message`, `uuid`, a `parentUuid` chain; a
  `<command-name>` + `isMeta` base-dir line records a skill invocation; the
  prompt is `/<plugin>:<skill> <the user's reply>` so the skill loads fresh.
  Seed its UUIDs.

## Fixture

`case.yaml`: `schema_version: "1.1"`, `name: <dir>`,
`context.scaffold_script: scaffold.sh`. The script runs in the empty run
workspace and builds exactly what `setup` describes, inline (heredocs); it
reads nothing from the repo. Where the setup says something is correct, make
it correct; where it says something is absent, make it absent. Runs have
no network and a fresh `$HOME`: a Go fixture with dependencies writes its
`go.sum` and ends with `go mod download`, which fills the run's module cache
from this machine's (served as `GOPROXY` by `eval-changed.sh`, whose preflight
names any module missing locally). A fictional module: the scaffold builds it
into a throwaway file proxy and `go get`s it (reshape's `oskit`). A fixture
must build and its tests pass unless the setup says otherwise — runs have a
shell and check. Build a broken state *drifted*, not as a different
consistent style. The run's workspace is `<tmp>/home/cwd` and `$HOME` is
`<tmp>/home`: never name a scaffold dir `home/`. The plugin dir is read-only
in runs: a skill that edits its own files needs a workspace checkout plus a
wiring paragraph, and `$HOME/.agent-data` redirected the same way. An srd
case writes `project-config.md` (content of
`srd/evals/fixtures/project-config.md`) unless the setup changes it.

## Server facts

Never the real server. Suite mocks in `srd/evals/mocks/srd-doc/` answer by
default: `get_doc` serves the frozen standard, `search` no hits, `list_gaps`
no gaps, `glossary_terms` a small glossary, write tools a canned success. A
setup that states server facts (hits, drafts, glossary terms, a failing
tool) overrides that one tool in `<case>/mocks/srd-doc/<tool>.md`: a bare body
is the canned result (`{{input.<field>}}` echoes an argument), `error: true`
makes it fail, `type: agent` plus a prose world serves call-dependent answers.
Leave a tool unmocked to make it absent. The suite's fixed `report_gap`
always answers `gap-0901` and `list_gaps` stays empty: a case that captures
two or more gaps, or reads back what it wrote, overrides each gap tool with
its own `<case>/mocks/srd-doc/<tool>.md` carrying the same `type: agent` prose
world (fresh ids, lists what was reported); a case `_server.md` does not
override suite per-tool files. A server the case must lack: point the case's
`project-config.md` `mcp-server` at a name with no mock. Every tool a setup
fact touches (`search`, `get_doc`, `glossary_terms`) tells the same story: the
suite `get_doc` answers every id with the standard, so a case whose `search`
names a doc overrides `get_doc` too. A case mock can't reach suite files, so a
fixture it needs is a copy; lint fails when a copy drifts from the suite file.

## Graders

One per bullet, `b<N>-<slug>.md`, deterministic wherever the bullet allows:

| Bullet checks                 | Grader                                                         |
|-------------------------------|----------------------------------------------------------------|
| what the reply says           | `regex`, `target: last_message`                                |
| an earlier turn or a tool use | `regex`, `target: trace`; `tool_used` with `input_match`       |
| order of calls                | `tool_order` with `before` / `after`                           |
| a call that must not happen   | `tool_used`, `min: 0`, `max: 0`, `arm: both`                   |
| server writes and arguments   | `regex`, `target: mock_calls`                                  |
| a file created / not created  | `file_exists`, `exists: true` / `false`                        |
| a file's content or unchanged | `regex`, `target: {source: file, path: <p>}`                   |
| judgment                      | `llm`, one atomic claim, `focus: last_message`                 |

Patterns are JavaScript regexes: put flags in `flags:` (`m`, `i`, `s`),
never inline `(?m)`, which throws; `\A` and `\Z` match a literal letter, so
anchor with `^` and `$` without `m`. A read-only check (`tool_used` Write/Edit
`max: 0`) only bites when Write/Edit are in `allowed_tools`. `file_exists`
sees only files the run created, never scaffold-made ones: check those by
content regex. An `llm` grader states one concrete, checkable claim; split a
compound bullet into several graders, and never judge counts or the trace
(the judge sees only its ends). Prefer `not_contains` on a planted marker
over an `llm` "did not" claim.

Haiku judges fail correct runs on universal, negative, "once", count, and
provenance claims: try a regex first, and tell any judge to ignore the
trailing org notice. Recipes:

- stated once → `match: "count:1"`; a count that must equal the file's →
  an enumerated alternation (`dev/eval/gen/system-check/gen_terse_b4.py`,
  `dev/eval/gen/review/gen_tally.py`); an aligned table → a generated width
  alternation (plan-smith `ALIGNED`); nothing else changed → an anchored
  exact-content regex (style `js_exact()`). Counting graders exclude line
  numbers.
- "before any edit" → the tempered trace regex
  `^(?:(?!"name":"(?:Edit|Write)")[\s\S])*?…`; `tool_order` compares first
  occurrences, one tool per side.
- a payload in the reply's first fenced block →
  ``^(?:(?!```)[\s\S])*```[a-z]*\n(?:(?!```)[^\n]*\n)*?<what>`` (no `m`).
- `mock_calls` lines are `{"tool":"mcp__srd-doc__<t>","input":{…},"output":"…"}`
  with JSON-escaped output; key-free lookaheads are safest.
- one finding of a numbered report, in either order of its parts → lookaheads
  bounded by the next item: `(?=(?:(?!\n[ \t]*\**\d+\.)[\s\S])*?<part>)`.

Pitfalls, each seen failing a correct run:

- Runs have Bash, granted to every case: a file read is Read *or* `cat`/`sed`,
  and a file write may come from `cp` or a heredoc. Grade reads with
  `"name":"(?:Read|Bash)","input":\{"(?:file_path|command)":"…<path>`, and
  writes by the file's content, not by `tool_used` Write.
- Trace and tool input are JSON: a command on a later script line reads
  `\ngit`, where `\b` finds no boundary — write `(?:\b|\\n)git`; a command's
  `\"` stops `[^"]*` — use `(?:[^"\\]|\\.)*`; `\bn't` never matches
  "didn't".
- A gate's "asks" grader must not require `?`: replies end in a menu or
  "Reply go…".
- Match the shapes a correct reply takes: `**Q1:**` as well as `**Q1**`, a
  table cell between a key and its value, a brace list `{alpha,…,hotel}` for
  "all packages", a prior turn quoted in `last_message`.
- `{source: file}` takes an exact path; only `file_exists` globs.
- Account-level org instructions still reach runs: replies may end with a
  policy notice. Text graders exclude it (`Weisung`, `AI-Agents`), and judges
  are told to ignore it.
- A case loads only its own plugin: a delegate in another plugin (srd →
  `craft:grill-me`) cannot load, so grade the attempted `Skill` call, never
  what the delegate would do.
- Fan-out: brief and scratch files under `/tmp` are normal — restrict
  no-write graders to product paths and id checks to tool_use inputs, which
  include a rule list written by a Bash heredoc.

## Calibrate

`./dev/lint-skills.sh` first: it checks every case (scenario coverage, tags,
the English line, limits, JavaScript patterns). Then, when the user asks for an audit, run
`./dev/eval-changed.sh --case <group> '<skill>--*' -j 1` (repeat `--case` for
several globs). A failure prints its last message and keeps its trace in
`<results>/<group>/failed/<case>.trace.jsonl`, so diagnose from those before
re-running; `--keep` keeps every workspace, `--clean` deletes leftover ones,
and a run the account's usage limit cut off prints `LIMIT` — re-run it, never
triage it. Test a changed grader offline with `./dev/eval-regrade.py <trace>`
instead of paying for a re-run. Typical cost per run (Opus): $0.10–0.30 for a craft
case, $0.25–0.80 for a go or srd case, $3–9 for a fan-out case; a full group
is $15–45. An invocation has no cost ceiling unless `--max-usd N` sets one:
a ceiling cuts graders off mid-case and leaves cases unrun. Runs draw on the
user's own 5-hour usage window: keep `-j 2`, never run a whole skill or group
unasked, re-run only failing or cut-off cases, and calibrate on
`--model sonnet` before confirming on Opus.
A failure is a case defect (fix the case) or a skill defect (record it; a
conversion never edits a skill).
