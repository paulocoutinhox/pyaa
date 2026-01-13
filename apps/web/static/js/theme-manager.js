(() => {
    'use strict'

    const storedTheme = localStorage.getItem('theme') || 'light'

    const getPreferredTheme = () => {
        if (storedTheme) {
            return storedTheme
        }

        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const setTheme = function (theme) {
        if (theme === 'auto') {
            document.documentElement.setAttribute('data-bs-theme',
                window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
            )
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme)
        }
    }

    setTheme(getPreferredTheme())

    const showActiveTheme = (theme) => {
        const themeSwitchers = document.querySelectorAll('[data-bs-theme-value]')

        themeSwitchers.forEach(switcher => {
            const btnIcon = switcher.querySelector('i')
            const themeName = switcher.getAttribute('data-bs-theme-value')

            switcher.classList.remove('active')

            if (themeName === theme) {
                switcher.classList.add('active')
            }
        })
    }

    window.addEventListener('DOMContentLoaded', () => {
        showActiveTheme(getPreferredTheme())

        document.querySelectorAll('[data-bs-theme-value]')
            .forEach(toggle => {
                toggle.addEventListener('click', () => {
                    const theme = toggle.getAttribute('data-bs-theme-value')
                    localStorage.setItem('theme', theme)
                    setTheme(theme)
                    showActiveTheme(theme)
                })
            })
    })

    // Update theme if system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (storedTheme !== 'light' && storedTheme !== 'dark') {
            setTheme(getPreferredTheme())
        }
    })
})()
