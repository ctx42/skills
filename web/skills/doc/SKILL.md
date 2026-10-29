---
name: doc
description: >
  Fixes and completes in-source documentation of a Vue 3 + TypeScript
  frontend — module TSDoc, symbol TSDoc, component header blocks, and inline
  comments — one documentable item at a time. Use to document, fix stale or
  inaccurate comments, or fill missing TSDoc across a function, a component, a
  line, a file, a directory, or the whole frontend.
license: MIT
argument-hint: "[func=NAME | component=NAME | FILE:LINE | FILE | DIR | all]
  [max=N] [dirs=a,b] [only=tsdoc|exported]"
---

# doc

## Usage

```
/web:doc                            the working diff (default), plan-first if several items
/web:doc func=formatDate            one function's TSDoc + body comments; no plan
/web:doc component=AppLayout        one component's header block + script comments; no plan
/web:doc src/api.ts:42              the item enclosing that line; no plan
/web:doc src/api.ts                 every item in the file, plan-first
/web:doc src/stores                 every item in the directory, plan-first
/web:doc all                        every directory, plan-first; fans out when large
/web:doc src max=8                  cap comments changed this run; reports the rest
/web:doc all dirs=pages,stores      restrict to these directories
/web:doc src only=tsdoc             skip inline comments
/web:doc src only=exported          module headers, component headers, exports only
```

Executing skill: it reads code, edits TSDoc and comments in `.ts` and `.vue`
files, and verifies. Unlike `web:review` it acts on the code. Scope stops at
in-source comments: never write a README or a docs page to carry what a
comment should say.

**Governing rule — a comment changes only when it fails the checklist.** Judge
every documentable item against the checklist below and apply the minimal edit
that clears the checklist items that fire. A comment that passes is left alone,
however short. The documentable item — never the file — is the unit of work.

Sources of truth:
- `../style/references/production.md` (on-demand: before the first comment is
  written — its "SFC structure", "Stores and reads", "Naming", and "TSDoc and
  comments" sections) — obey it in every comment written; it is the rule spec,
  do not restate it.
- The project's own comment voice, from the neighbouring modules (on-demand:
  when writing).

## Target

Read the tokens in any order: a reserved word is a mode or flag, `key=value` is
a control, and anything else is the target. `func=` and `component=` name the
target, not a control. Resolve the frontend root as
`../style/references/checking.md` does, then one of six kinds; each fixes an
order, always worked one item at a time:

- diff (default, no target) — every item whose code or comment the working
  diff changes (`git diff HEAD`; on a branch with no commits, staged then
  unstaged); files alphabetically, items top to bottom. Plan-first when it
  holds more than one item, else run straight. An empty diff: say so and ask
  for a target.
- unit — `func=<name>`: an exported function, composable, or store, with its
  TSDoc, its members' TSDoc, and its body's comments; `component=<Name>`: the
  component's header block and its script's TSDoc and comments. Run straight.
- line — `path:42`: the innermost item containing the line (a body's inline
  comments, or the TSDoc the line sits in). Run straight.
- file — every item in the file, top to bottom. Plan-first.
- directory — files alphabetically; items top to bottom. Plan-first.
- all — every directory under `src/`, plus `e2e/`, alphabetically,
  sequentially unless it fans out. Plan-first.

A documentable item is one of: a production module's header block; a
component's header block; one function's, type's, const's, or store member's
TSDoc; an interface's field docs; or the inline comments inside one function
body or one template. Test and spec files have no module header but their
helpers and their steps' comments are items. State the resolved kind and the
item set before reading.

## Controls

A `key=value` that names no control here, or a word left over once the modes,
the target, and any text the skill takes are read: say it was not recognized,
name the ones that exist, and run with the defaults as if it were absent —
unless dropping it would widen what the run changes; then ask. A target that
resolves to nothing: say so and ask — never guess what to work on.

- `max=N` — hard cap on comments changed; report what is left.
- `dirs=a,b` — restrict `all` to these directories.
- `only=tsdoc` — skip inline comments in bodies and templates.
- `only=exported` — module headers, component headers, and exported symbols
  only.

Fan-out is automatic: a target spanning several directories with more than ~40
files or ~3000 lines of `.vue`/`.ts` in scope (the threshold `web:style` and
`web:review` use) runs one subagent per directory, each given this file's path
and `../style/references/production.md`'s; a smaller target runs sequentially.
Merging is not accepting: re-read every added or changed comment against
checklist item 4 and the code before it enters the report, and revert a fact the
code does not carry.

## The checklist

Each item is a yes/no read against the code.

1. missing — a production module, a component, a function, type, const, or
   store member has no TSDoc where the style rules require one. Add it.
2. wrong lead — the summary starts with the symbol's own name, a function's
   does not start with a third-person verb, or a boolean's not with
   "Whether". Fix the lead only.
3. inaccurate — the comment contradicts the code: a stale name, a renamed or
   removed parameter, prop, event, slot, or model, a changed return, an order
   or default the code no longer has. Correct it to match the code.
4. missing fact — a fact the types cannot express is absent and non-obvious:
   what an empty or null value means, when a value is loaded or shared, the
   error or failure conditions, units or format, a side effect (a request, a
   storage write, a focus move, a navigation). Add only that fact.

   It fires on a fact the code *establishes*, never on a category the code
   leaves open: ask what the body proves, not which kind of fact has no
   sentence yet. An absent guarantee is a silence to leave alone or a
   question to flag under Accuracy.
5. incomplete header — a component's header block does not name, in
   backticks, every prop, event, slot, and model the component declares. Add
   what is missing to the block.
6. member TSDoc — a single member of a `defineProps`, `defineEmits`, or
   `defineSlots` type carries TSDoc. Move any fact it holds that the header
   block lacks into the block, then delete it.
7. bad form — not full sentences; a parameter named without backticks; a
   `@param` or `@returns` tag; a symbol cross-reference not as `{@link X}`;
   an interface field documented by a trailing `//`. Fix per style.
8. restates code — an inline comment narrates what the next line plainly
   does instead of why. Tighten to the why, or delete it.

## Accuracy

Never write a fact you cannot confirm from the code; flag it instead. Read
the signature, the body, and for a component its macros, template, and the
components it renders. Confirm anything beyond the visible code with the
`LSP` tool (`hover`, `goToDefinition`, `findReferences`) or grep: a "loaded
once" or "shared" claim needs every caller; a `{@link X}` must resolve to a
real symbol, else it becomes plain backticked text. No language server: read
the code and say the confidence is reduced.

## Per-item loop

For each item, in strict order; never start item B until item A is written.

1. Read the code the item documents; establish ground truth (Accuracy).
2. Run the checklist; none fires — leave the comment untouched.
3. Confirm each fact you will write; demote the unverifiable to a flag.
4. Write the minimal edit that clears the fired items — add only the missing
   fact, fix only the wrong clause; never rewrite a comment that needed a
   clause. Obey `../style/references/production.md`, `max`, and the `only=`
   filter.

## Never touch

Never edit these; name them in the report when in scope:
- directive comments — `// biome-ignore …`, `// @ts-expect-error`,
  `// @ts-ignore`, `/// <reference …>`, `/* @vite-ignore */`,
  `// @vitest-environment …` — they are code;
- generated files;
- a comment whose intent the code cannot confirm — flag it.

## Plan (diff / file / directory / all)

Before writing, present: whether the run fans out and why (the file and line
count against the threshold); per item, which checklist items fire
(`file:Symbol — item`, an item nothing fires on not listed); items to flag
unverifiable; and never-touch items in scope. Wait for approval, then run the
loop and Verify.

## Verify

End of run, from the frontend root: `bunx biome check <edited files>` and
`bunx vue-tsc --noEmit` must pass, and every edited comment line must fit
Biome's `lineWidth` (default 80), measured by script — Biome does not wrap
comments. A run that edited nothing has nothing to verify: say so.

## Output

- The Verify result, one line: the files checked and that Biome, `vue-tsc`,
  and the width measure passed.
- Changes made, one line each, exactly: `file:Symbol — <checklist item #>:
  <what changed>`.
- Flagged unverifiable: `file:Symbol — the fact left unwritten and why`.
- Never-touched in scope: `file:Symbol — reason`.
- `all`: which directories were done and which skipped.
- Items left alone get no line; a flagged or never-touched item is never
  dropped silently. Close with a one-line pointer to run `web:review` on the
  result.

Report tersely: no preamble or narration; state each fact once.

## Self-learning

Obey this skill's lessons: every run, read with the file-read tool (never a
shell), in parallel, the sibling `${CLAUDE_SKILL_DIR}/LESSONS.md` and the
fallback `~/.agent-data/ctx42-skills/lessons/web/doc.md` (pass `~` as is, the
file tools expand it; no environment probe; `$AGENT_DATA_DIR` replaces
`~/.agent-data` only when you are told it is set). The sibling wins a conflict;
the fallback, which a read-only install writes, still counts once the checkout
is writable. A missing file needs no comment. On a correction or self-caught
mistake, append a one-line rule — general, naming nothing from the project at
hand (its files, tests, tickets) — to the sibling when this directory is
writable, else to the fallback, creating it, and report where.
