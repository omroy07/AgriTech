/**
 * AgriTech Unified i18n & Server-Side Translation Bridge
 * Integrates Google Cloud Translation API via Flask backend.
 * Provides seamless client & server localization with localStorage persistence.
 * Zero dependency on Google Translate widgets/iframes.
 */

class I18nManager {
    constructor() {
        this.apiBase = window.location.origin.includes('5000') 
            ? '/api/v1' 
            : (window.API_BASE_URL || 'http://127.0.0.1:5000/api/v1');
        this.currentLang = this.getStoredLang() || 'en';
        this.cache = {};
        this.langNames = {
            'en': 'English',
            'hi': 'हिन्दी',
            'kn': 'ಕನ್ನಡ',
            'te': 'తెలుగు',
            'bn': 'বাংলা',
            'mr': 'मराठी',
            'ta': 'தமிழ்',
            'gu': 'ગુજરાતી',
            'ml': 'മലയാളം',
            'pa': 'ਪੰਜਾਬੀ'
        };
        this.init();
    }

    init() {
        // Set cookie for backend language detection
        this.setLanguageCookie(this.currentLang);

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.onDomReady());
        } else {
            this.onDomReady();
        }
    }

    onDomReady() {
        this.translatePage();
        this.updateLangUI();
        this.setupLanguageSwitcher();
    }

    getStoredLang() {
        return localStorage.getItem('agritech-lang') ||
            localStorage.getItem('agritech_lang') ||
            localStorage.getItem('selectedLang') ||
            this.getCookie('lang') ||
            'en';
    }

    getCookie(name) {
        const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[2]) : null;
    }

    setLanguageCookie(lang) {
        document.cookie = `lang=${lang}; path=/; max-age=31536000; SameSite=Lax`;
    }

    async changeLanguage(lang, label = null) {
        if (!lang) return;
        lang = lang.toLowerCase().trim();
        this.currentLang = lang;

        // Persist in localStorage across keys for full backwards compatibility
        localStorage.setItem('agritech-lang', lang);
        localStorage.setItem('agritech_lang', lang);
        localStorage.setItem('selectedLang', lang);
        this.setLanguageCookie(lang);

        // Update static UI text
        this.translatePage();
        this.updateLangUI(label);

        // Notify other components & trigger dynamic content updates
        window.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { 
                lang: lang,
                name: this.langNames[lang] || lang
            } 
        }));

        console.log(`[AgriTech i18n] Language switched to: ${lang} (${this.langNames[lang] || lang})`);
    }

    translatePage() {
        // 1. Static Dictionary translations if available
        if (window.translations && window.translations[this.currentLang]) {
            const dictionary = window.translations[this.currentLang];
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (dictionary[key]) {
                    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                        el.placeholder = dictionary[key];
                    } else {
                        el.textContent = dictionary[key];
                    }
                }
            });
        }

        // 2. Update document lang attribute
        document.documentElement.lang = this.currentLang;
    }

    updateLangUI(label = null) {
        const displayLabel = label || this.langNames[this.currentLang] || this.currentLang.toUpperCase();
        
        // Update all current-lang text containers
        document.querySelectorAll('#current-lang-text, .current-lang-label').forEach(el => {
            el.textContent = displayLabel;
        });

        // Update active class on options
        document.querySelectorAll('.lang-option, [data-lang-code]').forEach(option => {
            const optLang = option.getAttribute('data-lang-code') || 
                (option.getAttribute('onclick') && (option.getAttribute('onclick').match(/'([^']+)'/) || [])[1]);
            if (optLang === this.currentLang) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    }

    setupLanguageSwitcher() {
        // Generic dropdown toggles
        document.querySelectorAll('.lang-trigger, .lang-btn, #langTrigger, #navbarLangTrigger').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const container = btn.closest('.lang-container, .navbar-lang-container');
                if (container) {
                    const dropdown = container.querySelector('.lang-dropdown');
                    if (dropdown) {
                        dropdown.classList.toggle('active');
                    }
                }
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            document.querySelectorAll('.lang-dropdown.active').forEach(dd => dd.classList.remove('active'));
        });

        // Handle dropdown option clicks
        document.querySelectorAll('.lang-option').forEach(option => {
            option.addEventListener('click', (e) => {
                const code = option.getAttribute('data-lang-code') || 
                    (option.getAttribute('onclick') && (option.getAttribute('onclick').match(/'([^']+)'/) || [])[1]);
                const text = option.textContent.replace(/[^\w\s\u0900-\u0DFF]/gi, '').trim();
                if (code) {
                    this.changeLanguage(code, text);
                }
            });
        });
    }

    /**
     * Server-side Translation API Bridge using Google Cloud Translation API backend
     */
    async translateDynamic(text, targetLang = null, sourceLang = 'auto') {
        const lang = targetLang || this.currentLang;
        if (!text || lang === 'en') return text;

        const cacheKey = `${sourceLang}:${lang}:${text}`;
        if (this.cache[cacheKey]) return this.cache[cacheKey];

        try {
            const res = await fetch(`${this.apiBase}/translate/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    target_lang: lang,
                    source_lang: sourceLang
                })
            });

            if (res.ok) {
                const data = await res.json();
                if (data.status === 'success' && data.translated_text) {
                    this.cache[cacheKey] = data.translated_text;
                    return data.translated_text;
                }
            }
        } catch (err) {
            console.warn('[AgriTech i18n] Dynamic translation request failed:', err);
        }

        return text;
    }

    /**
     * Batch translation request to backend
     */
    async translateBatch(texts, targetLang = null, sourceLang = 'auto') {
        const lang = targetLang || this.currentLang;
        if (!texts || !texts.length || lang === 'en') return texts;

        try {
            const res = await fetch(`${this.apiBase}/translate/translate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    texts: texts,
                    target_lang: lang,
                    source_lang: sourceLang
                })
            });

            if (res.ok) {
                const data = await res.json();
                if (data.status === 'success' && data.translated_texts) {
                    return data.translated_texts;
                }
            }
        } catch (err) {
            console.warn('[AgriTech i18n] Batch translation request failed:', err);
        }

        return texts;
    }

    /**
     * Fetch localized dynamic blogs
     */
    async getLocalizedBlogs(lang = null) {
        const target = lang || this.currentLang;
        try {
            const res = await fetch(`${this.apiBase}/content/blogs?lang=${encodeURIComponent(target)}`);
            if (res.ok) {
                const data = await res.json();
                return data.blogs || [];
            }
        } catch (e) {
            console.warn('Failed to fetch localized blogs:', e);
        }
        return [];
    }

    /**
     * Fetch localized dynamic crops
     */
    async getLocalizedCrops(lang = null) {
        const target = lang || this.currentLang;
        try {
            const res = await fetch(`${this.apiBase}/content/crops?lang=${encodeURIComponent(target)}`);
            if (res.ok) {
                const data = await res.json();
                return data.crops || [];
            }
        } catch (e) {
            console.warn('Failed to fetch localized crops:', e);
        }
        return [];
    }

    /**
     * Fetch localized dynamic agricultural resources
     */
    async getLocalizedResources(lang = null) {
        const target = lang || this.currentLang;
        try {
            const res = await fetch(`${this.apiBase}/content/resources?lang=${encodeURIComponent(target)}`);
            if (res.ok) {
                const data = await res.json();
                return data.resources || [];
            }
        } catch (e) {
            console.warn('Failed to fetch localized resources:', e);
        }
        return [];
    }
}

// Global instance initialization
window.i18nManager = new I18nManager();

// Global wrapper functions for HTML onclick compatibility
window.setLanguage = (code, label) => {
    window.i18nManager.changeLanguage(code, label);
};

window.platformLanguageChange = (lang) => {
    window.i18nManager.changeLanguage(lang);
};

window.languagePlatformChange = window.platformLanguageChange;
window.updateContent = window.platformLanguageChange;
