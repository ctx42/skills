import { flushPromises } from "@vue/test-utils";
import Select from "primevue/select";
import { describe, expect, test } from "vitest";
import {
  buttonNamed,
  devicesAnswers,
  devicesPath,
  fakeFetch,
  json,
  mountAt,
  networkError,
  sitesAnswers,
  stalled,
  testDevices,
} from "../testing";
import DevicesPage from "./DevicesPage.vue";

describe("DevicesPage", () => {
  test("lists every device", async () => {
    fakeFetch({ ...sitesAnswers(), ...devicesAnswers() });

    const { wrapper } = await mountAt(DevicesPage, "/");

    expect(wrapper.findAll("tbody tr")).toHaveLength(3);
    expect(wrapper.text()).toContain("North Yard");
  });

  test("starts with the site and search the query names", async () => {
    const fetched = fakeFetch({
      ...sitesAnswers(),
      ...devicesAnswers(testDevices.slice(0, 2), "s2"),
    });

    const { wrapper } = await mountAt(DevicesPage, "/?site=s2&q=0002");

    expect(fetched).toHaveBeenCalledWith("/api/devices?site=s2");
    expect(wrapper.findAll("tbody tr")).toHaveLength(1);
    expect(wrapper.get("input").element.value).toBe("0002");
  });

  test("picking a site reads its devices and names it in the address", async () => {
    fakeFetch({
      ...sitesAnswers(),
      ...devicesAnswers(),
      ...devicesAnswers(testDevices.slice(0, 1), "s1"),
    });
    const { wrapper, router } = await mountAt(DevicesPage, "/");

    wrapper.findComponent(Select).vm.$emit("update:modelValue", "s1");
    await flushPromises();

    expect(wrapper.findAll("tbody tr")).toHaveLength(1);
    expect(router.currentRoute.value.query).toEqual({ site: "s1" });
  });

  test("picking every site again leaves the site out of the address", async () => {
    fakeFetch({
      ...sitesAnswers(),
      ...devicesAnswers(),
      ...devicesAnswers(testDevices.slice(0, 1), "s1"),
    });
    const { wrapper, router } = await mountAt(DevicesPage, "/?site=s1&q=sn");

    wrapper.findComponent(Select).vm.$emit("update:modelValue", "");
    await flushPromises();

    expect(wrapper.findAll("tbody tr")).toHaveLength(2);
    expect(router.currentRoute.value.query).toEqual({ q: "sn" });
  });

  test("the search narrows to matching serial numbers", async () => {
    fakeFetch({ ...sitesAnswers(), ...devicesAnswers() });
    const { wrapper, router } = await mountAt(DevicesPage, "/");

    await wrapper.get("input").setValue(" xn ");
    await flushPromises();

    expect(wrapper.findAll("tbody tr")).toHaveLength(1);
    expect(wrapper.get("tbody").text()).toContain("XN-0003");
    expect(router.currentRoute.value.query).toEqual({ q: " xn " });
  });

  test("a search matching nothing says so", async () => {
    fakeFetch({ ...sitesAnswers(), ...devicesAnswers() });
    const { wrapper } = await mountAt(DevicesPage, "/");

    await wrapper.get("input").setValue("nope");
    await flushPromises();

    expect(wrapper.text()).toContain("No devices match.");
  });

  test("a slash focuses the search box", async () => {
    fakeFetch({ ...sitesAnswers(), ...devicesAnswers() });
    const { wrapper } = await mountAt(DevicesPage, "/");

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "/" }));

    expect(document.activeElement).toBe(wrapper.get("input").element);
  });

  test("a slash typed in a text box stays there", async () => {
    fakeFetch({ ...sitesAnswers(), ...devicesAnswers() });
    await mountAt(DevicesPage, "/");
    const other = document.createElement("input");
    document.body.append(other);
    other.focus();

    other.dispatchEvent(
      new KeyboardEvent("keydown", { key: "/", bubbles: true }),
    );

    expect(document.activeElement).toBe(other);
    other.remove();
  });

  test("another key leaves the focus", async () => {
    fakeFetch({ ...sitesAnswers(), ...devicesAnswers() });
    await mountAt(DevicesPage, "/");

    window.dispatchEvent(new KeyboardEvent("keydown", { key: "a" }));

    expect(document.activeElement).toBe(document.body);
  });

  test("loading shows a spinner", async () => {
    fakeFetch({ ...sitesAnswers(), [devicesPath()]: stalled() });

    const { wrapper } = await mountAt(DevicesPage, "/");

    expect(wrapper.find('[aria-label="Loading devices"]').exists()).toBe(true);
  });

  test("a failed read offers to try again", async () => {
    const answers = { ...sitesAnswers(), [devicesPath()]: json(502, {}) };
    fakeFetch(answers);
    const { wrapper } = await mountAt(DevicesPage, "/");
    expect(wrapper.text()).toContain("The server answered 502.");
    Object.assign(answers, devicesAnswers());

    await buttonNamed(wrapper, "Try again").trigger("click");
    await flushPromises();

    expect(wrapper.findAll("tbody tr")).toHaveLength(3);
    expect(document.activeElement).toBe(wrapper.get("h1").element);
  });

  test("an unreachable server says so", async () => {
    fakeFetch({ ...sitesAnswers(), [devicesPath()]: networkError() });

    const { wrapper } = await mountAt(DevicesPage, "/");

    expect(wrapper.text()).toContain("The server cannot be reached.");
  });
});
