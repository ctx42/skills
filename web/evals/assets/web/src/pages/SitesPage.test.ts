import { flushPromises } from "@vue/test-utils";
import { describe, expect, test } from "vitest";
import {
  buttonNamed,
  fakeFetch,
  json,
  mountAt,
  sitesAnswers,
  sitesPath,
  stalled,
} from "../testing";
import SitesPage from "./SitesPage.vue";

describe("SitesPage", () => {
  test("lists the sites by name, each linking to its devices", async () => {
    fakeFetch(sitesAnswers());

    const { wrapper } = await mountAt(SitesPage, "/sites");

    const have = wrapper.findAll("li a").map((a) => a.attributes("href"));
    expect(have).toEqual(["/?site=s2", "/sites/s2", "/?site=s1", "/sites/s1"]);
    expect(wrapper.get("li span").text()).toBe("Basel");
  });

  test("the city filter narrows the sites", async () => {
    fakeFetch(sitesAnswers());
    const { wrapper } = await mountAt(SitesPage, "/sites");

    await wrapper.get("input").setValue(" zur ");

    expect(wrapper.findAll("li")).toHaveLength(1);
    expect(wrapper.get("li span").text()).toBe("Zurich");
  });

  test("no sites says so", async () => {
    fakeFetch(sitesAnswers([]));

    const { wrapper } = await mountAt(SitesPage, "/sites");

    expect(wrapper.text()).toContain("No sites yet.");
  });

  test("loading shows a spinner", async () => {
    fakeFetch({ [sitesPath]: stalled() });

    const { wrapper } = await mountAt(SitesPage, "/sites");

    expect(wrapper.find('[aria-label="Loading sites"]').exists()).toBeTruthy();
  });

  test("a failed read offers to try again", async () => {
    const answers = { [sitesPath]: json(502, {}) };
    fakeFetch(answers);
    const { wrapper } = await mountAt(SitesPage, "/sites");
    expect(wrapper.text()).toContain("The server answered 502.");
    Object.assign(answers, sitesAnswers());

    await buttonNamed(wrapper, "Try again").trigger("click");
    await flushPromises();

    expect(wrapper.findAll("li")).toHaveLength(2);
    expect(document.activeElement).toBe(wrapper.get("h1").element);
  });
});
