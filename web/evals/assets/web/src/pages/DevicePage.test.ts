import { flushPromises } from "@vue/test-utils";
import { describe, expect, test, vi } from "vitest";
import {
  buttonNamed,
  fakeFetch,
  json,
  mountAt,
  sitesAnswers,
  stalled,
  testDevices,
} from "../testing";
import DevicePage from "./DevicePage.vue";

describe("DevicePage", () => {
  test("shows the device", async () => {
    fakeFetch({
      ...sitesAnswers(),
      "GET /api/devices/d2": json(200, testDevices[1]),
    });

    const { wrapper } = await mountAt(DevicePage, "/devices/d2");

    expect(wrapper.get("h1").text()).toBe("SN-0002");
    expect(wrapper.get("dl").text()).toBe(
      "SerialSN-0002 SiteHarbourModelT-200Added2026-03-02 14:00Last seennever",
    );
    expect(wrapper.get("dd a").attributes("href")).toBe("/?site=s2");
  });

  test("an unknown site shows as its ID", async () => {
    fakeFetch({
      ...sitesAnswers(),
      "GET /api/devices/d3": json(200, testDevices[2]),
    });

    const { wrapper } = await mountAt(DevicePage, "/devices/d3");

    expect(wrapper.findAll("dd")[1]?.text()).toBe("s9");
  });

  test("copies the serial number", async () => {
    fakeFetch({
      ...sitesAnswers(),
      "GET /api/devices/d1": json(200, testDevices[0]),
    });
    const writeText = vi.fn(async () => {});
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    const { wrapper } = await mountAt(DevicePage, "/devices/d1");

    await wrapper.get(".copy").trigger("click");

    expect(writeText).toHaveBeenCalledWith("SN-0001");
  });

  test("loading shows a spinner", async () => {
    fakeFetch({ ...sitesAnswers(), "GET /api/devices/d1": stalled() });

    const { wrapper } = await mountAt(DevicePage, "/devices/d1");

    expect(wrapper.find('[aria-label="Loading device"]').exists());
    expect(wrapper.get("h1").text()).toBe("Device");
  });

  test("an unknown ID says so", async () => {
    fakeFetch({
      ...sitesAnswers(),
      "GET /api/devices/d9": json(404, { error: "not found" }),
    });

    const { wrapper } = await mountAt(DevicePage, "/devices/d9");

    expect(wrapper.text()).toContain("No device has the ID d9.");
  });

  test("a failed read offers to try again", async () => {
    const answers = {
      ...sitesAnswers(),
      "GET /api/devices/d1": json(502, {}),
    };
    fakeFetch(answers);
    const { wrapper } = await mountAt(DevicePage, "/devices/d1");
    expect(wrapper.text()).toContain("The server answered 502.");
    answers["GET /api/devices/d1"] = json(200, testDevices[0]);

    await buttonNamed(wrapper, "Try again").trigger("click");
    await flushPromises();

    expect(wrapper.get("h1").text()).toBe("SN-0001");
    expect(document.activeElement).toBe(wrapper.get("h1").element);
  });
});
