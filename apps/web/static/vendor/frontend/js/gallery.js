import GLightbox from "glightbox";
import "glightbox/dist/css/glightbox.min.css";

document.addEventListener("DOMContentLoaded", () => {
    if (!document.querySelector(".gallery-item")) {
        return;
    }

    GLightbox({
        selector: ".gallery-item",
        loop: true,
        touchNavigation: true,
        zoomable: true,
    });
});
