(function () {
    function applyTheme() {
        var saved = localStorage.getItem('theme');
        // По умолчанию тёмная тема (в HTML уже class="dark"); светлая только если пользователь выбрал
        if (saved === 'light') {
            document.documentElement.classList.remove('dark');
        } else {
            document.documentElement.classList.add('dark');
        }
    }
    applyTheme();
    window.toggleDarkTheme = function () {
        var isDark = document.documentElement.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    };
})();
