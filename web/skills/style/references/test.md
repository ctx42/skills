# Web style — Test

Rules for `*.test.ts` and `e2e/*.spec.ts` files, on top of `production.md`: a
test file obeys both, and a rule here overrides the Production rule it
contradicts.

## Contents

- Shape and naming
- Fixtures and fakes
- Component, page, and store tests
- Cleanup and config
- End-to-end (Playwright)

## Shape and naming

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

## Fixtures and fakes

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

## Component, page, and store tests

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

## Cleanup and config

- Reset test state centrally: `restoreMocks` and `unstubGlobals` in the
  Vitest config, `enableAutoUnmount(afterEach)` and `localStorage.clear()` in
  the setup file; never per test file.
- Hold coverage thresholds just below the measured totals; delete code no test
  can reach rather than lower them.

## End-to-end (Playwright)

- Write one top-level `test` per user flow, no `describe`, narrating its
  steps in `//` comments.
- Locate by role and accessible name; when none fits, a semantic `data-<noun>`
  attribute; never `data-testid` or a layout class.
- Put each page region behind a documented `(page) => Locator` helper.
- Run against the built server backed by a fake upstream; extend the fake per
  test with `page.route` falling back to it.
- Read credentials only from the environment, and `test.skip` with a reason
  when they are missing.
