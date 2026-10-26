import { describe, expect, test } from "vitest";
import { mountAt, testDevices, testSites } from "../testing";
import DeviceTable from "./DeviceTable.vue";

/** Returns the text of each cell of each body row of `wrapper`. */
function cells(wrapper: Awaited<ReturnType<typeof mountAt>>["wrapper"]) {
  return wrapper
    .findAll("tbody tr")
    .map((row) => row.findAll("td").map((td) => td.text()));
}

describe("DeviceTable", () => {
  test("a row per device, by serial", async () => {
    const props = {
      devices: [...testDevices].reverse(),
      sites: new Map(testSites.map((s) => [s.id, s])),
      zone: "utc",
    };

    const { wrapper } = await mountAt(DeviceTable, "/", props);

    expect(cells(wrapper)).toEqual([
      ["SN-0001", "North Yard", "T-100", "2026-10-20 07:15"],
      ["SN-0002", "Harbour", "T-200", "never"],
      ["XN-0003", "s9", "H-10", "2026-10-22 05:00"],
    ]);
    expect(wrapper.get("tbody a").attributes("href")).toBe("/devices/d1");
  });

  test("sorts by site name", async () => {
    const { wrapper } = await mountAt(DeviceTable, "/", {
      devices: testDevices,
      sites: new Map(testSites.map((s) => [s.id, s])),
      zone: "utc",
    });

    await wrapper.findAll("th")[1]?.trigger("click");

    const have = cells(wrapper).map((row) => row[1]);
    expect(have).toEqual(["Harbour", "North Yard", "s9"]);
  });
});
