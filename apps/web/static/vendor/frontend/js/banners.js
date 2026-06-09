import { language } from "./config.js";

const VIEW_URL = "/banner/track-view-access/";
const CLICK_URL = "/banner/track-click-access/";

const buildHeaders = () => {
    const headers = { "Content-Type": "application/json" };

    if (language) {
        headers["Accept-Language"] = language;
    }

    return headers;
};

const track = (url, token) =>
    fetch(url, {
        method: "POST",
        headers: buildHeaders(),
        body: JSON.stringify({ token }),
    });

const navigate = (url, external) => {
    if (!url) {
        return;
    }

    if (external) {
        window.open(url, "_blank");
    } else {
        window.location.href = url;
    }
};

const trackViews = (carousel) => {
    carousel.querySelectorAll("[data-banner-view]").forEach((item) => {
        track(VIEW_URL, item.dataset.bannerToken);
    });
};

const bindClicks = (carousel) => {
    carousel.querySelectorAll("[data-banner-click]").forEach((element) => {
        element.addEventListener("click", (event) => {
            event.preventDefault();

            const token = element.dataset.bannerToken;
            const link = element.dataset.bannerLink || "";
            const external = element.dataset.bannerTargetBlank === "true";

            track(CLICK_URL, token).finally(() => navigate(link, external));
        });
    });
};

const initCarousel = (carousel) => {
    const items = [...carousel.querySelectorAll(".carousel-item")];

    if (items.length <= 1) {
        return;
    }

    const indicators = [...document.querySelectorAll("[data-carousel-to]")];
    let current = 0;

    const show = (index) => {
        current = (index + items.length) % items.length;
        items.forEach((item, i) => item.classList.toggle("hidden", i !== current));
        indicators.forEach((btn, i) =>
            btn.classList.toggle("btn-active", i === current),
        );
    };

    carousel
        .querySelectorAll("[data-carousel-prev]")
        .forEach((btn) => btn.addEventListener("click", () => show(current - 1)));

    carousel
        .querySelectorAll("[data-carousel-next]")
        .forEach((btn) => btn.addEventListener("click", () => show(current + 1)));

    indicators.forEach((btn) =>
        btn.addEventListener("click", () => show(Number(btn.dataset.carouselTo))),
    );

    setInterval(() => show(current + 1), 5000);
};

document.addEventListener("DOMContentLoaded", () => {
    const carousel = document.getElementById("bannerCarousel");

    if (!carousel) {
        return;
    }

    trackViews(carousel);
    bindClicks(carousel);
    initCarousel(carousel);
});
