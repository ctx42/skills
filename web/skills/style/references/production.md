# Web style — Production

Rules for every `*.vue` and `*.ts` file, tests included: Test inherits these
unless a rule in `test.md` overrides one. Mechanical rules live in the
reference Biome config, `biome.json` (this directory); these are the rules a
tool cannot check.

## Contents

- Tooling
- SFC structure
- Props, emits, model, slots
- Reactivity and lifecycle
- Stores and reads
- Router
- API client
- Types
- Naming
- TSDoc and comments
- PrimeVue
- CSS
- Templates and accessibility

## Tooling

- The project's `biome.json` turns on every rule the reference sets, at the
  reference's level and options, and its HTML formatter; it may add rules,
  never drop one.
- Comments fit Biome's `lineWidth` (default 80); the formatter never wraps
  them, so wrap by hand.

## SFC structure

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

## Props, emits, model, slots

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

## Reactivity and lifecycle

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

## Stores and reads

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

## Router

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

## API client

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

## Types

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

## Naming

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

## TSDoc and comments

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

## PrimeVue

- Import each PrimeVue component where it is used (`primevue/button`); no
  global registration, no pass-through (`pt`), no PrimeIcons font.
- Customize the theme only through `definePreset` in the theme module; fix
  contrast and focus rings there, never per component.
- Reach for PrimeVue props (`severity`, `size`, `text`, `outlined`) before CSS;
  style PrimeVue internals only with `:deep(.p-…)` in a scoped rule with a
  comment saying why.
- Name every PrimeVue form control with `input-id` and `<label for>`, and give
  `Select` and `SelectButton` `aria-labelledby`, which they need besides.

## CSS

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

## Templates and accessibility

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
