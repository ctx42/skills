# Native eval cases

The fast tier: `claude plugin eval` cases a change selects and runs in minutes
(`dev/eval-changed.sh`). Each case runs the real skill in a fresh `claude -p`
session with only its plugin loaded. `evals/evals.json` and
`evals/expectations.json` stay the scenario spec; a case is that scenario made
executable.

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
  in English." — the runner otherwise inherits an org language rule and
  answers in German, breaking text graders.
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
  a gate case, `<skill>--<scenario>--gate`, with no `append_system_prompt`:
  the run ends where the skill waits, and its graders assert that turn
  (`tool_used` Write/Edit `max: 0`, `arm: both`; the proposal in
  `last_message`). The full case keeps the after-approval bullets.
- A decision deep in a conversation that needs the real earlier turns:
  `context.history_file: history.jsonl`, a session recorded from a prior run
  (`--keep-temp`, then `config/projects/*/<id>.jsonl`); the prompt is the
  user's next reply and the scaffold rebuilds the files those turns left.
  Use it only where a gate case cannot express the bullet.

## Fixture

`case.yaml`: `schema_version: "1.1"`, `name: <dir>`,
`context.scaffold_script: scaffold.sh`. The script runs in the empty run
workspace and builds exactly what `setup` describes, inline (heredocs); it
reads nothing from the repo. Where the setup says something is correct, make
it correct; where it says something is absent, make it absent. An srd case
writes `project-config.md` (content of `srd/evals/fixtures/project-config.md`)
unless the setup changes it.

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
`project-config.md` `mcp-server` at a name with no mock.

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
| judgment                      | `llm`, one atomic claim, `focus: last_message` or `trace`      |

Patterns are JavaScript regexes: put flags in `flags:` (`m`, `i`, `s`),
never inline `(?m)`, which throws. A read-only check (`tool_used` Write/Edit
`max: 0`) only bites when Write/Edit are in `allowed_tools`. `file_exists`
sees only files the run created, never scaffold-made ones: check those by
content regex. An `llm` grader states one concrete, checkable claim; split a
compound bullet into several graders, and never judge counts or the trace
(the judge sees only its ends). Prefer `not_contains` on a planted marker
over an `llm` "did not" claim.

## Calibrate

Run `./dev/eval-changed.sh --case <group> '<skill>--*' -j 1`. A failure is a
case defect (fix the case) or a skill defect (record it; a conversion never
edits a skill).
