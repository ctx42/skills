import { describe, expect, test } from "vitest";
import { ApiError, device, devices, site, sites } from "./api";
import {
  devicesAnswers,
  devicesPath,
  fakeFetch,
  json,
  networkError,
  sitesAnswers,
  testDevices,
  testSites,
} from "./testing";

describe("ApiError", () => {
  test("keeps the status and message", () => {
    const have = new ApiError(502, "down");

    expect(have.status).toBe(502);
    expect(have.message).toBe("down");
    expect(have.name).toBe("ApiError");
  });
});

describe("devices", () => {
  test("of every site", async () => {
    const fetched = fakeFetch(devicesAnswers());

    const have = await devices();

    expect(have).toEqual(testDevices);
    expect(fetched).toHaveBeenCalledOnce();
  });

  test("of a site, its ID escaped", async () => {
    fakeFetch(devicesAnswers([], "s+1"));

    const have = await devices("s 1");

    expect(have).toEqual([]);
  });

  test("fields of the wrong type read as empty", async () => {
    fakeFetch({ [devicesPath()]: json(200, { data: [{ id: 7 }, null] }) });

    const have = await devices();

    const blank = {
      id: "",
      serial: "",
      site_id: "",
      model: "",
      added: "",
      last_seen: null,
    };
    expect(have).toEqual([blank, blank]);
  });

  test("an answer without a list reads as none", async () => {
    fakeFetch({ [devicesPath()]: json(200, {}) });

    const have = await devices();

    expect(have).toEqual([]);
  });

  test("a failed answer throws its status", async () => {
    fakeFetch({ [devicesPath()]: json(502, { error: "down" }) });

    const have = devices();

    await expect(have).rejects.toEqual(
      new ApiError(502, "The server answered 502."),
    );
  });

  test("an answer that is not JSON throws", async () => {
    fakeFetch({ [devicesPath()]: new Response("{", { status: 200 }) });

    const have = devices();

    await expect(have).rejects.toEqual(
      new ApiError(200, "The server answered with no data."),
    );
  });

  test("an unreachable server throws status 0", async () => {
    fakeFetch({ [devicesPath()]: networkError() });

    const have = devices();

    await expect(have).rejects.toEqual(
      new ApiError(0, "The server cannot be reached."),
    );
  });
});

describe("device", () => {
  test("by ID, escaped", async () => {
    fakeFetch({ "GET /api/devices/d%2F1": json(200, testDevices[0]) });

    const have = await device("d/1");

    expect(have).toEqual(testDevices[0]);
  });

  test("an unknown ID gives null", async () => {
    fakeFetch({ "GET /api/devices/d9": json(404, { error: "not found" }) });

    const have = await device("d9");

    expect(have).toBeNull();
  });

  test("another failure throws", async () => {
    fakeFetch({ "GET /api/devices/d1": json(502, {}) });

    const have = device("d1");

    await expect(have).rejects.toEqual(
      new ApiError(502, "The server answered 502."),
    );
  });
});

describe("site", () => {
  test("by ID, escaped, its fields checked", async () => {
    fakeFetch({
      "GET /api/sites/s%2F1": json(200, { id: "s1", name: 7, city: "Basel" }),
    });

    const have = await site("s/1");

    expect(have).toEqual({ id: "s1", name: "", city: "Basel" });
  });

  test("an unknown ID gives null", async () => {
    fakeFetch({ "GET /api/sites/s9": json(404, { error: "not found" }) });

    const have = await site("s9");

    expect(have).toBeNull();
  });

  test("another failure throws", async () => {
    fakeFetch({ "GET /api/sites/s1": json(502, {}) });

    const have = site("s1");

    await expect(have).rejects.toEqual(
      new ApiError(502, "The server answered 502."),
    );
  });
});

describe("sites", () => {
  test("every site", async () => {
    fakeFetch(sitesAnswers());

    const have = await sites();

    expect(have).toEqual(testSites);
  });
});
