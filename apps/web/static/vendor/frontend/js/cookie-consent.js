import { cookieConsentVersion } from "./config.js";

const STORAGE_KEY = "cookie-consent";
const UPDATED_EVENT = "cookie-consent:updated";
const OPTIONAL_CATEGORIES = ["analytics"];

const readStored = () => {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);

        if (!raw) {
            return null;
        }

        const parsed = JSON.parse(raw);

        if (!parsed || parsed.version !== cookieConsentVersion) {
            return null;
        }

        return parsed;
    } catch (error) {
        return null;
    }
};

const writeStored = (categories) => {
    const payload = {
        version: cookieConsentVersion,
        categories,
        updatedAt: new Date().toISOString(),
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
};

const normalize = (categories) => {
    const result = { essential: true };

    OPTIONAL_CATEGORIES.forEach((category) => {
        result[category] = Boolean(categories && categories[category]);
    });

    return result;
};

const getCategories = () => {
    const stored = readStored();
    return normalize(stored ? stored.categories : {});
};

const broadcast = (categories) => {
    window.dispatchEvent(
        new CustomEvent(UPDATED_EVENT, { detail: { categories } }),
    );
};

const getBanner = () => document.getElementById("cookie-consent-banner");
const getModal = () => document.getElementById("cookie-consent-modal");

const showBanner = () => getBanner()?.classList.remove("hidden");
const hideBanner = () => getBanner()?.classList.add("hidden");

const syncModalInputs = () => {
    const current = getCategories();

    OPTIONAL_CATEGORIES.forEach((category) => {
        const input = document.querySelector(
            `#cookie-consent-modal [data-category="${category}"]`,
        );

        if (input) {
            input.checked = current[category];
        }
    });
};

const collectModalInputs = () => {
    const result = {};

    OPTIONAL_CATEGORIES.forEach((category) => {
        const input = document.querySelector(
            `#cookie-consent-modal [data-category="${category}"]`,
        );

        result[category] = Boolean(input && input.checked);
    });

    return result;
};

const openModal = () => {
    const modal = getModal();

    if (modal && typeof modal.showModal === "function") {
        syncModalInputs();
        modal.showModal();
    }
};

const closeModal = () => {
    const modal = getModal();

    if (modal && typeof modal.close === "function") {
        modal.close();
    }
};

const persist = (categories) => {
    const normalized = normalize(categories);
    writeStored(normalized);
    broadcast(normalized);
    hideBanner();
    closeModal();
};

const actions = {
    acceptAll() {
        persist({ analytics: true });
    },
    rejectAll() {
        persist({ analytics: false });
    },
    savePreferences() {
        persist(collectModalInputs());
    },
    openPreferences() {
        openModal();
    },
};

const bindActions = () => {
    document.querySelectorAll("[data-cookie-action]").forEach((element) => {
        element.addEventListener("click", (event) => {
            event.preventDefault();

            const handler = actions[element.dataset.cookieAction];

            if (handler) {
                handler();
            }
        });
    });
};

document.addEventListener("DOMContentLoaded", () => {
    bindActions();

    if (readStored()) {
        broadcast(getCategories());
    } else {
        showBanner();
    }
});
