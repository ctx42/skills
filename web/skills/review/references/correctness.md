# review correctness

Read in Check mode, after the style dimension. Look for what style does not
cover; each item names the defect, not a rule to quote. A form the style rules
require is never a defect here.

## Reactivity

- A store destructured without `storeToRefs`, or a `reactive` object or a
  ref's `.value` copied into a plain variable at setup: the copy never
  updates.
- A `watch` whose source is a value read once (`watch(props.id, …)`,
  `watch(store.items.length, …)`) instead of a getter or ref.
- A `computed` with side effects, or one mutating its own sources.
- A prop, or an object a prop holds, mutated by the child.
- A page reused across route changes (same component, new params or query)
  that reads only in `onMounted`: the new route shows the old answer.

## Lifecycle and leaks

- A listener, observer, timer, interval, or library instance started in
  setup or `onMounted` with no matching removal in `onBeforeUnmount`; search
  for every `addEventListener`, `setInterval`, `setTimeout`, `observe(`, and
  `new <Library>` with no release at all, not only for releases done wrong.
- A `watch` or `effectScope` created inside a store action, which runs per
  call and is never stopped.

## Async

- A superseded answer written to state: two reads can overlap (a filter, a
  route param, a retry) and the slower, older one lands last.
- State written after the component unmounted, or a `busy` flag a failure
  path never clears (no `finally`).
- A promise neither awaited nor `void`ed whose rejection is lost, or an
  `await` inside a loop where the reads are independent.
- A double action: a submit or delete button that stays enabled while its
  request runs.

## Router

- A guard that can neither return nor redirect on some path, or that reads a
  store not yet loaded.
- A param or query value assumed to be a string when vue-router may give an
  array or `null`.
- `router.push`/`replace` results ignored where a failed navigation must be
  shown.

## PrimeVue

- `DataTable` selection, expansion, or editing without `data-key`, or sorting
  on a field the rows do not carry.
- `Select`, `SelectButton`, or `MultiSelect` with object options and no
  `option-value`, so the model holds whole objects compared by identity.
- A `Dialog`'s `visible` bound one-way, so closing it from inside does not
  update the parent.
- A lazy `DataTable` or paginator whose `page`/`sort` events are not handled.

## Templates and security

- An index `:key` on a list that reorders or filters.
- `target="_blank"` without `rel="noopener"`; server text placed in an
  attribute that executes (`href="javascript:…"`).
- A server error message shown raw to the user where it may carry internals.

## Tests

- A test that passes while the code is wrong: an `expect` with no matcher, an
  assertion on a value shared by every branch, a missing `await
  flushPromises()` before asserting async output, a fake `fetch` that answers
  any request.
- A behaviour the code has with no test reaching it: a branch, an error path,
  an event handler.
- Shared state leaking between tests (a stubbed global, a listener, a
  module-level value) that makes order matter.
