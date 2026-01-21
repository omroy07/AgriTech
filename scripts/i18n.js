/**window.updateContent = updateContent; // This makes the 'onclick' in HTML find the function
const translations = {
    "en": { "login": "Login", "faq": "FAQ", "register": "Register", "search": "Search...", "theme_light": "Light", "theme_dark": "Dark" },
    "hi": { "login": "लॉगिन", "faq": "सामान्य प्रश्न", "register": "पंजीकरण", "search": "खोजें...", "theme_light": "रोशनी", "theme_dark": "अंधेरा" },
    "te": { "login": "లాగిన్", "faq": "ప్రశ్నలు", "register": "నమోదు", "search": "వెతకండి...", "theme_light": "కాంతి", "theme_dark": "చీకటి" },
    // Add other 7 languages following this pattern...
};

function updateContent(lang) {
    localStorage.setItem('selectedLang', lang);
    
    // Update the button text to show current language
    const langNames = { "en": "English", "hi": "हिन्दी", "te": "తెలుగు", "bn": "বাংলা", "mr": "मराठी", "ta": "தமிழ்", "gu": "ગુજરાતી", "kn": "ಕನ್ನಡ", "ml": "മലയാളം", "pa": "ਪੰਜਾਬੀ" };
    document.querySelector('.selected-lang').textContent = langNames[lang];

    // Update all elements with [data-i18n]
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            if (element.tagName === 'INPUT') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
}

window.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('selectedLang') || 'en';
    updateContent(savedLang);
});**/

// 1. Ensure the function is global so 'onclick' can find it
/*window.updateContent = function(lang) {
    // 2. Save preference to LocalStorage
    localStorage.setItem('selectedLang', lang);
    
    // 3. Update the dropdown button's display text
    const langNames = {
        "en": "English", "hi": "हिन्दी", "bn": "বাংলা", "te": "తెలుగు", 
        "mr": "मराठी", "ta": "தமிழ்", "gu": "ગુજરાતી", "kn": "ಕನ್ನಡ", 
        "ml": "മലയാളം", "pa": "ਪੰਜਾਬੀ"
    };
    const selectedSpan = document.querySelector('.selected-lang');
    if (selectedSpan) selectedSpan.textContent = langNames[lang];

    // 4. Swap all text on the page with [data-i18n] attributes
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            // Handle placeholders for inputs (like search)
            if (el.tagName === 'INPUT') {
                el.placeholder = translations[lang][key];
            } else {
                el.textContent = translations[lang][key];
            }
        }
    });
};

// 5. Load the saved language automatically when the page opens
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('selectedLang') || 'en';
    window.updateContent(savedLang);
});*/

// ATTACH TO WINDOW SO HTML ONCLICK CAN FIND IT
/*window.updateContent = function(lang) {
    console.log("Switching to: " + lang); // This helps you debug in the console
    
    // 1. Save to LocalStorage
    localStorage.setItem('selectedLang', lang);
    
    // 2. Update the Globe Button text immediately
    const langNames = {
        "en": "English", "hi": "हिन्दी", "bn": "বাংলা", "te": "తెలుగు", 
        "mr": "मराठी", "ta": "தமிழ்", "gu": "ગુજરાતી", "kn": "ಕನ್ನಡ", 
        "ml": "മലയാളം", "pa": "ਪੰਜਾਬੀ"
    };
    
    const label = document.querySelector('.selected-lang');
    if (label) label.textContent = langNames[lang];

    // 3. The Actual Translation Swap
    // Ensure 'translations' object is defined above or in a separate file
    if (typeof translations !== 'undefined') {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                if (el.tagName === 'INPUT') {
                    el.placeholder = translations[lang][key];
                } else {
                    el.textContent = translations[lang][key];
                }
            }
        });
    }
};

// Auto-run on load
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('selectedLang') || 'en';
    window.updateContent(saved);
});*/

// Add this at the top of i18n.js
/*window.updateContent = function(lang) {
    // Save to browser memory
    localStorage.setItem('selectedLang', lang);
    
    // Update the button label (e.g., change 'English' to 'हिन्दी')
    const langNames = {
        "en": "English", "hi": "हिन्दी", "bn": "বাংলা", "te": "తెలుగు", 
        "mr": "मराठी", "ta": "தமிழ்", "gu": "ગુજરાતી", "kn": "ಕನ್ನಡ", 
        "ml": "മലയാളം", "pa": "ਪੰਜਾਬੀ"
    };
    document.querySelector('.selected-lang').textContent = langNames[lang];

    // Swap the text for every tagged element
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            if (el.tagName === 'INPUT') {
                el.placeholder = translations[lang][key];
            } else {
                el.textContent = translations[lang][key];
            }
        }
    });
};*/
/**
 * AgriTech i18n Engine
 * This file handles the actual swapping of text on the screen.
 */

// ATTACH TO WINDOW SO HTML ONCLICK CAN FIND IT
window.updateContent = function(lang) {
    console.log("i18n Engine: Attempting to switch to " + lang);
    
    // 1. Save to LocalStorage
    localStorage.setItem('selectedLang', lang);
    
    // 2. Update the Globe Button label
    const langNames = {
        "en": "English", "hi": "हिन्दी", "bn": "বাংলা", "te": "తెలుగు", 
        "mr": "मराठी", "ta": "தமிழ்", "gu": "ગુજરાતી", "kn": "ಕನ್ನಡ", 
        "ml": "മലയാളം", "pa": "ਪੰਜਾਬੀ"
    };
    
    const label = document.querySelector('.selected-lang');
    if (label) label.textContent = langNames[lang];

    // 3. The Translation Swap (Checking window scope)
    if (typeof window.translations !== 'undefined') {
        const langData = window.translations[lang];
        if (langData) {
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (langData[key]) {
                    if (el.tagName === 'INPUT') {
                        el.placeholder = langData[key];
                    } else {
                        el.textContent = langData[key];
                    }
                }
            });
        }
    } else {
        console.error("Click Error: window.translations data is not loaded.");
    }
};

// Auto-run on load
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('selectedLang') || 'en';
    setTimeout(() => window.updateContent(saved), 50);
});
// This forces the click to work even if 'onclick' is blocked
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('lang-option')) {
        const lang = e.target.getAttribute('onclick').match(/'([^']+)'/)[1];
        console.log("Forced Listener: Switching to " + lang);
        window.updateContent(lang);
    }
});