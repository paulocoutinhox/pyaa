(() => {
    'use strict'

    const LIGHT_THEME = 'light'
    const DARK_THEME = 'black'

    const getStoredTheme = () => localStorage.getItem('theme')

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        if (storedTheme) {
            return storedTheme
        }
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? DARK_THEME : LIGHT_THEME
    }

    const setTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme)
    }

    const updateThemeToggle = (theme) => {
        const toggle = document.querySelector('.theme-controller')
        if (toggle) {
            toggle.checked = (theme === DARK_THEME)
        }
    }

    // Set initial theme
    setTheme(getPreferredTheme())

    window.addEventListener('DOMContentLoaded', () => {
        updateThemeToggle(getPreferredTheme())

        // Handle DaisyUI swap toggle
        const themeToggle = document.querySelector('.theme-controller')
        if (themeToggle) {
            themeToggle.addEventListener('change', (e) => {
                const theme = e.target.checked ? DARK_THEME : LIGHT_THEME
                localStorage.setItem('theme', theme)
                setTheme(theme)
            })
        }
    })

    // Update theme if system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!getStoredTheme()) {
            const theme = e.matches ? DARK_THEME : LIGHT_THEME
            setTheme(theme)
            updateThemeToggle(theme)
        }
    })
})()
