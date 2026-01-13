import "../css/frontend.css";

// theme switcher
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.querySelector('.theme-controller');

    if (themeToggle) {
        // load saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);

        if (savedTheme === 'dark') {
            themeToggle.checked = true;
        }

        // handle theme change
        themeToggle.addEventListener('change', (e) => {
            const theme = e.target.checked ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    }
});
