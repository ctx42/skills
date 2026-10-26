import { describe, expect, test } from "vitest";
import { mountAt } from "../testing";
import NotFoundPage from "./NotFoundPage.vue";

describe("NotFoundPage", () => {
  test("names the path and links to the devices", async () => {
    const { wrapper } = await mountAt(NotFoundPage, "/no/such");

    expect(wrapper.get("code").text()).toBe("/no/such");
    expect(wrapper.get("main a").attributes("href")).toBe("/");
  });
});
