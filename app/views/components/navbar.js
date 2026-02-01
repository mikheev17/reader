class CustomNavbar extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .navbar {
                    transition: all 0.3s ease;
                    background: transparent;
                }
                .navbar.scrolled {
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
                    background: rgba(255,255,255,0.9);
                    backdrop-filter: blur(8px);
                }
                :host-context(html.dark) .navbar.scrolled {
                    background: rgba(31,41,55,0.95);
                    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
                }
                .nav-link { position: relative; color: #374151; }
                .nav-link:hover { color: #2563eb; }
                .nav-link::after {
                    content: '';
                    position: absolute;
                    bottom: -2px;
                    left: 0;
                    width: 0;
                    height: 2px;
                    background-color: #2563eb;
                    transition: width 0.3s ease;
                }
                .nav-link:hover::after { width: 100%; }
                :host-context(html.dark) .nav-link { color: #d1d5db; }
                :host-context(html.dark) .nav-link:hover { color: #93c5fd; }
                :host-context(html.dark) .nav-link::after { background-color: #60a5fa; }
                .logo-text { color: #1f2937; font-size: 1.25rem; font-weight: 700; }
                .logo-icon { color: #2563eb; }
                :host-context(html.dark) .logo-text { color: #f3f4f6; }
                :host-context(html.dark) .logo-icon { color: #60a5fa; }
                .btn-login { color: #374151; }
                .btn-login:hover { color: #2563eb; }
                :host-context(html.dark) .btn-login { color: #d1d5db; }
                :host-context(html.dark) .btn-login:hover { color: #93c5fd; }
                .btn-reg { background: #2563eb; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; transition: all 0.3s; }
                .btn-reg:hover { background: #1d4ed8; }
                .theme-btn { background: #e5e7eb; border: none; border-radius: 0.5rem; padding: 0.5rem; cursor: pointer; color: #374151; transition: all 0.2s; }
                .theme-btn:hover { background: #d1d5db; }
                :host-context(html.dark) .theme-btn { background: #4b5563; color: #d1d5db; }
                :host-context(html.dark) .theme-btn:hover { background: #6b7280; }
                .mobile-btn { color: #374151; }
                :host-context(html.dark) .mobile-btn { color: #d1d5db; }
                .mobile-menu { background: white; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-radius: 0.5rem; margin-top: 0.5rem; padding: 0.5rem 0; }
                :host-context(html.dark) .mobile-menu { background: #374151; }
                .mobile-menu a { display: block; padding: 0.5rem 1rem; color: #374151; }
                .mobile-menu a:hover { background: #f3f4f6; }
                :host-context(html.dark) .mobile-menu a { color: #d1d5db; }
                :host-context(html.dark) .mobile-menu a:hover { background: #4b5563; }
                .mobile-menu a.reg { color: #2563eb; }
                :host-context(html.dark) .mobile-menu a.reg { color: #93c5fd; }
                .container { max-width: 1280px; margin-left: auto; margin-right: auto; padding-left: 1.5rem; padding-right: 1.5rem; }
                .flex { display: flex; }
                .items-center { align-items: center; }
                .justify-between { justify-content: space-between; }
                .space-x-8 > * + * { margin-left: 2rem; }
                .nav-desktop { display: none; }
                .nav-mobile { display: flex; }
                @media (min-width: 768px) { .nav-desktop { display: flex; } .nav-mobile { display: none !important; } }
                .mobile-menu.hidden { display: none !important; }
                @media (min-width: 768px) { .mobile-menu { display: none !important; } }
                .w-6 { width: 1.5rem; } .h-6 { height: 1.5rem; } .mr-2 { margin-right: 0.5rem; }
                .py-4 { padding-top: 1rem; padding-bottom: 1rem; } .px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
                .fixed { position: fixed; } .w-full { width: 100%; } .z-50 { z-index: 50; }
                .mt-2 { margin-top: 0.5rem; } .py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
                .px-4 { padding-left: 1rem; padding-right: 1rem; } .rounded-lg { border-radius: 0.5rem; }
            </style>
            <nav class="navbar fixed w-full z-50 py-4 px-6">
                <div class="container flex justify-between items-center">
                    <a href="/" class="flex items-center">
                        <i data-feather="book-open" class="logo-icon w-6 h-6 mr-2"></i>
                        <span class="logo-text text-xl font-bold">Читалка</span>
                    </a>
                    
                    <div class="nav-desktop items-center space-x-8">
                        <a href="#features" class="nav-link">Возможности</a>
                        <a href="#" class="nav-link">Как это работает</a>
                        <a href="#" class="nav-link">Цены</a>
                        <a href="/dashboard.html" class="nav-link">Мой кабинет</a>
                        <a href="/login.html" class="btn-login">Войти</a>
                        <a href="/register.html" class="btn-reg">Регистрация</a>
                        <button type="button" class="theme-btn" id="theme-toggle" title="Тёмная тема">
                            <i data-feather="moon" class="w-5 h-5 theme-icon-sun"></i>
                            <i data-feather="sun" class="w-5 h-5 theme-icon-moon" style="display:none"></i>
                        </button>
                    </div>
                    
                    <div class="nav-mobile items-center" style="gap: 0.5rem">
                        <button type="button" class="theme-btn" id="theme-toggle-mobile" title="Тёмная тема">
                            <i data-feather="moon" class="w-5 h-5 theme-icon-sun-mob"></i>
                            <i data-feather="sun" class="w-5 h-5 theme-icon-moon-mob" style="display:none"></i>
                        </button>
                        <button class="mobile-btn focus:outline-none" id="mobile-menu-button">
                            <i data-feather="menu" class="w-6 h-6"></i>
                        </button>
                    </div>
                </div>
                
                <div class="mobile-menu hidden mt-2 py-2" id="mobile-menu">
                    <a href="#features" class="block px-4 py-2">Возможности</a>
                    <a href="#" class="block px-4 py-2">Как это работает</a>
                    <a href="#" class="block px-4 py-2">Цены</a>
                    <a href="/dashboard.html" class="block px-4 py-2">Мой кабинет</a>
                    <a href="/login.html" class="block px-4 py-2">Войти</a>
                    <a href="/register.html" class="block px-4 py-2 reg">Регистрация</a>
                </div>
            </nav>
            
            <script>
                (function() {
                    function updateThemeIcons() {
                        var isDark = document.documentElement.classList.contains('dark');
                        var suns = document.querySelectorAll('.theme-icon-sun, .theme-icon-sun-mob');
                        var moons = document.querySelectorAll('.theme-icon-moon, .theme-icon-moon-mob');
                        suns.forEach(function(el) { el.style.display = isDark ? 'none' : 'block'; });
                        moons.forEach(function(el) { el.style.display = isDark ? 'block' : 'none'; });
                    }
                    function toggleTheme() {
                        if (window.toggleDarkTheme) window.toggleDarkTheme();
                        updateThemeIcons();
                    }
                    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
                    document.getElementById('theme-toggle-mobile').addEventListener('click', toggleTheme);
                    var observer = new MutationObserver(updateThemeIcons);
                    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
                    updateThemeIcons();
                })();
                document.getElementById('mobile-menu-button').addEventListener('click', function() {
                    document.getElementById('mobile-menu').classList.toggle('hidden');
                });
                var host = this;
                window.addEventListener('scroll', function() {
                    var navbar = host.shadowRoot.querySelector('.navbar');
                    if (navbar && window.scrollY > 10) navbar.classList.add('scrolled');
                    else if (navbar) navbar.classList.remove('scrolled');
                });
                if (typeof feather !== 'undefined') feather.replace();
            </script>
        `;
    }
}

customElements.define('custom-navbar', CustomNavbar);