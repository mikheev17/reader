class CustomNavbar extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .navbar {
                    transition: all 0.3s ease;
                }
                .navbar.scrolled {
                    @apply shadow-md bg-white/90 backdrop-blur-sm;
                }
                .nav-link {
                    position: relative;
                }
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
                .nav-link:hover::after {
                    width: 100%;
                }
            </style>
            <nav class="navbar fixed w-full z-50 py-4 px-6">
                <div class="container mx-auto flex justify-between items-center">
                    <a href="/" class="flex items-center">
                        <i data-feather="book-open" class="text-blue-600 w-6 h-6 mr-2"></i>
                        <span class="text-xl font-bold text-gray-800">Читалка</span>
                    </a>
                    
                    <div class="hidden md:flex items-center space-x-8">
                        <a href="#features" class="nav-link text-gray-700 hover:text-blue-600">Возможности</a>
                        <a href="#" class="nav-link text-gray-700 hover:text-blue-600">Как это работает</a>
                        <a href="#" class="nav-link text-gray-700 hover:text-blue-600">Цены</a>
                        <a href="/dashboard.html" class="nav-link text-gray-700 hover:text-blue-600">Мой кабинет</a>
                        <a href="/login.html" class="text-gray-700 hover:text-blue-600">Войти</a>
                        <a href="/register.html" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition duration-300">Регистрация</a>
</div>
                    
                    <button class="md:hidden focus:outline-none" id="mobile-menu-button">
                        <i data-feather="menu" class="w-6 h-6 text-gray-700"></i>
                    </button>
                </div>
                
                <!-- Mobile menu -->
                <div class="md:hidden hidden bg-white shadow-lg rounded-lg mt-2 py-2" id="mobile-menu">
                    <a href="#features" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Возможности</a>
                    <a href="#" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Как это работает</a>
                    <a href="#" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Цены</a>
                    <a href="/dashboard.html" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Мой кабинет</a>
                    <a href="/login.html" class="block px-4 py-2 text-gray-700 hover:bg-gray-100">Войти</a>
                    <a href="/register.html" class="block px-4 py-2 text-blue-600 hover:bg-blue-50">Регистрация</a>
</div>
            </nav>
            
            <script>
                // Mobile menu toggle
                document.getElementById('mobile-menu-button').addEventListener('click', function() {
                    const menu = document.getElementById('mobile-menu');
                    menu.classList.toggle('hidden');
                });
                
                // Navbar scroll effect
                window.addEventListener('scroll', function() {
                    const navbar = document.querySelector('.navbar');
                    if (window.scrollY > 10) {
                        navbar.classList.add('scrolled');
                    } else {
                        navbar.classList.remove('scrolled');
                    }
                });
                
                // Replace feather icons
                if (typeof feather !== 'undefined') {
                    feather.replace();
                }
            </script>
        `;
    }
}

customElements.define('custom-navbar', CustomNavbar);