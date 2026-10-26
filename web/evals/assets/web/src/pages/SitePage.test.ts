import { flushPromises } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import { buttonNamed, fakeFetch, json, mountAt, stalled } from "../testing";
import SitePage from "./SitePage.vue";

describe("SitePage", () => {
  test("shows the site and links to its devices", async () => {
    fakeFetch({
      "GET /api/sites/s2": json(200, {
        id: "s2",
        name: "Harbour",
        city: "Basel",
      }),
    });

    const { wrapper } = await mountAt(SitePage, "/sites/s2");

    expect(wrapper.get("h1").text()).toBe("Harbour");
    expect(wrapper.get(".city").text()).toBe("Basel");
    expect(wrapper.get("main a").attributes("href")).toBe("/?site=s2");
  });

  test("loading shows a spinner", async () => {
    fakeFetch({ "GET /api/sites/s1": stalled() });

    const { wrapper } = await mountAt(SitePage, "/sites/s1");

    expect(wrapper.find('[aria-label="Loading site"]').exists()).toBe(true);
    expect(wrapper.get("h1").text()).toBe("Site");
  });

  test("an unknown ID says so", async () => {
    fakeFetch({ "GET /api/sites/s9": json(404, { error: "not found" }) });

    const { wrapper } = await mountAt(SitePage, "/sites/s9");

    expect(wrapper.text()).toContain("No site has the ID s9.");
  });

  test("a failed read offers to try again", async () => {
    const answers = { "GET /api/sites/s1": json(502, {}) };
    fakeFetch(answers);
    const { wrapper } = await mountAt(SitePage, "/sites/s1");
    expect(wrapper.text()).toContain("The server answered 502.");
    answers["GET /api/sites/s1"] = json(200, {
      id: "s1",
      name: "North Yard",
      city: "Zurich",
    });

    await buttonNamed(wrapper, "Try again").trigger("click");
    await flushPromises();

    expect(wrapper.get("h1").text()).toBe("North Yard");
    expect(document.activeElement).toBe(wrapper.get("h1").element);
  });
});
