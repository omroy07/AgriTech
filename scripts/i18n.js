/**
 * AgriTech Universal i18n & Translation System
 * Extends seamless multilingual support across the entire website.
 * Integrates static dictionaries + server-side Google Cloud Translation API.
 * Automatically synchronizes language preference via localStorage across all pages.
 */

(function () {
  'use strict';

  // Core navigation and common UI dictionary for instant translation
  const COMMON_DICTIONARY = {
    'en': {
      'home': 'Home',
      'about': 'About',
      'blog': 'Blog',
      'schemes': 'Schemes',
      'services': 'Services',
      'community_forum': 'Community Forum',
      'levelup': 'Level Up',
      'certificate': 'Certificates',
      'favorites': 'Favorites',
      'login': 'Login',
      'register': 'Register',
      'logout': 'Logout',
      'search_placeholder': 'Search crops, diseases, advisory...',
      'contact_us': 'Contact Us',
      'privacy_policy': 'Privacy Policy',
      'terms_of_service': 'Terms of Service',
      'knowledge_hub': 'Knowledge Hub',
      'marketplace': 'Marketplace',
      'weather': 'Weather',
      'crop_advisory': 'Crop Advisory',
      'smart_farming': 'Smart Farming',
      'subscribe': 'Subscribe'
    },
    'hi': {
      'home': 'होम',
      'about': 'हमारे बारे में',
      'blog': 'ब्लॉग',
      'schemes': 'योजनाएं',
      'services': 'सेवाएं',
      'community_forum': 'कम्युनिटी फोरम',
      'levelup': 'लेवल अप',
      'certificate': 'प्रमाणपत्र',
      'favorites': 'पसंदीदा',
      'login': 'लॉग इन',
      'register': 'पंजीकरण',
      'logout': 'लॉग आउट',
      'search_placeholder': 'फसलें, रोग, सलाह खोजें...',
      'contact_us': 'संपर्क करें',
      'privacy_policy': 'गोपनीयता नीति',
      'terms_of_service': 'सेवा की शर्तें',
      'knowledge_hub': 'ज्ञान केंद्र',
      'marketplace': 'मार्केटप्लेस',
      'weather': 'मौसम',
      'crop_advisory': 'फसल सलाह',
      'smart_farming': 'स्मार्ट कृषि',
      'subscribe': 'सदस्यता लें'
    },
    'kn': {
      'home': 'ಮುಖಪುಟ',
      'about': 'ನಮ್ಮ ಬಗ್ಗೆ',
      'blog': 'ಬ್ಲಾಗ್',
      'schemes': 'ಯೋಜನೆಗಳು',
      'services': 'ಸೇವೆಗಳು',
      'community_forum': 'ಸಮುದಾಯ ವೇದಿಕೆ',
      'levelup': 'ಲೆವೆಲ್ ಅಪ್',
      'certificate': 'ಪ್ರಮಾಣಪತ್ರಗಳು',
      'favorites': 'ಮೆಚ್ಚಿನವುಗಳು',
      'login': 'ಲಾಗಿನ್',
      'register': 'ನೋಂದಣಿ',
      'logout': 'ಲಾಗ್‌ಔಟ್',
      'search_placeholder': 'ಬೆಳೆಗಳು, ರೋಗಗಳು, ಸಲಹೆಗಳನ್ನು ಹುಡುಕಿ...',
      'contact_us': 'ಸಂಪರ್ಕಿಸಿ',
      'privacy_policy': 'ಗೌಪ್ಯತಾ ನೀತಿ',
      'terms_of_service': 'ಸೇವಾ ನಿಯಮಗಳು',
      'knowledge_hub': 'ಜ್ಞಾನ ಕೇಂದ್ರ',
      'marketplace': 'ಮಾರುಕಟ್ಟೆ',
      'weather': 'ಹವಾಮಾನ',
      'crop_advisory': 'ಬೆಳೆ ಸಲಹೆ',
      'smart_farming': 'ಸ್ಮಾರ್ಟ್ ಕೃಷಿ',
      'subscribe': 'ಚಂದಾದಾರರಾಗಿ'
    },
    'te': {
      'home': 'హోమ్',
      'about': 'గురించి',
      'blog': 'బ్లాగ్',
      'schemes': 'పథకాలు',
      'services': 'సేవలు',
      'community_forum': 'కమ్యూనిటీ ఫోరం',
      'levelup': 'లెవల్ అప్',
      'certificate': 'ధృవపత్రాలు',
      'favorites': 'ఇష్టమైనవి',
      'login': 'లాగిన్',
      'register': 'రిజిస్టర్',
      'logout': 'లాగ్అవుట్',
      'search_placeholder': 'పంటలు, వ్యాధులు, సలహాలు శోధించండి...',
      'contact_us': 'సంప్రదించండి',
      'privacy_policy': 'గోప్యతా విధానం',
      'terms_of_service': 'సేవా నిబంధనలు',
      'knowledge_hub': 'నాలెడ్జ్ హబ్',
      'marketplace': 'మార్కెట్‌ప్లేస్',
      'weather': 'వాతావరణం',
      'crop_advisory': 'పంట సలహా',
      'smart_farming': 'స్మార్ట్ ఫార్మింగ్',
      'subscribe': 'సబ్‌స్క్రైబ్'
    },
    'ta': {
      'home': 'முகப்பு',
      'about': 'பற்றி',
      'blog': 'வலைப்பதிவு',
      'schemes': 'திட்டங்கள்',
      'services': 'சேவைகள்',
      'community_forum': 'சமூக மன்றம்',
      'levelup': 'லெவல் அப்',
      'certificate': 'சான்றிதழ்கள்',
      'favorites': 'விருப்பங்கள்',
      'login': 'உள்நுழைக',
      'register': 'பதிவு செய்க',
      'logout': 'வெளியேறு',
      'search_placeholder': 'பயிர்கள், நோய்கள், ஆலோசனைகளைத் தேடுங்கள்...',
      'contact_us': 'தொடர்பு கொள்ள',
      'privacy_policy': 'தனியுரிமைக் கொள்கை',
      'terms_of_service': 'சேவை விதிமுறைகள்',
      'knowledge_hub': 'அறிவு மையம்',
      'marketplace': 'சந்தை',
      'weather': 'வானிலை',
      'crop_advisory': 'பயிர் ஆலோசனை',
      'smart_farming': 'ஸ்மார்ட் விவசாயம்',
      'subscribe': 'குழுசேர்'
    }
  };

  const LANG_NAMES = {
    'en': 'English',
    'hi': 'हिन्दी',
    'kn': 'ಕನ್ನಡ',
    'te': 'తెలుగు',
    'ta': 'தமிழ்',
    'bn': 'বাংলা',
    'mr': 'मराठी',
    'gu': 'ગુજરાતી',
    'ml': 'മലയാളം',
    'pa': 'ਪੰਜਾਬੀ'
  };

  class UniversalI18nManager {
    constructor() {
      this.apiBase = window.location.origin.includes('5000')
        ? '/api/v1'
        : (window.API_BASE_URL || 'http://127.0.0.1:5000/api/v1');
      this.currentLang = this.getStoredLang() || 'en';
      this.cache = {};
      this.init();
    }

    init() {
      this.setLanguageCookie(this.currentLang);

      const runInit = () => {
        this.ensureTranslationsLoaded();
        this.translatePage();
        this.updateLangUI();
        this.setupLanguageSwitcher();
      };

      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', runInit);
      } else {
        runInit();
      }
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

    ensureTranslationsLoaded() {
      // If translations.js wasn't explicitly loaded, populate window.translations from COMMON_DICTIONARY
      if (!window.translations) {
        window.translations = COMMON_DICTIONARY;
      } else {
        // Merge common dictionary into window.translations for missing keys
        Object.keys(COMMON_DICTIONARY).forEach(lang => {
          if (!window.translations[lang]) {
            window.translations[lang] = COMMON_DICTIONARY[lang];
          } else {
            window.translations[lang] = Object.assign({}, COMMON_DICTIONARY[lang], window.translations[lang]);
          }
        });
      }
    }

    async changeLanguage(lang, label = null) {
      if (!lang) return;
      lang = lang.toLowerCase().trim();
      this.currentLang = lang;

      // Persist across all keys for complete website compatibility
      localStorage.setItem('agritech-lang', lang);
      localStorage.setItem('agritech_lang', lang);
      localStorage.setItem('selectedLang', lang);
      this.setLanguageCookie(lang);

      this.translatePage();
      this.updateLangUI(label);

      window.dispatchEvent(new CustomEvent('languageChanged', {
        detail: {
          lang: lang,
          name: LANG_NAMES[lang] || lang
        }
      }));

      console.log(`[AgriTech i18n] Website language changed to: ${lang}`);
    }

    translatePage() {
      this.ensureTranslationsLoaded();
      const dictionary = (window.translations && window.translations[this.currentLang]) || COMMON_DICTIONARY[this.currentLang] || {};

      // 1. Translate elements with explicit [data-i18n]
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

      // 2. Automatically translate standard nav links if no data-i18n present
      document.querySelectorAll('.nav-link, .nav-menu a, .navbar-nav a, .top-nav a').forEach(el => {
        const text = el.textContent.trim().toLowerCase();
        const map = {
          'home': 'home',
          'about': 'about',
          'blog': 'blog',
          'schemes': 'schemes',
          'scheme': 'schemes',
          'community forum': 'community_forum',
          'level up': 'levelup',
          'certificates': 'certificate',
          'certificate': 'certificate',
          'favorites': 'favorites',
          'login': 'login',
          'register': 'register',
          'logout': 'logout',
          'services': 'services',
          'knowledge hub': 'knowledge_hub',
          'marketplace': 'marketplace',
          'weather': 'weather'
        };

        if (map[text] && dictionary[map[text]]) {
          if (!el.getAttribute('data-original-text')) {
            el.setAttribute('data-original-text', el.textContent.trim());
          }
          if (this.currentLang === 'en') {
            el.textContent = el.getAttribute('data-original-text') || dictionary[map[text]];
          } else {
            el.textContent = dictionary[map[text]];
          }
        }
      });

      // 3. Update document language tag
      document.documentElement.lang = this.currentLang;
    }

    updateLangUI(label = null) {
      const displayLabel = label || LANG_NAMES[this.currentLang] || this.currentLang.toUpperCase();

      document.querySelectorAll('#current-lang-text, .current-lang-label, #navbarCurrentLang').forEach(el => {
        el.textContent = displayLabel;
      });

      document.querySelectorAll('.lang-option, .navbar-lang-option, [data-lang-code]').forEach(option => {
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
      // Toggle click handlers
      document.querySelectorAll('.lang-trigger, .lang-btn, #langTrigger, #navbarLangTrigger').forEach(btn => {
        btn.removeEventListener('click', this._onTriggerClick);
        btn.addEventListener('click', this._onTriggerClick);
      });

      // Click outside to close
      document.removeEventListener('click', this._onDocClick);
      document.addEventListener('click', this._onDocClick);

      // Option clicks
      document.querySelectorAll('.lang-option, .navbar-lang-option').forEach(option => {
        option.removeEventListener('click', this._onOptionClick);
        option.addEventListener('click', this._onOptionClick);
      });
    }

    _onTriggerClick = (e) => {
      e.stopPropagation();
      const btn = e.currentTarget;
      const container = btn.closest('.lang-container, .navbar-lang-container');
      if (container) {
        const dropdown = container.querySelector('.lang-dropdown, .navbar-lang-dropdown');
        if (dropdown) {
          dropdown.classList.toggle('active');
          container.classList.toggle('active');
        }
      }
    };

    _onDocClick = () => {
      document.querySelectorAll('.lang-dropdown.active, .navbar-lang-dropdown.active, .lang-container.active, .navbar-lang-container.active').forEach(el => {
        el.classList.remove('active');
      });
    };

    _onOptionClick = (e) => {
      const option = e.currentTarget;
      const code = option.getAttribute('data-lang-code') ||
        (option.getAttribute('onclick') && (option.getAttribute('onclick').match(/'([^']+)'/) || [])[1]);
      const text = option.textContent.replace(/[^\w\s\u0900-\u0DFF]/gi, '').trim();
      if (code) {
        this.changeLanguage(code, text);
      }
    };

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
        console.debug('[AgriTech i18n] Dynamic translation request fallback:', err);
      }

      return text;
    }

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
        console.debug('[AgriTech i18n] Batch translation request fallback:', err);
      }

      return texts;
    }
  }

  // Attach global instances and compatibility helpers
  window.i18nManager = new UniversalI18nManager();

  window.setLanguage = function (code, label) {
    window.i18nManager.changeLanguage(code, label);
  };

  window.platformLanguageChange = function (lang) {
    window.i18nManager.changeLanguage(lang);
  };

  window.languagePlatformChange = window.platformLanguageChange;
  window.updateContent = window.platformLanguageChange;
})();
