class CustomFeatures extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .feature-icon {
                    @apply flex items-center justify-center w-16 h-16 rounded-full bg-blue-100 text-blue-600 mb-4;
                }
            </style>
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div class="feature-item bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition duration-300">
                    <div class="feature-icon">
                        <i data-feather="bookmark" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-gray-800">Умное выделение</h3>
                    <p class="text-gray-600">
                        ИИ автоматически выделяет сложные слова и фразы, предлагая их перевод и объяснение.
                    </p>
                </div>
                
                <div class="feature-item bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition duration-300">
                    <div class="feature-icon">
                        <i data-feather="mic" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-gray-800">Аудио сопровождение</h3>
                    <p class="text-gray-600">
                        Профессиональное озвучивание текста с возможностью регулировки скорости.
                    </p>
                </div>
                
                <div class="feature-item bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition duration-300">
                    <div class="feature-icon">
                        <i data-feather="activity" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-gray-800">Анализ прогресса</h3>
                    <p class="text-gray-600">
                        Подробная статистика вашего чтения и запоминания новых слов.
                    </p>
                </div>
                
                <div class="feature-item bg-white p-6 rounded-lg shadow-sm hover:shadow-md transition duration-300">
                    <div class="feature-icon">
                        <i data-feather="layers" class="w-8 h-8"></i>
                    </div>
                    <h3 class="text-xl font-bold mb-2 text-gray-800">Персонализация</h3>
                    <p class="text-gray-600">
                        Рекомендации книг и упражнений на основе вашего уровня и интересов.
                    </p>
                </div>
            </div>
        `;
    }
}

customElements.define('custom-features', CustomFeatures);