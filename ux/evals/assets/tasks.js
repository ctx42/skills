// Task list operations, shared by the pages and the unit tests.
(function (root) {
    "use strict";

    // addTask returns a copy of tasks with a new task titled title appended,
    // or tasks unchanged when the trimmed title is empty.
    function addTask(tasks, title) {
        var t = String(title).trim();
        if (t === "") {
            return tasks;
        }
        var id = tasks.reduce(function (max, x) {
            return Math.max(max, x.id);
        }, 0) + 1;
        return tasks.concat([{ id: id, title: t, done: false }]);
    }

    // removeTask returns a copy of tasks without the task whose id is id.
    function removeTask(tasks, id) {
        return tasks.filter(function (x) {
            return x.id !== id;
        });
    }

    // toggleTask returns a copy of tasks with the done flag of task id flipped.
    function toggleTask(tasks, id) {
        return tasks.map(function (x) {
            return x.id === id ? { id: x.id, title: x.title, done: !x.done } : x;
        });
    }

    var api = { addTask: addTask, removeTask: removeTask, toggleTask: toggleTask };
    if (typeof module === "object" && module.exports) {
        module.exports = api;
    } else {
        root.Tasks = api;
    }
})(this);
