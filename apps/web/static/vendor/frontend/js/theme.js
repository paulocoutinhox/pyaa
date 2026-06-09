const LIGHT_THEME = "lofi";
const DARK_THEME = "black";

const getStoredTheme = () => localStorage.getItem("theme");

const setTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
};

const getPreferredTheme = () => {
    const stored = getStoredTheme();

    if (stored) {
        return stored;
    }

    return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? DARK_THEME
        : LIGHT_THEME;
};

const updateToggle = (theme) => {
    const toggle = document.querySelector(".theme-controller");

    if (toggle) {
        toggle.checked = theme === DARK_THEME;
    }
};

const bindToggle = () => {
    const toggle = document.querySelector(".theme-controller");

    if (!toggle) {
        return;
    }

    toggle.addEventListener("change", (event) => {
        const theme = event.target.checked ? DARK_THEME : LIGHT_THEME;
        localStorage.setItem("theme", theme);
        setTheme(theme);
    });
};

// follow the system preference while the user has no explicit choice
window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (event) => {
        if (getStoredTheme()) {
            return;
        }

        const theme = event.matches ? DARK_THEME : LIGHT_THEME;
        setTheme(theme);
        updateToggle(theme);
    });

document.addEventListener("DOMContentLoaded", () => {
    updateToggle(getPreferredTheme());
    bindToggle();
});
