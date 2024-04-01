module.exports = {
    content: [
        './apps/**/*.html',
        './assets/**/*.js',
        './assets/**/*.vue',
        './assets/**/*.tsx',
        './assets/**/*.jsx',
        './templates/**/*.html',
        './pyaa/settings.py',
    ],
    safelist: [

    ],
    theme: {

    },
    variants: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/forms'),
    ],
}
