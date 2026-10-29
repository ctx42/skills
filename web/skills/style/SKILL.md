---
name: style
description: >
  Enforced Vue 3 + TypeScript coding style for the frontend (production and
  test code): the rulebook to read before writing or editing any .vue or .ts
  file, and a runnable style-only pass that lists style offenses, and drift
  from the reference Biome config, across a diff, a directory, a file, or the
  whole frontend, and proposes fixes to apply. Use before touching frontend
  code, or to check or fix its style; adding or changing a rule belongs to
  web:review.
license: MIT
argument-hint: "[TARGET] [dirs=a,b] [max=N] [depth=light|standard*|full]
  [plan_first] [fix]"
---

# style

## Usage

```
/web:style                                style-check the current git diff (default)
/web:style src/pages                      style-check one directory
/web:style src/pages/DevicesPage.vue      style-check one file
/web:style src/pages/DevicesPage.vue:42   the unit enclosing that line
/web:style component=DeviceTable          one component; func=<name> for one function
/web:style all                            check the whole frontend
/web:style src/pages fix                  apply every offense's fix without asking
/web:style all plan_first                 propose the budget, then stop
/web:style all dirs=pages,stores          restrict a whole-frontend check to these directories
/web:style all max=15 depth=light         cap offenses; set depth
```

Authoritative frontend style rules and the style-only pass that enforces
them, for one fixed stack: Vue 3 SFCs with `<script setup lang="ts">`,
TypeScript strict, Pinia, vue-router, PrimeVue 4, Bun, Vite, Biome,
`vue-tsc`, Vitest with happy-dom and `@vue/test-utils`, Playwright. The rules
live in two files:

- [references/production.md](references/production.md) — the Production
  rules: tooling, SFCs, reactivity, stores, router, API client, types, naming,
  comments, PrimeVue, CSS, and templates.
- [references/test.md](references/test.md) — the Test rules: unit, component,
  store, and end-to-end tests.

Two uses:

- Reference — when loaded as context before writing frontend code (the
  default): apply Production to `*.vue` and `*.ts`, and Test to `*.test.ts`
  and `e2e/*.spec.ts`; Test inherits Production unless a Test rule overrides
  it. Before editing a production file, read `references/production.md`;
  before editing a test, an e2e spec, or test support (`src/testing.ts`,
  benchmarks), read `references/test.md` and `references/production.md`
  both. Read each file once per session, the first
  time an edit needs it; a one-line edit needs it too.
- Run a pass — when invoked as `/web:style [target]`: check finished code
  against these rules and propose fixes. Read
  [references/checking.md](references/checking.md) and follow it.

Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. `func=` and `component=` name the
target, not a control. A `key=value` that names no control here, or a word left
over once the modes, the target, and any text the skill takes are read: say it
was not recognized, name the ones that exist, and run with the defaults as if it
were absent — unless dropping it would widen what the run changes; then ask. A
target that resolves to nothing: say so and ask — never guess what to work on.

Mechanical rules live in [references/biome.json](references/biome.json), the
reference Biome config; the two rule files hold the rules a tool cannot
check. Change any of them only through `web:review` (state a preference, or
`web:review learn` to mine an editing session); never hand-edit them.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see — when citing a rule, name it and the fix, not
its full text.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/style.md` (pass `~` as is,
the file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
