// Tests for eval-model.mjs. Run: node --test eval-model.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import { mainModel } from "./eval-model.mjs";

test("mainModel picks the costliest model", () => {
  const have = mainModel({ "claude-helper-1": { costUSD: 0.001 }, "claude-main-1": { costUSD: 0.4 } });

  assert.equal(have, "claude-main-1");
});

test("mainModel returns the only model", () => {
  const have = mainModel({ "claude-main-1": { costUSD: 0 } });

  assert.equal(have, "claude-main-1");
});

test("mainModel returns null without usage", () => {
  assert.equal(mainModel(undefined), null);
  assert.equal(mainModel({}), null);
});
