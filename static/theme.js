// Theme Management System
class ThemeManager {
  constructor() {
    this.currentTheme = this.getStoredTheme() || 'light';
    this.init();
  }

  init() {
    // Apply stored theme immediately
    this.applyTheme(this.currentTheme);
    
    // Create and setup toggle button
    this.createToggleButton();
    
    // Listen for system theme changes
    this.watchSystemTheme();
  }

  getStoredTheme() {
    try {
      return localStorage.getItem('agritech-theme');
    } catch (error) {
      console.warn('localStorage not available, using default theme');
      return null;
    }
  }

  setStoredTheme(theme) {
    try {
      localStorage.setItem('agritech-theme', theme);
    } catch (error) {
      console.warn('localStorage not available, theme will not persist');
    }
  }

  applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    this.currentTheme = theme;
    this.setStoredTheme(theme);
    this.updateToggleButton();
    
    // Dispatch custom event for other scripts to listen to
    window.dispatchEvent(new CustomEvent('themeChanged', { 
      detail: { theme: theme } 
    }));
  }

  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
    console.log(`Switching to ${newTheme} mode`);
    this.applyTheme(newTheme);
  }

  createToggleButton() {
    // Find existing theme toggle or create new one
    let toggleButton = document.querySelector('.theme-toggle');
    
    if (!toggleButton) {
      toggleButton = document.createElement('button');
      toggleButton.className = 'theme-toggle';
      toggleButton.setAttribute('aria-label', 'Toggle dark/light mode');
      toggleButton.setAttribute('title', 'Toggle theme');
      
      // Add icons
      toggleButton.innerHTML = `
        <i class="fas fa-sun sun-icon"></i>
        <i class="fas fa-moon moon-icon"></i>
        <span class="theme-text">Light</span>
      `;
      
      // Find the best place to insert the toggle
      this.insertToggleButton(toggleButton);
    }

    // Add click event listener
    toggleButton.addEventListener('click', () => {
      this.toggleTheme();
    });

    // Add keyboard support
    toggleButton.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.toggleTheme();
      }
    });
  }

  insertToggleButton(toggleButton) {
    // Try to find header buttons container
    const headerButtons = document.querySelector('.header-buttons');
    if (headerButtons) {
      headerButtons.appendChild(toggleButton);
      return;
    }

    // Try to find nav buttons
    const navButtons = document.querySelector('.nav-buttons');
    if (navButtons) {
      navButtons.appendChild(toggleButton);
      return;
    }

    // Try to find header content
    const headerContent = document.querySelector('.header-content');
    if (headerContent) {
      headerContent.appendChild(toggleButton);
      return;
    }

    // Try to find any header
    const header = document.querySelector('header');
    if (header) {
      header.appendChild(toggleButton);
      return;
    }

    // Try to find navbar
    const navbar = document.querySelector('.navbar');
    if (navbar) {
      navbar.appendChild(toggleButton);
      return;
    }

    // Fallback: add to body
    document.body.appendChild(toggleButton);
  }

  updateToggleButton() {
    const toggleButton = document.querySelector('.theme-toggle');
    const themeText = toggleButton?.querySelector('.theme-text');
    
    if (toggleButton && themeText) {
      themeText.textContent = this.currentTheme === 'light' ? 'Light' : 'Dark';
    }
  }

  watchSystemTheme() {
    // Listen for system theme changes
    if (window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      mediaQuery.addEventListener('change', (e) => {
        // Only auto-switch if user hasn't manually set a preference
        if (!this.getStoredTheme()) {
          this.applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    }
  }

  // Public method to get current theme
  getCurrentTheme() {
    return this.currentTheme;
  }

  // Public method to set theme programmatically
  setTheme(theme) {
    if (theme === 'light' || theme === 'dark') {
      this.applyTheme(theme);
    }
  }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.themeManager = new ThemeManager();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
}