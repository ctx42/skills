import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { nextTick } from "vue";
import { blockedStorage } from "../testing";
import { settingsKey, useSettingsStore } from "./settings";

beforeEach(() => setActivePinia(createPinia()));

describe("useSettingsStore", () => {
  test.each([
    [null, "utc"],
    ['{"zone":"local"}', "local"],
    ['{"zone":"utc"}', "utc"],
    ['{"zone":"mars"}', "utc"],
    ['"local"', "utc"],
    ["null", "utc"],
    ["not JSON", "utc"],
  ])("kept %s shows dates in %s", (kept, want) => {
    if (kept !== null) localStorage.setItem(settingsKey, kept);

    const have = useSettingsStore().zone;

    expect(have).toBe(want);
  });

  test("keeps a zone other than the default", async () => {
    const store = useSettingsStore();

    store.zone = "local";
    await nextTick();

    expect(localStorage.getItem(settingsKey)).toBe('{"zone":"local"}');
  });

  test("keeps nothing for the default zone", async () => {
    localStorage.setItem(settingsKey, '{"zone":"local"}');
    const store = useSettingsStore();

    store.zone = "utc";
    await nextTick();

    expect(localStorage.getItem(settingsKey)).toBeNull();
  });

  test("blocked storage keeps the zone for the visit", async () => {
    vi.stubGlobal("localStorage", blockedStorage());
    const store = useSettingsStore();

    store.zone = "local";
    await nextTick();

    expect(store.zone).toBe("local");
  });
});
