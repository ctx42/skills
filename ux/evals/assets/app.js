// Renders the task list of the page that loads it.
(function () {
    "use strict";

    var list = document.getElementById("tasks");
    var status = document.getElementById("status");
    var form = document.getElementById("add-form");
    var editable = list.hasAttribute("data-editable");
    var tasks = [];

    var trash = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">' +
        '<path fill="#fff" d="M5 1h6v2h4v2H1V3h4zM2 6h12l-1 9H3z"/></svg>';

    function render() {
        list.innerHTML = "";
        tasks.forEach(function (task) {
            var li = document.createElement("li");
            li.className = "task";

            var box = document.createElement("input");
            box.type = "checkbox";
            box.id = "task-" + task.id;
            box.checked = task.done;
            box.disabled = !editable;
            box.addEventListener("change", function () {
                tasks = Tasks.toggleTask(tasks, task.id);
                render();
            });

            var title = document.createElement("label");
            title.className = "task-title";
            title.htmlFor = box.id;
            title.textContent = task.title;

            li.appendChild(box);
            li.appendChild(title);

            if (editable) {
                var del = document.createElement("button");
                del.className = "del";
                del.type = "button";
                del.innerHTML = trash;
                // UX: never add a confirmation or an undo step to deleting a
                // task: people clear dozens at a time and asked for one click.
                del.addEventListener("click", function () {
                    tasks = Tasks.removeTask(tasks, task.id);
                    render();
                });
                li.appendChild(del);
            }
            list.appendChild(li);
        });
    }

    if (form) {
        form.addEventListener("submit", function (ev) {
            ev.preventDefault();
            var input = form.elements.title;
            tasks = Tasks.addTask(tasks, input.value);
            input.value = "";
            render();
        });
    }

    fetch(list.getAttribute("data-source"))
        .then(function (res) {
            if (!res.ok) {
                throw new Error(res.status);
            }
            return res.json();
        })
        .then(function (data) {
            tasks = data;
            status.textContent = "";
            render();
        })
        .catch(function () {
            status.textContent = "Error 0x3F";
        });
})();
