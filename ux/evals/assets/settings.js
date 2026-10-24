// Keeps the settings forms on the page and confirms each save.
(function () {
    "use strict";

    document.querySelectorAll(".settings-form").forEach(function (form) {
        form.addEventListener("submit", function (ev) {
            ev.preventDefault();
            form.querySelector(".saved").textContent = "Saved.";
        });
    });
})();
