// Tests for eval-guard.mjs. Run: node --test eval-guard.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import { denyHomeEdits, homeCommands, homeWrites } from "./eval-guard.mjs";

const HOME = "/home/u", WS = "/tmp/claude-eval-sh-1";

function write(id, input, name = "Write") {
  return { type: "assistant", message: { content: [{ type: "tool_use", id, name, input }] } };
}

function result(id, isError = false) {
  return { type: "user", message: { content: [{ type: "tool_result", tool_use_id: id, is_error: isError }] } };
}

test("denyHomeEdits denies edits under the real home", () => {
  const have = denyHomeEdits(HOME, WS);

  assert.deepEqual(have, ["--disallowedTools", "Edit(//home/u/**)"]);
});

test("denyHomeEdits denies nothing when the workspace is inside the home", () => {
  const have = denyHomeEdits(HOME, "/home/u/tmp/claude-eval-sh-1");

  assert.deepEqual(have, []);
});

test("homeWrites lists a write into the real home", () => {
  const events = [write("t1", { file_path: "/home/u/.agent-data/lessons/go/doc.md" }), result("t1")];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, ["/home/u/.agent-data/lessons/go/doc.md"]);
});

test("homeWrites lists Edit and NotebookEdit too", () => {
  const events = [
    write("t1", { file_path: "/home/u/a.go" }, "Edit"), result("t1"),
    write("t2", { notebook_path: "/home/u/b.ipynb" }, "NotebookEdit"), result("t2"),
  ];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, ["/home/u/a.go", "/home/u/b.ipynb"]);
});

test("homeWrites skips a refused write", () => {
  const events = [write("t1", { file_path: "/home/u/x.md" }), result("t1", true)];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, []);
});

test("homeWrites skips writes inside the workspace and relative paths", () => {
  const events = [
    write("t1", { file_path: `${WS}/home/cwd/x.md` }), result("t1"),
    write("t2", { file_path: "notes/y.md" }), result("t2"),
    write("t3", { file_path: "~/.agent-data/z.md" }), result("t3"),
  ];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, []);
});

test("homeWrites skips writes outside the real home", () => {
  const events = [write("t1", { file_path: "/tmp/other/x.md" }), result("t1")];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, []);
});

test("homeWrites does not match a sibling of the home by prefix", () => {
  const events = [write("t1", { file_path: "/home/u2/x.md" }), result("t1")];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, []);
});

test("homeWrites skips a write with no result", () => {
  const events = [write("t1", { file_path: "/home/u/x.md" })];

  const have = homeWrites(events, HOME, WS);

  assert.deepEqual(have, []);
});

function bash(id, command) {
  return { type: "assistant", message: { content: [{ type: "tool_use", id, name: "Bash", input: { command } }] } };
}

test("homeCommands lists a Bash call that names the real home", () => {
  const events = [bash("b1", "wc -l /home/u/.agent-data/lessons/craft/cm.md"), result("b1")];

  const have = homeCommands(events, HOME);

  assert.deepEqual(have, ["wc -l /home/u/.agent-data/lessons/craft/cm.md"]);
});

test("homeCommands skips a refused call and a sibling of the home", () => {
  const events = [
    bash("b1", "cat /home/u/x"), result("b1", true),
    bash("b2", "cat /home/u2/x"), result("b2"),
    bash("b3", "go test ./..."), result("b3"),
  ];

  const have = homeCommands(events, HOME);

  assert.deepEqual(have, []);
});

test("homeCommands matches the home itself at the end of a command", () => {
  const events = [bash("b1", "ls /home/u"), result("b1")];

  const have = homeCommands(events, HOME);

  assert.deepEqual(have, ["ls /home/u"]);
});
