console.log("i18n loaded");

let translations = {};
let currentLang = localStorage.getItem("lang") || "en";

async function loadLanguage(lang) {
  try {
    const response = await fetch(`locals/${lang}.json`);
    translations = await response.json();

    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      if (translations[key]) {
        el.innerHTML = translations[key];
      }
    });

    localStorage.setItem("lang", lang);
    updateLangLabel(lang);
  } catch (err) {
    console.error("Language load error:", err);
  }
}

function updateLangLabel(lang) {
  const labels = {
    en: "English",
    hi: "हिन्दी",
    te: "తెలుగు",
    ta: "தமிழ்"
  };
  document.getElementById("current-lang-text").innerText = labels[lang] || "English";
}

function platformLanguageChange(lang) {
  loadLanguage(lang);
}

// Load default language on page load
document.addEventListener("DOMContentLoaded", () => {
  loadLanguage(currentLang);
});
