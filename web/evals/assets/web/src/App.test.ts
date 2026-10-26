import { describe, expect, test } from "vitest";
import App from "./App.vue";
import { fakeFetch, mountAt } from "./testing";

describe("App", () => {
  test("shows the page the route names", async () => {
    fakeFetch({});

    const { wrapper } = await mountAt(App, "/settings");

    expect(wrapper.get("h1").text()).toBe("Settings");
  });
});
