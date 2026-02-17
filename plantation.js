// ===================================
// SCROLL PROGRESS INDICATOR
// ===================================
window.addEventListener("scroll", () => {
  const scrollIndicator = document.getElementById("scrollIndicator");
  const scrollTop = document.documentElement.scrollTop;
  const scrollHeight =
    document.documentElement.scrollHeight -
    document.documentElement.clientHeight;
  const scrollPercent = (scrollTop / scrollHeight) * 100;
  scrollIndicator.style.width = scrollPercent + "%";

  // Update sidebar progress
  updateProgress();
});

// ===================================
// TAB NAVIGATION SYSTEM
// ===================================
const tabs = document.querySelectorAll('.tab-btn');
const panels = document.querySelectorAll('.tab-panel');

// Initialize tabs
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => {
    switchTab(tab.dataset.tab);
  });

  // Keyboard navigation for tabs
  tab.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      const nextTab = tabs[Math.min(index + 1, tabs.length - 1)];
      nextTab.focus();
      switchTab(nextTab.dataset.tab);
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      const prevTab = tabs[Math.max(index - 1, 0)];
      prevTab.focus();
      switchTab(prevTab.dataset.tab);
    }
  });
});

function switchTab(tabName) {
  // Remove active state from all tabs and panels
  tabs.forEach(tab => {
    tab.classList.remove('active');
    tab.setAttribute('aria-selected', 'false');
  });

  panels.forEach(panel => {
    panel.classList.remove('active');
  });

  // Add active state to selected tab and panel
  const selectedTab = document.querySelector(`[data-tab="${tabName}"]`);
  const selectedPanel = document.getElementById(`panel-${tabName}`);

  if (selectedTab && selectedPanel) {
    selectedTab.classList.add('active');
    selectedTab.setAttribute('aria-selected', 'true');
    selectedPanel.classList.add('active');

    // Smooth scroll to content
    setTimeout(() => {
      selectedPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Update URL hash without jumping
    history.pushState(null, null, `#${tabName}`);

    // Update quick navigation
    updateQuickNav();
  }
}

// Handle deep linking from URL hash
window.addEventListener('DOMContentLoaded', () => {
  const hash = window.location.hash.substring(1);
  if (hash) {
    // Map old section IDs to new tab names
    const hashMap = {
      'research-development': 'research',
      'soil-preparation': 'soil',
      'seed-sowing': 'sowing',
      'irrigation-fertilization': 'irrigation',
      'pest-disease-management': 'pest',
      'harvesting': 'harvest',
      'post-harvest': 'postharvest'
    };
    const tabName = hashMap[hash] || hash;
    switchTab(tabName);
  }
});

// ===================================
// CARD EXPAND/COLLAPSE
// ===================================
function toggleCard(button) {
  const card = button.closest('.info-card');
  const content = card.querySelector('.card-content');
  const isExpanded = card.classList.contains('expanded');

  if (isExpanded) {
    card.classList.remove('expanded');
    content.style.maxHeight = '0';
    button.querySelector('span').textContent = 'Read More';
    button.querySelector('i').style.transform = 'rotate(0deg)';
    button.setAttribute('aria-expanded', 'false');
  } else {
    card.classList.add('expanded');
    content.style.maxHeight = content.scrollHeight + 'px';
    button.querySelector('span').textContent = 'Show Less';
    button.querySelector('i').style.transform = 'rotate(180deg)';
    button.setAttribute('aria-expanded', 'true');

    // Smooth scroll to card if needed
    setTimeout(() => {
      const cardTop = card.getBoundingClientRect().top + window.scrollY;
      const offset = 100; // Offset for header
      if (window.scrollY > cardTop - offset) {
        window.scrollTo({ top: cardTop - offset, behavior: 'smooth' });
      }
    }, 300);
  }
}

// Initialize card buttons with ARIA attributes
document.querySelectorAll('.expand-btn').forEach(btn => {
  btn.setAttribute('aria-expanded', 'false');
  btn.setAttribute('aria-controls', btn.closest('.info-card').querySelector('.card-content').id || 'card-content');
});

// ===================================
// PROGRESS TRACKING
// ===================================
function updateProgress() {
  const activePanel = document.querySelector('.tab-panel.active');
  if (!activePanel) return;

  const cards = activePanel.querySelectorAll('.info-card');
  const expandedCards = activePanel.querySelectorAll('.info-card.expanded');
  const progressPercent = cards.length > 0 ? Math.round((expandedCards.length / cards.length) * 100) : 0;

  const progressBar = document.getElementById('progressBar');
  const progressText = document.getElementById('progressPercent');

  if (progressBar && progressText) {
    progressBar.style.width = progressPercent + '%';
    progressText.textContent = progressPercent;
  }
}

// Update progress when cards are toggled
document.addEventListener('click', (e) => {
  if (e.target.closest('.expand-btn')) {
    setTimeout(updateProgress, 300);
  }
});

// ===================================
// QUICK NAVIGATION SIDEBAR
// ===================================
function updateQuickNav() {
  const activePanel = document.querySelector('.tab-panel.active');
  const quickNavList = document.getElementById('quickNavList');

  if (!activePanel || !quickNavList) return;

  // Clear existing items
  quickNavList.innerHTML = '';

  // Get all cards in active panel
  const cards = activePanel.querySelectorAll('.info-card');

  cards.forEach((card, index) => {
    const cardTitle = card.querySelector('h3').textContent;
    const li = document.createElement('li');
    const a = document.createElement('a');

    a.href = '#';
    a.textContent = cardTitle;
    a.addEventListener('click', (e) => {
      e.preventDefault();
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // Auto-expand card if not expanded
      if (!card.classList.contains('expanded')) {
        const expandBtn = card.querySelector('.expand-btn');
        if (expandBtn) expandBtn.click();
      }
    });

    li.appendChild(a);
    quickNavList.appendChild(li);
  });
}

// Initialize quick nav on page load
window.addEventListener('DOMContentLoaded', () => {
  updateQuickNav();
});

// ===================================
// SCROLL TO TOP BUTTON
// ===================================
const scrollTopBtn = document.getElementById('scrollTopBtn');
const scrollThreshold = 250; // px

const toggleScrollTopBtn = () => {
  const scrollY = window.scrollY || document.documentElement.scrollTop;
  if (scrollY > scrollThreshold) {
    scrollTopBtn.classList.add('show');
  } else {
    scrollTopBtn.classList.remove('show');
  }
};

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
  const header = document.querySelector('header');
  if (header) {
    header.setAttribute('tabindex', '-1');
    header.focus();
  }
};

window.addEventListener('scroll', toggleScrollTopBtn, { passive: true });
if (scrollTopBtn) {
  scrollTopBtn.addEventListener('click', scrollToTop);
}

// ===================================
// MOBILE TAB SWIPE GESTURES
// ===================================
let touchStartX = 0;
let touchEndX = 0;

const tabNav = document.querySelector('.tab-navigation');

if (tabNav && 'ontouchstart' in window) {
  tabNav.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  tabNav.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  }, { passive: true });
}

function handleSwipe() {
  const swipeThreshold = 50;
  const diff = touchStartX - touchEndX;

  if (Math.abs(diff) < swipeThreshold) return;

  const activeTab = document.querySelector('.tab-btn.active');
  const allTabs = Array.from(tabs);
  const currentIndex = allTabs.indexOf(activeTab);

  if (diff > 0 && currentIndex < allTabs.length - 1) {
    // Swipe left - next tab
    switchTab(allTabs[currentIndex + 1].dataset.tab);
  } else if (diff < 0 && currentIndex > 0) {
    // Swipe right - previous tab
    switchTab(allTabs[currentIndex - 1].dataset.tab);
  }
}

// ===================================
// HORIZONTAL TAB SCROLL
// ===================================
function initTabScroll() {
  const tabNavWrapper = document.querySelector('.tab-navigation-wrapper');
  const tabNavigation = document.querySelector('.tab-navigation');

  if (!tabNavWrapper || !tabNavigation) return;

  // Check if tabs overflow
  if (tabNavigation.scrollWidth > tabNavWrapper.clientWidth) {
    tabNavWrapper.classList.add('scrollable');

    // Scroll active tab into view
    const activeTab = document.querySelector('.tab-btn.active');
    if (activeTab) {
      activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
  }
}

window.addEventListener('DOMContentLoaded', initTabScroll);
window.addEventListener('resize', initTabScroll);

// Scroll active tab into view when switching
const originalSwitchTab = switchTab;
switchTab = function(tabName) {
  originalSwitchTab(tabName);
  const activeTab = document.querySelector('.tab-btn.active');
  if (activeTab) {
    setTimeout(() => {
      activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }, 100);
  }
};

// ===================================
// LOCAL STORAGE FOR READING POSITION
// ===================================
function saveReadingPosition() {
  const activeTab = document.querySelector('.tab-btn.active');
  if (activeTab) {
    localStorage.setItem('agritech_last_tab', activeTab.dataset.tab);
  }

  // Save expanded cards
  const expandedCards = [];
  document.querySelectorAll('.info-card.expanded').forEach(card => {
    const cardId = card.querySelector('h3').textContent;
    expandedCards.push(cardId);
  });
  localStorage.setItem('agritech_expanded_cards', JSON.stringify(expandedCards));
}

function restoreReadingPosition() {
  const lastTab = localStorage.getItem('agritech_last_tab');
  if (lastTab && !window.location.hash) {
    switchTab(lastTab);
  }

  // Restore expanded cards
  setTimeout(() => {
    const expandedCards = JSON.parse(localStorage.getItem('agritech_expanded_cards') || '[]');
    expandedCards.forEach(cardTitle => {
      const card = Array.from(document.querySelectorAll('.info-card')).find(c => 
        c.querySelector('h3').textContent === cardTitle
      );
      if (card && !card.classList.contains('expanded')) {
        const expandBtn = card.querySelector('.expand-btn');
        if (expandBtn) expandBtn.click();
      }
    });
  }, 500);
}

// Save position before leaving page
window.addEventListener('beforeunload', saveReadingPosition);

// Restore position on load (optional - can be disabled)
// window.addEventListener('DOMContentLoaded', restoreReadingPosition);

// ===================================
// PERFORMANCE OPTIMIZATION
// ===================================
// Debounce scroll events
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Debounced scroll handler
const debouncedScroll = debounce(() => {
  updateProgress();
}, 100);

window.addEventListener('scroll', debouncedScroll, { passive: true });

// ===================================
// ACCESSIBILITY ENHANCEMENTS
// ===================================
// Announce tab changes to screen readers
function announceTabChange(tabName) {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', 'polite');
  announcement.className = 'sr-only';
  announcement.textContent = `Switched to ${tabName} section`;
  document.body.appendChild(announcement);
  setTimeout(() => announcement.remove(), 1000);
}

// Add screen reader only class
const style = document.createElement('style');
style.textContent = `
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0,0,0,0);
    white-space: nowrap;
    border: 0;
  }
`;
document.head.appendChild(style);

// ===================================
// RESOURCE DOWNLOAD HANDLERS
// ===================================
document.querySelectorAll('.resource-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const resourceType = link.querySelector('span').textContent;
    console.log(`Download ${resourceType} - Implement your download logic here`);
    // Add your actual download/bookmark logic here
  });
});

// ===================================
// INITIALIZE ON DOM READY
// ===================================
document.addEventListener('DOMContentLoaded', () => {
  console.log('AgriTech Professional Interface Initialized');

  // Set initial progress
  updateProgress();

  // Smooth scroll for all internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href !== '#' && href.length > 1) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });
});
// --- Cursor Trailing Effect ---
const container = document.getElementById('cursorTrail');
const circleCount = 12;
const circles = [];

let mouseX = 0;
let mouseY = 0;

// Create circles
for (let i = 0; i < circleCount; i++) {
    const circle = document.createElement('div');
    circle.classList.add('cursor-circle');
    container.appendChild(circle);
    circles.push({ el: circle, x: 0, y: 0 });
}

// Mouse move
document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
});

// Click effects
document.addEventListener('mousedown', () => {
    circles.forEach(c => c.el.classList.add('cursor-clicking'));
});
document.addEventListener('mouseup', () => {
    circles.forEach(c => c.el.classList.remove('cursor-clicking'));
});

// Hover effects on interactive elements
document.addEventListener('mouseover', (e) => {
    if (e.target.closest('a, button, .cta-button, .service-card, .shipment-card')) {
        circles.forEach(c => c.el.classList.add('cursor-hovering'));
    }
});
document.addEventListener('mouseout', (e) => {
    if (e.target.closest('a, button, .cta-button, .service-card, .shipment-card')) {
        circles.forEach(c => c.el.classList.remove('cursor-hovering'));
    }
});

// Animate trailing effect
function animateCursor() {
    let x = mouseX;
    let y = mouseY;

    circles.forEach((circle) => {
        circle.x += (x - circle.x) * 0.25;
        circle.y += (y - circle.y) * 0.25;

        circle.el.style.left = circle.x + 'px';
        circle.el.style.top = circle.y + 'px';

        x = circle.x;
        y = circle.y;
    });

    requestAnimationFrame(animateCursor);
}
animateCursor();