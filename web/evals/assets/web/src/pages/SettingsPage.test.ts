import { describe, expect, test } from "vitest";
import { useSettingsStore } from "../stores/settings";
import { mountAt } from "../testing";
import SettingsPage from "./SettingsPage.vue";

describe("SettingsPage", () => {
  test("choosing a zone keeps it", async () => {
    const { wrapper } = await mountAt(SettingsPage, "/settings");

    await wrapper.findAll("button")[1]?.trigger("click");

    expect(useSettingsStore().zone).toBe("local");
  });
});
