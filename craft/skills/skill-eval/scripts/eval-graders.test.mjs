// Tests for eval-graders.mjs. Run: node --test eval-graders.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import { asserts, canUse } from "./eval-graders.mjs";

test("asserts: a regex that must match asserts something", () => {
  assert.equal(asserts({ type: "regex" }), true);
  assert.equal(asserts({ type: "regex", match: "contains" }), true);
  assert.equal(asserts({ type: "regex", match: "count:2" }), true);
});

test("asserts: a regex that must not match asserts nothing", () => {
  assert.equal(asserts({ type: "regex", match: "not_contains" }), false);
  assert.equal(asserts({ type: "regex", match: "count:0" }), false);
});

test("asserts: tool_used asserts only a use", () => {
  assert.equal(asserts({ type: "tool_used" }), true);
  assert.equal(asserts({ type: "tool_used", min: "2" }), true);
  assert.equal(asserts({ type: "tool_used", max: "0" }), false);
  assert.equal(asserts({ type: "tool_used", min: "0", max: "3" }), false);
});

test("asserts: file_exists asserts only a created file", () => {
  assert.equal(asserts({ type: "file_exists" }), true);
  assert.equal(asserts({ type: "file_exists", exists: "false" }), false);
});

test("asserts: tool_order and llm assert something", () => {
  assert.equal(asserts({ type: "tool_order" }), true);
  assert.equal(asserts({ type: "llm" }), true);
});

test("canUse: a tool the case allows", () => {
  assert.equal(canUse("Bash", ["Read", "Bash(git:*)"], true), true);
  assert.equal(canUse("Read", ["Read"], true), true);
});

test("canUse: a mocked MCP tool", () => {
  assert.equal(canUse("mcp__srd__report_gap", [], false), true);
});

test("canUse: Write, Edit, and LSP only in a plain case", () => {
  assert.equal(canUse("Write", ["Read"], false), true);
  assert.equal(canUse("Edit", ["Read"], false), true);
  assert.equal(canUse("Write", ["Read", "Bash(git:*)"], true), false);
});

test("canUse: a tool the case does not allow", () => {
  assert.equal(canUse("Bash", ["Read"], false), false);
  assert.equal(canUse("WebFetch", ["Read"], false), false);
});
