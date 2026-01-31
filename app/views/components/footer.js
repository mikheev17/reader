class CustomFooter extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .footer-link {
                    @apply text-gray-600 hover:text-blue-600 transition duration-300;
                }
            </style>
            <footer class="bg-gray-100 py-12">
                <div class="container mx-auto px-4">
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                        <div>
                            <h3 class="text-xl font-bold mb-4 flex items-center">
                                <i data-feather="book-open" class="text-blue-600 w-6 h-6 mr-2"></i>
                                Читалка
                            </h3>
                            <p class="text-gray-600 mb-4">
                                Инновационное приложение для чтения английских книг с искусственным интеллектом.
                            </p>
                            <div class="flex space-x-4">
                                <a href="#" class="footer-link">
                                    <i data-feather="facebook" class="w-5 h-5"></i>
                                </a>
                                <a href="#" class="footer-link">
                                    <i data-feather="twitter" class="w-5 h-5"></i>
                                </a>
                                <a href="#" class="footer-link">
                                    <i data-feather="instagram" class="w-5 h-5"></i>
                                </a>
                                <a href="#" class="footer-link">
                                    <i data-feather="youtube" class="w-5 h-5"></i>
                                </a>
                            </div>
                        </div>
                        
                        <div>
                            <h4 class="font-bold text-lg mb-4 text-gray-800">Продукт</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="footer-link">Возможности</a></li>
                                <li><a href="#" class="footer-link">Цены</a></li>
                                <li><a href="#" class="footer-link">Примеры</a></li>
                                <li><a href="#" class="footer-link">Обновления</a></li>
                            </ul>
                        </div>
                        
                        <div>
                            <h4 class="font-bold text-lg mb-4 text-gray-800">Поддержка</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="footer-link">Помощь</a></li>
                                <li><a href="#" class="footer-link">Учебник</a></li>
                                <li><a href="#" class="footer-link">FAQ</a></li>
                                <li><a href="#" class="footer-link">Контакты</a></li>
                            </ul>
                        </div>
                        
                        <div>
                            <h4 class="font-bold text-lg mb-4 text-gray-800">Компания</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="footer-link">О нас</a></li>
                                <li><a href="#" class="footer-link">Блог</a></li>
                                <li><a href="#" class="footer-link">Карьера</a></li>
                                <li><a href="#" class="footer-link">Партнеры</a></li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="border-t border-gray-200 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
                        <p class="text-gray-500 mb-4 md:mb-0">© 2023 Читалка. Все права защищены.</p>
                        <div class="flex space-x-6">
                            <a href="#" class="footer-link text-sm">Условия использования</a>
                            <a href="#" class="footer-link text-sm">Политика конфиденциальности</a>
                        </div>
                    </div>
                </div>
            </footer>
            
            <script>
                if (typeof feather !== 'undefined') {
                    feather.replace();
                }
            </script>
        `;
    }
}

customElements.define('custom-footer', CustomFooter);