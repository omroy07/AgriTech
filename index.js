// DOM Elements
const yearEl = document.querySelector(".current-year");
if (yearEl) {
  yearEl.textContent = new Date().getFullYear();
}

const hamburgerBtn = document.getElementById('hamburgerBtn');
const mobileMenu = document.querySelector('.mobile-menu');
const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
const mobileThemeToggle = document.getElementById('mobileThemeToggle');
const mobileServicesToggle = document.getElementById('mobileServicesToggle');
const mobileServicesList = document.getElementById('mobileServicesList');
const themeToggle = document.querySelector('.theme-toggle');
const themeText = document.querySelector('.theme-text');
const sunIcon = document.querySelector('.sun-icon');
const moonIcon = document.querySelector('.moon-icon');
const scrollBtn = document.getElementById('scrollBtn');
const scrollIcon = document.getElementById('scrollIcon');


// Theme Management
const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    if (theme === 'dark') {
        if (themeText) themeText.textContent = 'Light';
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'inline-block';
    } else {
        if (themeText) themeText.textContent = 'Dark';
        if (moonIcon) moonIcon.style.display = 'inline-block';
        if (sunIcon) sunIcon.style.display = 'none';
    }
};

const savedTheme = localStorage.getItem('theme') || 'dark';
applyTheme(savedTheme);

// Desktop Theme Toggle
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
    });
}

// Mobile Theme Toggle
if (mobileThemeToggle) {
    mobileThemeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
    });
}

// Mobile Menu Functions
function openMobileMenu() {
    if (hamburgerBtn) hamburgerBtn.classList.add('active');
    if (mobileMenu) mobileMenu.classList.add('active');
    if (mobileMenuOverlay) mobileMenuOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMobileMenu() {
    if (hamburgerBtn) hamburgerBtn.classList.remove('active');
    if (mobileMenu) mobileMenu.classList.remove('active');
    if (mobileMenuOverlay) mobileMenuOverlay.classList.remove('active');
    document.body.style.overflow = '';
    
    // Close services dropdown if open
    if (mobileServicesList && mobileServicesList.classList.contains('active')) {
        mobileServicesList.classList.remove('active');
        const mobileServicesArrow = document.querySelector('.mobile-services-toggle .services-arrow');
        if (mobileServicesArrow) {
            mobileServicesArrow.classList.remove('rotated');
        }
    }
}

// Hamburger Menu Toggle
if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (hamburgerBtn.classList.contains('active')) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });
}

// Close menu when clicking overlay
if (mobileMenuOverlay) {
    mobileMenuOverlay.addEventListener('click', closeMobileMenu);
}

// Close menu when clicking links
const mobileLinks = document.querySelectorAll('.mobile-menu a:not(.mobile-services-toggle)');
mobileLinks.forEach(link => {
    link.addEventListener('click', closeMobileMenu);
});

// Mobile Services Toggle
if (mobileServicesToggle && mobileServicesList) {
    mobileServicesToggle.addEventListener('click', (e) => {
        e.preventDefault();
        mobileServicesList.classList.toggle('active');
        const arrow = mobileServicesToggle.querySelector('.services-arrow');
        if (arrow) {
            arrow.classList.toggle('rotated');
        }
    });
}

// Desktop Services Toggle
const servicesToggle = document.querySelector('.services-toggle');
const servicesDropdown = document.querySelector('.services-dropdown');
const servicesArrow = document.querySelector('.services-arrow');

if (servicesToggle && servicesDropdown && servicesArrow) {
    servicesToggle.addEventListener('click', (event) => {
        event.stopPropagation();
        servicesDropdown.classList.toggle('active');
        servicesArrow.classList.toggle('rotated');
    });

    document.addEventListener('click', (e) => {
        const container = document.querySelector('.services-toggle-container');
        if (container && !container.contains(e.target) && servicesDropdown.classList.contains('active')) {
            servicesDropdown.classList.remove('active');
            servicesArrow.classList.remove('rotated');
        }
    });
}

// Scroll Button
if (scrollBtn && scrollIcon) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 300) {
            scrollBtn.classList.add('visible');
            scrollIcon.classList.remove("fa-arrow-down");
            scrollIcon.classList.add("fa-arrow-up");
        } else {
            scrollBtn.classList.remove('visible');
            scrollIcon.classList.remove("fa-arrow-up");
            scrollIcon.classList.add("fa-arrow-down");
        }
    });

    scrollBtn.addEventListener("click", () => {
        if (scrollIcon.classList.contains("fa-arrow-up")) {
            window.scrollTo({top: 0, behavior: "smooth"});
        } else {
            window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});
        }
    });
}

// Mobile Search
const mobileSearchInput = document.querySelector('.mobile-search-input');
if (mobileSearchInput) {
    mobileSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            alert('Searching for: ' + mobileSearchInput.value);
            closeMobileMenu();
        }
    });
}

// Close menu on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
        closeMobileMenu();
    }
});

// Close menu on window resize (if resized to desktop size)
window.addEventListener('resize', () => {
    if (window.innerWidth > 1024 && mobileMenu && mobileMenu.classList.contains('active')) {
        closeMobileMenu();
    }
});

// Initialize Three.js animation
function initThreeJS() {
    // Your Three.js code here
}