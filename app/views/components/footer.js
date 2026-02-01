class CustomFooter extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                footer { background: #f3f4f6; padding: 3rem 0; }
                :host-context(html.dark) footer { background: #1f2937; border-top: 1px solid #374151; }
                .footer-link { color: #4b5563; transition: color 0.3s; }
                .footer-link:hover { color: #2563eb; }
                :host-context(html.dark) .footer-link { color: #9ca3af; }
                :host-context(html.dark) .footer-link:hover { color: #60a5fa; }
                .footer-title { color: #1f2937; font-size: 1.125rem; font-weight: 700; margin-bottom: 1rem; }
                :host-context(html.dark) .footer-title { color: #f3f4f6; }
                .footer-brand { color: #1f2937; font-size: 1.25rem; font-weight: 700; margin-bottom: 1rem; display: flex; align-items: center; }
                :host-context(html.dark) .footer-brand { color: #f3f4f6; }
                .footer-brand-icon { color: #2563eb; width: 1.5rem; height: 1.5rem; margin-right: 0.5rem; }
                :host-context(html.dark) .footer-brand-icon { color: #60a5fa; }
                .footer-desc { color: #4b5563; margin-bottom: 1rem; }
                :host-context(html.dark) .footer-desc { color: #9ca3af; }
                .footer-bottom { color: #6b7280; }
                :host-context(html.dark) .footer-bottom { color: #9ca3af; }
                .container { max-width: 1280px; margin: 0 auto; padding: 0 1rem; }
                .grid { display: grid; gap: 2rem; }
                .grid-cols-1 { grid-template-columns: 1fr; }
                @media (min-width: 768px) { .md\\:grid-cols-4 { grid-template-columns: repeat(4, 1fr); } }
                .space-y-2 > * + * { margin-top: 0.5rem; }
                .flex { display: flex; } .space-x-4 > * + * { margin-left: 1rem; }
                .space-x-6 > * + * { margin-left: 1.5rem; }
                .border-t { border-top-width: 1px; } .border-gray-200 { border-color: #e5e7eb; }
                :host-context(html.dark) .border-gray-200 { border-color: #374151; }
                .mt-8 { margin-top: 2rem; } .pt-8 { padding-top: 2rem; }
                .flex-col { flex-direction: column; }
                @media (min-width: 768px) { .md\\:flex-row { flex-direction: row; } }
                .justify-between { justify-content: space-between; } .items-center { align-items: center; }
                .mb-4 { margin-bottom: 1rem; } .mb-0 { margin-bottom: 0; }
                .text-sm { font-size: 0.875rem; } .text-lg { font-size: 1.125rem; }
                .w-5 { width: 1.25rem; } .h-5 { height: 1.25rem; }
                .w-6 { width: 1.5rem; } .h-6 { height: 1.5rem; } .mr-2 { margin-right: 0.5rem; }
            </style>
            <footer>
                <div class="container">
                    <div class="grid grid-cols-1 md:grid-cols-4">
                        <div>
                            <h3 class="footer-brand">
                                <i data-feather="book-open" class="footer-brand-icon"></i>
                                Читалка
                            </h3>
                            <p class="footer-desc">
                                Инновационное приложение для чтения английских книг с искусственным интеллектом.
                            </p>
                            <div class="flex space-x-4">
                                <a href="#" class="footer-link"><i data-feather="facebook" class="w-5 h-5"></i></a>
                                <a href="#" class="footer-link"><i data-feather="twitter" class="w-5 h-5"></i></a>
                                <a href="#" class="footer-link"><i data-feather="instagram" class="w-5 h-5"></i></a>
                                <a href="#" class="footer-link"><i data-feather="youtube" class="w-5 h-5"></i></a>
                            </div>
                        </div>
                        <div>
                            <h4 class="footer-title">Продукт</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="footer-link">Возможности</a></li>
                                <li><a href="#" class="footer-link">Цены</a></li>
                                <li><a href="#" class="footer-link">Примеры</a></li>
                                <li><a href="#" class="footer-link">Обновления</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 class="footer-title">Поддержка</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="footer-link">Помощь</a></li>
                                <li><a href="#" class="footer-link">Учебник</a></li>
                                <li><a href="#" class="footer-link">FAQ</a></li>
                                <li><a href="#" class="footer-link">Контакты</a></li>
                            </ul>
                        </div>
                        <div>
                            <h4 class="footer-title">Компания</h4>
                            <ul class="space-y-2">
                                <li><a href="#" class="footer-link">О нас</a></li>
                                <li><a href="#" class="footer-link">Блог</a></li>
                                <li><a href="#" class="footer-link">Карьера</a></li>
                                <li><a href="#" class="footer-link">Партнеры</a></li>
                            </ul>
                        </div>
                    </div>
                    <div class="border-t border-gray-200 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
                        <p class="footer-bottom mb-4 md:mb-0">© 2023 Читалка. Все права защищены.</p>
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