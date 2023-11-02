document.addEventListener("DOMContentLoaded", function () {
    var currentPageURL = window.location.href;
    var menuLinks = document.querySelectorAll(".nav-link"); // Schimbați selectorul pentru a se potrivi cu elementele meniului dvs.

    menuLinks.forEach(function (link) {
        if (currentPageURL.includes(link.href)) {
            link.classList.add("active-link");
        }
    });
});