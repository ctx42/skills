import { describe, expect, test } from "vitest";
import { mountAt } from "../testing";
import AppLayout from "./AppLayout.vue";

describe("AppLayout", () => {
  test("names the page in the heading and the browser tab", async () => {
    const { wrapper } = await mountAt(AppLayout, "/", { title: "Devices" });

    await wrapper.setProps({ title: "Sites" });

    expect(wrapper.get("h1").text()).toBe("Sites");
    expect(document.title).toBe("Sites · Fleet");
  });

  test("links every page from the navigation", async () => {
    const { wrapper } = await mountAt(AppLayout, "/", { title: "Devices" });

    const have = wrapper
      .get("nav")
      .findAll("a")
      .map((a) => a.attributes("href"));

    expect(have).toEqual(["/", "/sites", "/settings"]);
  });
});
