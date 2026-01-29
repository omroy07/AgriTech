/**
 * AgriTech i18n Management System
 * Handles client-side translations and serves as a bridge to the backend localization.
 */

class I18nManager {
    constructor() {
        this.currentLang = this.getStoredLang() || 'en';
        this.init();
    }

    init() {
        // Set cookie for backend language detection
        this.setLanguageCookie(this.currentLang);

        // Initial translation
        document.addEventListener('DOMContentLoaded', () => {
            this.translatePage();
            this.updateLangUI();
            this.setupLanguageSwitcher();
        });
    }

    getStoredLang() {
        // Check localStorage first (compat with old selectedLang), then cookie
        return localStorage.getItem('agritech-lang') ||
            localStorage.getItem('selectedLang') ||
            document.cookie.replace(/(?:(?:^|.*;\s*)lang\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    }

    setLanguageCookie(lang) {
        document.cookie = `lang=${lang}; path=/; max-age=31536000; SameSite=Lax`;
    }

    changeLanguage(lang) {
        // Translations come from translations.js (window.translations)
        if (!window.translations || !window.translations[lang]) {
            console.warn(`Language ${lang} not found in window.translations. Falling back to key.`);
        }

        this.currentLang = lang;
        localStorage.setItem('agritech-lang', lang);
        localStorage.setItem('selectedLang', lang); // Maintain compat
        this.setLanguageCookie(lang);

        // Update UI
        this.translatePage();
        this.updateLangUI();

        // Notify other components
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: lang } }));

        console.log(`Language switched to: ${lang}`);
    }

    translatePage() {
        if (!window.translations) {
            console.error("Translations data (translations.js) missing!");
            return;
        }

        const translations = window.translations[this.currentLang];
        if (!translations) return;

        // Translate elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (translations[key]) {
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    el.placeholder = translations[key];
                } else {
                    el.textContent = translations[key];
                }
            }
        });

        // Update document lang attribute
        document.documentElement.lang = this.currentLang;
    }

    updateLangUI() {
        const langText = document.getElementById('current-lang-text');
        if (langText) {
            const langNames = {
                'en': 'English', 'hi': 'हिन्दी', 'bn': 'বাংলা', 'te': 'తెలుగు',
                'mr': 'मराठी', 'ta': 'தமிழ்', 'gu': 'ગુજરાતી', 'kn': 'ಕನ್ನಡ',
                'ml': 'മലയാളം', 'pa': 'ਪੰਜਾਬੀ'
            };
            langText.textContent = langNames[this.currentLang] || this.currentLang.toUpperCase();
        }
    }

    setupLanguageSwitcher() {
        const langBtn = document.querySelector('.lang-btn');
        const langDropdown = document.querySelector('.lang-dropdown');

        if (langBtn && langDropdown) {
            langBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                langDropdown.classList.toggle('active');
            });

            document.addEventListener('click', () => {
                langDropdown.classList.remove('active');
            });
        }

        // Handle dropdown clicks for robustness
        document.querySelectorAll('.lang-option').forEach(option => {
            option.addEventListener('click', (e) => {
                // Extract lang code from onclick if present, or just use hardcoded ones
                const onclick = option.getAttribute('onclick');
                if (onclick) {
                    const match = onclick.match(/'([^']+)'/);
                    if (match) {
                        this.changeLanguage(match[1]);
                    }
                }
            });
        });
    }
}

// Global initialization
window.i18nManager = new I18nManager();

// Bridge for the onclick attributes in HTML
window.platformLanguageChange = (lang) => {
    window.i18nManager.changeLanguage(lang);
};

// Fix for legacy or typos
window.languagePlatformChange = window.platformLanguageChange;
window.updateContent = window.platformLanguageChange;