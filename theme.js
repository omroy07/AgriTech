/**
 * AgriTech - Theme Controller & Visual Theme Toggle
 * Handles system preference detection, localStorage persistence,
 * seamless visual toggle animations between Sun (☀️) and Moon (🌙),
 * and custom themeChanged events.
 */

(function () {
  'use strict';

  const KEY = 'agritech-theme';
  const LEGACY_KEY = 'theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(KEY, theme);
      localStorage.removeItem(LEGACY_KEY);
    } catch (e) {}

    document.querySelectorAll('.theme-toggle, #themeToggle, .mobile-theme-toggle, [data-theme-toggle]').forEach(btn => {
      const label = theme === 'light' ? 'Switch to Dark Mode (🌙)' : 'Switch to Light Mode (☀️)';
      btn.setAttribute('aria-label', label);
      btn.setAttribute('title', label);
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    });

    window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
  }

  function setupToggleUI(btn) {
    if (!btn || btn.dataset.enhancedToggle) return;
    btn.dataset.enhancedToggle = 'true';

    // Inject visual toggle structure if not already present
    if (!btn.querySelector('.theme-toggle-track')) {
      btn.innerHTML = `
        <span class="theme-toggle-track">
          <span class="theme-toggle-icon sun-icon" aria-hidden="true">
            <i class="fas fa-sun"></i>
          </span>
          <span class="theme-toggle-icon moon-icon" aria-hidden="true">
            <i class="fas fa-moon"></i>
          </span>
          <span class="theme-toggle-thumb"></span>
        </span>
      `;
    }

    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      applyTheme(current === 'light' ? 'dark' : 'light');
    });
  }

  // Get initial theme preference
  let initialTheme = 'dark';
  try {
    const saved = localStorage.getItem(KEY) || localStorage.getItem(LEGACY_KEY);
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    initialTheme = saved || (prefersDark ? 'dark' : 'light');
    if (saved && !localStorage.getItem(KEY)) {
      localStorage.setItem(KEY, saved);
    }
  } catch (e) {}

  applyTheme(initialTheme);

  function initThemeButtons() {
    document.querySelectorAll('.theme-toggle, #themeToggle, .mobile-theme-toggle, [data-theme-toggle]').forEach(setupToggleUI);
    const currentTheme = document.documentElement.getAttribute('data-theme') || initialTheme;
    applyTheme(currentTheme);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThemeButtons);
  } else {
    initThemeButtons();
  }

  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      try {
        if (!localStorage.getItem(KEY)) applyTheme(e.matches ? 'dark' : 'light');
      } catch (err) {}
    });
  }

  window.themeManager = {
    setTheme: applyTheme,
    getCurrentTheme: () => document.documentElement.getAttribute('data-theme'),
    toggleTheme: () => {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      applyTheme(current === 'light' ? 'dark' : 'light');
    }
  };
})();