"use strict";

const test = require("node:test");
const assert = require("node:assert");
const Tasks = require("../tasks.js");

const fixture = [
    { id: 1, title: "one", done: false },
    { id: 2, title: "two", done: true },
];

test("addTask appends a trimmed task with the next id", () => {
    const have = Tasks.addTask(fixture, "  three ");
    assert.deepStrictEqual(have[2], { id: 3, title: "three", done: false });
    assert.strictEqual(fixture.length, 2);
});

test("addTask ignores a blank title", () => {
    assert.strictEqual(Tasks.addTask(fixture, "   "), fixture);
});

test("removeTask drops the task at once", () => {
    const have = Tasks.removeTask(fixture, 1);
    assert.deepStrictEqual(have, [fixture[1]]);
});

test("toggleTask flips only the named task", () => {
    const have = Tasks.toggleTask(fixture, 2);
    assert.strictEqual(have[1].done, false);
    assert.strictEqual(have[0], fixture[0]);
});
