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
// GLOBAL TRANSLATIONS OBJECT (ACTIVE)
window.translations = {
  en: {
    nav_home: "Home",
    nav_about: "About",
    nav_blog: "Blog",
    nav_schemes: "Schemes",
    nav_community: "Community Forum",

    hero_title: "Empowering Agriculture Through Technology",
    hero_desc: "AgriTech connects Farmers, Buyers, Equipment Suppliers, and Grocery Sellers to revolutionize India's agricultural ecosystem."
  },

  te: {
    nav_home: "హోమ్",
    nav_about: "గురించి",
    nav_blog: "బ్లాగ్",
    nav_schemes: "పథకాలు",
    nav_community: "సముదాయ వేదిక",

    hero_title: "సాంకేతికత ద్వారా వ్యవసాయాన్ని బలోపేతం చేయడం",
    hero_desc: "అగ్రిటెక్ రైతులు, కొనుగోలుదారులు, సరఫరాదారులను అనుసంధానిస్తుంది."
  },

  hi: {
    nav_home: "होम",
    nav_about: "परिचय",
    nav_blog: "ब्लॉग",
    nav_schemes: "योजनाएं",
    nav_community: "सामुदायिक मंच",

    hero_title: "प्रौद्योगिकी के माध्यम से कृषि को सशक्त बनाना",
    hero_desc: "एग्रीटेक किसानों और सेवा प्रदाताओं को जोड़ता है।"
  },
  ta: {
  nav_home: "முகப்பு",
  nav_about: "எங்களை பற்றி",
  nav_blog: "வலைப்பதிவு",
  nav_schemes: "திட்டங்கள்",
  nav_community: "சமூக மன்றம்",

  hero_title: "தொழில்நுட்பத்தின் மூலம் விவசாயத்தை வலுப்படுத்துதல்",
  hero_desc: "அக்ரிடெக் விவசாயிகள், வாங்குபவர்கள், உபகரண வழங்குநர்கள் மற்றும் மளிகை விற்பனையாளர்களை இணைக்கிறது."
}

};

window.updateContent = function(lang) {
    console.log("i18n Engine: Attempting to switch to " + lang);
    
    // 1. Save to LocalStorage
    localStorage.setItem('lang', lang);
    
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
    const saved = localStorage.getItem('lang') || 'en';
    window.updateContent(saved);
});

// This forces the click to work even if 'onclick' is blocked
