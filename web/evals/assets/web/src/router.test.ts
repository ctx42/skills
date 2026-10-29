import { describe, expect, test } from "vitest";
import { createMemoryHistory } from "vue-router";
import { createAppRouter, queryText } from "./router";

describe("createAppRouter", () => {
  test.each([
    ["/", "devices"],
    ["/devices/d1", "device"],
    ["/sites", "sites"],
    ["/sites/s1", "site"],
    ["/settings", "settings"],
    ["/no/such/page", "not-found"],
  ])("%s shows %s", (path, want) => {
    const router = createAppRouter(createMemoryHistory());

    const have = router.resolve(path).name;

    expect(have).toBe(want);
  });

  test("loads every page on its first visit", async () => {
    const router = createAppRouter(createMemoryHistory());
    const loaders = router
      .getRoutes()
      .map((record) => record.components?.default as () => Promise<unknown>);

    const have = await Promise.all(loaders.map((load) => load()));

    expect(have).toHaveLength(6);
  });

  test("defaults to the browser history", () => {
    const have = createAppRouter();

    expect(have.options.history.base).toBe("");
  });
});

describe("queryText", () => {
  test.each([
    ["s1", "s1"],
    [["s1", "s2"], "s1"],
    [[], ""],
    [null, ""],
    [undefined, ""],
  ])("%j gives %j", (value, want) => {
    const have = queryText(value);

    expect(have).toBe(want);
  });
});
