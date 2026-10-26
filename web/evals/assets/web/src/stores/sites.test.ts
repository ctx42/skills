import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, test } from "vitest";
import {
  fakeFetch,
  json,
  sitesAnswers,
  sitesPath,
  testSites,
} from "../testing";
import { useSitesStore } from "./sites";

beforeEach(() => setActivePinia(createPinia()));

describe("useSitesStore", () => {
  test("loads the sites and maps them by ID", async () => {
    fakeFetch(sitesAnswers());
    const store = useSitesStore();

    await store.load();

    expect(store.sites).toEqual(testSites);
    expect(store.byId.get("s2")?.name).toBe("Harbour");
  });

  test("loads only once", async () => {
    const fetched = fakeFetch(sitesAnswers());
    const store = useSitesStore();
    await store.load();

    await store.load();

    expect(fetched).toHaveBeenCalledOnce();
  });

  test("callers during a load share it", async () => {
    const fetched = fakeFetch(sitesAnswers());
    const store = useSitesStore();

    await Promise.all([store.load(), store.load()]);

    expect(fetched).toHaveBeenCalledOnce();
  });

  test("a failure leaves the sites empty and the next load retries", async () => {
    const answers = { [sitesPath]: json(502, {}) };
    const fetched = fakeFetch(answers);
    const store = useSitesStore();
    await store.load();
    expect(store.sites).toEqual([]);
    Object.assign(answers, sitesAnswers());

    await store.load();

    expect(store.sites).toEqual(testSites);
    expect(fetched).toHaveBeenCalledTimes(2);
  });
});
