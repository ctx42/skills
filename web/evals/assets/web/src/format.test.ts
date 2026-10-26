import { describe, expect, test } from "vitest";
import { formatDate, isDateZone } from "./format";

describe("formatDate", () => {
  test.each([
    ["2026-10-03T08:00:00Z", "2026-10-03 08:00"],
    ["2026-10-03T08:05:59.999Z", "2026-10-03 08:05"],
    ["2026-10-03T10:00:00+02:00", "2026-10-03 08:00"],
    ["2026-10-03T00:30:00Z", "2026-10-03 00:30"],
    [null, "never"],
  ])("%j in UTC gives %s", (value, want) => {
    const have = formatDate(value, "utc");

    expect(have).toBe(want);
  });

  test("in the browser's time zone", () => {
    const value = "2026-10-03T08:00:00Z";
    const time = new Date(value);
    const pad = (n: number) => String(n).padStart(2, "0");
    const want =
      `${time.getFullYear()}-${pad(time.getMonth() + 1)}-` +
      `${pad(time.getDate())} ${pad(time.getHours())}:${pad(time.getMinutes())}`;

    const have = formatDate(value, "local");

    expect(have).toBe(want);
  });
});

describe("isDateZone", () => {
  test.each([
    ["utc", true],
    ["local", true],
    ["UTC", false],
    [null, false],
  ])("%j gives %s", (value, want) => {
    const have = isDateZone(value);

    expect(have).toBe(want);
  });
});
