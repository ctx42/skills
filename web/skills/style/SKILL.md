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
argument-hint: "[TARGET] [dirs=a,b] [max_issues=N]
  [depth=light|standard*|full] [plan_first] [fix]"
---

# style

## Usage

```
/web:style                                style-check the current git diff (default)
/web:style src/pages                      style-check one directory
/web:style src/pages/DevicesPage.vue      style-check one file
/web:style component=DeviceTable          one component; func=<name> for one function
/web:style all                            check the whole frontend
/web:style src/pages fix                  apply every offense's fix without asking
/web:style all plan_first                 propose the budget, then stop
/web:style all dirs=pages,stores          restrict a whole-frontend check to these directories
/web:style all max_issues=15 depth=light  cap offenses; set depth
```

Authoritative frontend style rules and the style-only pass that enforces
them, for one fixed stack: Vue 3 SFCs with `<script setup lang="ts">`,
TypeScript strict, Pinia, vue-router, PrimeVue 4, Bun, Vite, Biome,
`vue-tsc`, Vitest with happy-dom and `@vue/test-utils`, Playwright. Two uses:

- Reference — when loaded as context before writing frontend code (the
  default): apply Production to `*.vue` and `*.ts`, and Test to `*.test.ts`
  and `e2e/*.spec.ts`; Test inherits Production unless a Test rule overrides
  it.
- Run a pass — when invoked as `/web:style [target]`: check finished code
  against these rules and propose fixes. Read
  [references/checking.md](references/checking.md) and follow it.

Mechanical rules live in [references/biome.json](references/biome.json), the
reference Biome config; this file holds the rules a tool cannot check. Change
either only through `web:review` (state a preference, or `web:review learn`
to mine an editing session); never hand-edit them.

Report tersely: no preamble or narration; state each fact once; don't restate
output the user can already see — when citing a rule, name it and the fix, not
its full text.

## Production

### Tooling

- The project's `biome.json` turns on every rule the reference sets, at the
  reference's level and options, and its HTML formatter; it may add rules,
  never drop one.
- Comments fit Biome's `lineWidth` (default 80); the formatter never wraps
  them, so wrap by hand.

### SFC structure

- Blocks in order: `<script setup lang="ts">`, `<template>`, `<style scoped>`.
- In `<script setup>`: imports, the component TSDoc, macros, composables and
  stores, consts, state, computed, functions, watchers, lifecycle hooks.
- Document each component in one TSDoc block above its first macro (or its
  first statement when it has none), naming in backticks every prop, event,
  slot, and model; never TSDoc on single members of the `defineProps`,
  `defineEmits`, or `defineSlots` types. The script's own functions and
  consts are documented like any others (TSDoc and comments).
- Export the types a component's callers need from a plain
  `<script lang="ts">` block above `<script setup>`.
- Name a base widget `App*`, a routed view `*Page` in `pages/`, a page's tab
  views in `pages/<page>/` without the suffix.
- Make a component generic (`generic="T extends …"`) when its props carry the
  caller's rows or values.

### Props, emits, model, slots

- Bind `defineProps` to `props` only when the script reads it.
- Name a boolean prop so leaving it out means false (`plain`, `lazy`).
- Give optional props defaults with `withDefaults`, never by destructuring.
- Declare emits with named tuples (`zoom: [from: number, to: number]`); a
  payload of several fields is one typed event interface.
- Use `defineModel` for a two-way value, `required: true` when the parent must
  bind it.
- Type slots with `defineSlots`, and annotate scoped-slot parameters in the
  template (`#body="{ data }: { data: Row }"`).
- Name emits camelCase in script; templates use them kebab-case.

### Reactivity and lifecycle

- Hold template elements with `useTemplateRef<T>("name")`, typed by just the
  members used; never `ref<HTMLElement | null>(null)`.
- Keep non-reactive handles — library instances, observers, timers, in-flight
  promises, load counters — in a plain `let`, never a `ref`.
- Undo in `onBeforeUnmount` everything `onMounted` started: listeners,
  observers, timers, library instances.
- Watch a getter; derive a primitive key (`tabs.map(…).join()`) instead of
  `deep: true`.
- Give `flush: "post"` to a watcher that reads layout or drives a library
  bound to the DOM.
- Hide an element whose size code reads with `:hidden`, never `v-show`, which
  applies after watchers run.
- Drop a superseded async answer: guard every state write with a load counter
  or the key that was asked for.
- Share an in-flight load: cache its promise (`running ??= (async () => …)()`)
  and clear it in `finally`, so concurrent callers share one request and a
  failed load can be retried.
- Mark large static objects handed to a plugin with `markRaw`; hold large
  immutable data in `shallowRef`.
- Start a component's first read with `watch(src, load, { immediate: true })`
  when it depends on the route or props, else `onMounted(() => void load())`.

### Stores and reads

- Write setup stores only (`defineStore(id, () => …)`), named `useXxxStore` in
  `stores/xxx.ts`, returning every ref, computed, and action.
- Put a read in a store only when several views share it or it must outlive
  navigation; a page's own reads stay in the page.
- Hold an async read's state — its result, `busy`, and `error` (a sentence to
  show, `""` for none) — in the project's one shared read helper, never in
  hand-rolled refs per page.
- Document what every store member holds and what it holds when empty ("`""`
  until chosen", "null until known").
- Read store state through the store object (`project.namespace`);
  destructure only through `storeToRefs`.
- Keep a browser preference under an app-prefixed key, wrap its reads and
  writes in try/catch, and store nothing while it holds the default.
- Keep module-level mutable state to app-wide wiring set once; anything else
  goes in a store.

### Router

- Lazy-load every routed page through `() => import(…)` consts at the top of
  the router module.
- Name every route in kebab-case and navigate with `{ name, params, query }`,
  never a string path.
- Type route meta by augmenting `RouteMeta`, each field documented.
- Keep a list's state (filters, search, page) in the query string through
  `router.replace`, leaving out values at their default, so a link reproduces
  the view.
- Read params and query through `computed` and the project's one shared guard
  helper, never an inline `typeof` per page.
- Export a router factory taking `history`, defaulting to
  `createWebHistory()`.

### API client

- Send every request through the one client module; pages and stores never
  call `fetch`, and nothing names a parameter `fetch`.
- Fail with one `Error` subclass carrying `status` (0 = unreachable) and
  setting `this.name`; callers branch on `instanceof` and status.
- Check every response into the app's own types at the client boundary
  (`unknown` in, typed values out); never `as T` an unchecked body.
- Build queries with `URLSearchParams`; pass every interpolated path segment
  through `encodeURIComponent`.
- Map errors to user-facing full sentences in one helper per domain.
- Catch narrowly and rethrow the rest; a `catch` that swallows on purpose
  carries a comment saying why.
- Start independent reads together (`Promise.all`, or several `void` reads),
  never one after another.

### Types

- Model a closed set as a string-literal union plus an
  `isX(v: unknown): v is X` guard over a labelled options array.
- Parse stored or untrusted JSON as `unknown` and narrow it with guards; keep
  `as` for gaps in DOM or library types.
- Type a table event with its row type (`TableRowClickEvent<Row>`), never cast
  `event.data`.
- Give every magic number a module-level `const` whose TSDoc names its unit.
- Create expensive objects on first use (`x ??= new …`), not at module load.
- Take "now" as a parameter or prop defaulting to `new Date()`; never read the
  clock inside the logic.
- Use `| null` for a value not there yet; `undefined` only for an optional
  prop or field.

### Naming

- Name a boolean with a bare adjective or participle (`open`, `busy`),
  documented "Whether …"; the in-flight flag is `busy`, never `loading`, and no
  `is`/`has` prefix.
- Name template event handlers `onEvent` (`onRowClick`), action handlers with a
  verb (`submit`, `copy`).
- Spell words out (`response`, `device`, `value`); no shortened names such as
  `rsp`, `qry`, `prj`, `typ`, `dev`, `val`, `fn`. `err` in a `catch` and a
  single-letter parameter of a one-line arrow are fine.
- Keep modules flat in `src/`, camelCase by topic, exporting their composables
  (`useXxx`); `stores/`, `pages/`, `components/` are the only subdirectories.

### TSDoc and comments

- Open every production `.ts` module — not a test, spec, or config file —
  with a TSDoc block stating its purpose, above the imports.
- Give every function, type, const, and store member a `/** */` block: a
  function's summary starts with a third-person verb ("Returns …", "Returns
  whether …"), a value's or type's with a noun phrase, a boolean's with
  "Whether …"; never with the symbol's own name. A `const` holding what a
  composable or store returns (`const route = useRoute()`) needs none, and a
  run of like consts (the lazy route pages) may share one comment above it.
- Name parameters in backticks in the prose; no `@param` or `@returns`.
- Cross-reference symbols with `{@link X}`.
- Document an interface field with `/** */` above it, never a trailing `//`.
- Put the reason for non-obvious code in a comment above it: `//` in script,
  `<!-- -->` in templates, `/* */` with ` * ` leaders in CSS.
- A one-line `if` whose body fits on the line may go unbraced; anything longer
  is braced.

### PrimeVue

- Import each PrimeVue component where it is used (`primevue/button`); no
  global registration, no pass-through (`pt`), no PrimeIcons font.
- Customize the theme only through `definePreset` in the theme module; fix
  contrast and focus rings there, never per component.
- Reach for PrimeVue props (`severity`, `size`, `text`, `outlined`) before CSS;
  style PrimeVue internals only with `:deep(.p-…)` in a scoped rule with a
  comment saying why.
- Name every PrimeVue form control with `input-id` and `<label for>`, and give
  `Select` and `SelectButton` `aria-labelledby`, which they need besides.

### CSS

- Scope component styles; shared rules and utilities (`.sr-only`) live once in
  one global stylesheet `main.ts` imports.
- Color only with PrimeVue semantic tokens (`--p-text-muted-color`); a palette
  token needs a matching dark-mode override.
- Size in `rem`, breakpoints included; `px` only for hairlines, focus rings,
  and sizes a library needs in pixels.
- Bind script values into CSS with `v-bind()` in the scoped style, never an
  inline `:style` object, except positions that change per frame.
- Make every interactive target at least 24px, and show hover-only controls
  always under `@media (hover: none)`.

### Templates and accessibility

- Keep template expressions simple; a multi-line or multi-branch expression
  goes into a `computed`.
- Key a component only on what must reset it.
- Show a count, an empty message, or "none" only after a read finished
  without error.
- Announce changes with `role="status"`/`aria-live="polite"`; one
  `role="alert"` per error, never nested; give state shown only visually an
  `.sr-only` text.
- Keep heading levels in sequence under the page's single `<h1>`, which the
  layout renders.
- When a control removes itself, move focus to what replaces it.

## Test

### Shape and naming

- One flat `describe("<symbol or Component>")` per unit, `test` inside it;
  never a bare top-level `test` in a unit test file.
- Title a test with a short lowercase phrase of the behaviour (UI labels keep
  their case); no `error - ` prefix.
- Separate arrange, act, and assert with blank lines, no `--- Given ---`
  markers; act again after an assertion only to check a sequence.
- Write table tests as `test.each([[input, want], …])("%j gives %s", …)`, rows
  positional.
- Assign a returned act result to `have` and the expected value to `want`;
  assert DOM reads after a mount or trigger inline. A mounted component is
  `wrapper`.
- Raise a timeout per test only, with a comment saying why.

### Fixtures and fakes

- Fake the network at `fetch` with canned answers keyed `"METHOD /path"` that
  throw on any request not listed; never mock your own modules.
- Keep shared fakes in `src/testing.ts`: `testXxx` values, `xxxAnswers()`
  factories, `xxxPath` request keys, and `json`/`stalled`/`networkError`
  responses; each a documented function declaration, never an arrow const.
- Build each `Response` fresh from a factory, since a body reads once; fakes
  clone.
- Cover the loading (`stalled()`), empty, and error states of every read.
- Test concurrent and superseded loads with a held answer the test releases.
- Fake a browser API by stubbing the global with a shared fake
  (`vi.stubGlobal("localStorage", blockedStorage())`), never by spying on a
  prototype.
- Mock a third-party module only for what happy-dom lacks (canvas charts).

### Component, page, and store tests

- Test a page by mounting it at its URL through `mountAt` (real Pinia, memory
  router, PrimeVue) with the fetch fake; assert on the DOM and
  `router.currentRoute`.
- Drive your own components with DOM events (`trigger`, `setValue`); emit
  (`vm.$emit`) only on PrimeVue widgets happy-dom cannot operate.
- Test a composable through the shared probe helper in `src/testing.ts`.
- Give each store test a fresh `setActivePinia(createPinia())`.
- Leave layout CSS drives (sizes, visibility set in CSS) to Playwright;
  happy-dom loads no styles.
- Assert exact values (`toBe(true)`, `toEqual([...])`, `toHaveLength`), never
  `toBeTruthy`; assert whole lists of cell texts.
- Find elements by text, tag, or attribute (`[aria-label=…]`); a class only
  when none of these singles one out.

### Cleanup and config

- Reset test state centrally: `restoreMocks` and `unstubGlobals` in the
  Vitest config, `enableAutoUnmount(afterEach)` and `localStorage.clear()` in
  the setup file; never per test file.
- Hold coverage thresholds just below the measured totals; delete code no test
  can reach rather than lower them.

### End-to-end (Playwright)

- Write one top-level `test` per user flow, no `describe`, narrating its
  steps in `//` comments.
- Locate by role and accessible name; when none fits, a semantic `data-<noun>`
  attribute; never `data-testid` or a layout class.
- Put each page region behind a documented `(page) => Locator` helper.
- Run against the built server backed by a fake upstream; extend the fake per
  test with `page.route` falling back to it.
- Read credentials only from the environment, and `test.skip` with a reason
  when they are missing.

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
