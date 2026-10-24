import assert from "node:assert/strict";
import { test } from "node:test";
import { filterDevices, sortDevices, uniqueTags } from "../lib.js";

const devices = [
  { id: 1, name: "device-0002", tags: ["edge", "lab"] },
  { id: 2, name: "device-0001", tags: ["lab", "core"] },
];

test("uniqueTags keeps the first-seen order", () => {
  assert.deepEqual(uniqueTags(devices), ["edge", "lab", "core"]);
});

test("filterDevices matches a name or a tag", () => {
  assert.deepEqual(filterDevices(devices, "0001").map((d) => d.id), [2]);
  assert.deepEqual(filterDevices(devices, "edge").map((d) => d.id), [1]);
  assert.equal(filterDevices(devices, " ").length, 2);
});

test("sortDevices orders by name both ways", () => {
  assert.deepEqual(sortDevices(devices, false).map((d) => d.id), [2, 1]);
  assert.deepEqual(sortDevices(devices, true).map((d) => d.id), [1, 2]);
});
