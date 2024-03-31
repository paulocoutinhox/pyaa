/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/templates/**/*.html',
    ],
    safelist: [

    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
