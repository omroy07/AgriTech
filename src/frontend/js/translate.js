import languages from "./languages.js";

export function translatePage() {
  const lang = localStorage.getItem("lang") || "en";

  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (languages[lang] && languages[lang][key]) {
      el.innerText = languages[lang][key];
    }
  });
}
