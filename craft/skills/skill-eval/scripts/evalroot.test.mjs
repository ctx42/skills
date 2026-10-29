// Tests for evalroot.mjs. Run: node --test evalroot.test.mjs (from scripts/)
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { test } from "node:test";

import { findRoot } from "./evalroot.mjs";

const tmp = () => fs.realpathSync(fs.mkdtempSync(path.join(os.tmpdir(), "evalroot-")));

test("the environment wins", () => {
  const dir = tmp();
  assert.equal(findRoot({ SKILL_EVAL_ROOT: dir }, os.tmpdir()), dir);
});

test("the git top level of the working directory", () => {
  const dir = tmp();
  execFileSync("git", ["init", "-q", dir]);
  fs.mkdirSync(path.join(dir, "a", "b"), { recursive: true });
  assert.equal(findRoot({}, path.join(dir, "a", "b")), dir);
});

test("the working directory outside git", () => {
  const dir = tmp();
  const env = { GIT_CEILING_DIRECTORIES: path.dirname(dir), PATH: process.env.PATH };
  assert.equal(findRoot(env, dir), dir);
});
