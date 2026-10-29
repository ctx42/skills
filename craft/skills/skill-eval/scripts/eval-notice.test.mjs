// Tests for eval-notice.mjs. Run: node --test eval-notice.test.mjs
import assert from "node:assert/strict";
import { test } from "node:test";

import { stripNotice } from "./eval-notice.mjs";

const RE = "«Acme policy»";

test("drops a trailing paragraph that matches", () => {
  const have = stripNotice("Done.\n\nNote: this falls under «Acme policy» V1.2.\n", RE);
  assert.equal(have, "Done.");
});

test("keeps the text when the last paragraph does not match", () => {
  const text = "Note: «Acme policy» applies.\n\nDone.";
  assert.equal(stripNotice(text, RE), text);
});

test("keeps a reply that is only the notice", () => {
  const text = "Note: this falls under «Acme policy».";
  assert.equal(stripNotice(text, RE), text);
});

test("keeps the text without a pattern", () => {
  const text = "Done.\n\nNote: «Acme policy».";
  assert.equal(stripNotice(text, ""), text);
  assert.equal(stripNotice(text, undefined), text);
});

test("drops only the last paragraph", () => {
  const have = stripNotice("A.\n\n«Acme policy» once.\n\n«Acme policy» twice.", RE);
  assert.equal(have, "A.\n\n«Acme policy» once.");
});
