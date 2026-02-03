class CustomFeatures extends HTMLElement {
    connectedCallback() {
        this.attachShadow({ mode: 'open' });
        this.shadowRoot.innerHTML = `
            <style>
                .feature-grid { display: grid; gap: 2rem; }
                @media (min-width: 768px) { .feature-grid { grid-template-columns: repeat(2, 1fr); } }
                @media (min-width: 1024px) { .feature-grid { grid-template-columns: repeat(4, 1fr); } }
                .feature-item {
                    background: white;
                    padding: 1.5rem;
                    border-radius: 0.5rem;
                    box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);
                    transition: box-shadow 0.3s;
                }
                .feature-item:hover { box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
                :host-context(html.dark) .feature-item {
                    background: #1f2937;
                    box-shadow: 0 1px 3px 0 rgba(0,0,0,0.3);
                }
                :host-context(html.dark) .feature-item:hover { box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
                .feature-icon {
                    display: flex; align-items: center; justify-content: center;
                    width: 4rem; height: 4rem; border-radius: 9999px;
                    background: #dbeafe; color: #2563eb; margin-bottom: 1rem;
                }
                :host-context(html.dark) .feature-icon { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
                .feature-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem; color: #1f2937; }
                :host-context(html.dark) .feature-title { color: #f3f4f6; }
                .feature-desc { color: #4b5563; }
                :host-context(html.dark) .feature-desc { color: #9ca3af; }
                .w-8 { width: 2rem; } .h-8 { height: 2rem; }
            </style>
            <div class="feature-grid">
                <div class="feature-item">
                    <div class="feature-icon"><i data-feather="bookmark" class="w-8 h-8"></i></div>
                    <h3 class="feature-title">Умное выделение</h3>
                    <p class="feature-desc">ИИ автоматически выделяет сложные слова и фразы, предлагая их перевод и объяснение.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon"><i data-feather="mic" class="w-8 h-8"></i></div>
                    <h3 class="feature-title">Аудио сопровождение</h3>
                    <p class="feature-desc">Профессиональное озвучивание текста с возможностью регулировки скорости.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon"><i data-feather="activity" class="w-8 h-8"></i></div>
                    <h3 class="feature-title">Анализ прогресса</h3>
                    <p class="feature-desc">Подробная статистика вашего чтения и запоминания новых слов.</p>
                </div>
                <div class="feature-item">
                    <div class="feature-icon"><i data-feather="layers" class="w-8 h-8"></i></div>
                    <h3 class="feature-title">Персонализация</h3>
                    <p class="feature-desc">Рекомендации книг и упражнений на основе вашего уровня и интересов.</p>
                </div>
            </div>
        `;
    }
}

customElements.define('custom-features', CustomFeatures);