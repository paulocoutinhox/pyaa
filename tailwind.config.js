/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui";

export default {
    content: [
        "./templates/**/*.html",
        "./apps/web/static/vendor/frontend/js/**/*.js",
    ],
    theme: {
        extend: {},
    },
    plugins: [daisyui],
    daisyui: {
        themes: ["light", "black"],
    },
};
