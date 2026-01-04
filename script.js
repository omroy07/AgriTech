document.addEventListener("DOMContentLoaded", function () {
  // --- Homepage Search Functionality ---
  const liveSuggestList = document.querySelector('.live-suggest-list');
  const searchInput = document.querySelector('.search-input');
  const searchButton = document.querySelector('.search-button');
  const featureCards = document.querySelectorAll('.feature-card');
  const heroContent = document.querySelector('.hero-content');
  const ctaContent = document.querySelector('.cta-content');
  const sitePages = [
    { name: 'About', keywords: ['about', 'team', 'mission', 'info', 'company', 'us', 'who', 'profile', 'history', 'vision', 'values'], url: 'about.html' },
    { name: 'Blog', keywords: ['blog', 'news', 'articles', 'updates', 'stories', 'events', 'announcements', 'tips', 'insights'], url: 'blog.html' },
    { name: 'FAQ', keywords: ['faq', 'questions', 'help', 'support', 'answers', 'common', 'doubts', 'info', 'guide'], url: 'faq.html' },
    { name: 'Login', keywords: ['login', 'signin', 'sign in', 'account', 'dashboard', 'access', 'enter', 'user', 'portal'], url: 'login.html' },
    { name: 'Register', keywords: ['register', 'signup', 'sign up', 'create account', 'join', 'new user', 'enroll', 'start'], url: 'register.html' },
     { name: 'Crop Monitoring', keywords: ['crop', 'monitoring', 'smart crop', 'calendar', 'plan', 'field', 'growth', 'season', 'timing', 'date', 'schedule', 'observe', 'track', 'yield', 'harvest', 'product', 'products', 'technology', 'tech', 'tools', 'equipment', 'sensor', 'sensors', 'iot', 'device', 'devices', 'monitor', 'detect'], url: 'crop.html' },
  { name: 'Crop Calendar', keywords: ['calendar', 'crop', 'season', 'schedule', 'timing', 'date', 'month', 'year', 'timeline', 'planting', 'harvest', 'cycle', 'product', 'products'], url: 'cropCalendar.html' },
     { name: 'Farmer', keywords: ['farmer', 'farmers', 'farming', 'grower', 'agriculture', 'seed', 'plant', 'producer', 'rural', 'village', 'community', 'product', 'products', 'technology', 'tech', 'tools', 'equipment', 'sensor', 'sensors', 'iot', 'device', 'devices', 'monitor', 'detect'], url: 'farmer.html' },
  { name: 'Supply Chain', keywords: ['supply', 'chain', 'distribution', 'logistics', 'transport', 'delivery', 'network', 'route', 'shipment', 'product', 'products', 'technology', 'tech', 'tools', 'equipment'], url: 'supply-chain.html' },
     { name: 'Supply Chain', keywords: ['supply', 'chain', 'distribution', 'logistics', 'transport', 'delivery', 'network', 'route', 'shipment', 'product', 'products', 'technology', 'tech', 'tools', 'equipment', 'sensor', 'sensors', 'iot', 'device', 'devices', 'monitor', 'detect'], url: 'supply-chain.html' },
  { name: 'Sustainable Farming', keywords: ['sustainable', 'farming', 'eco', 'green', 'organic', 'environment', 'nature', 'earth', 'friendly', 'renewable', 'technology', 'tech', 'innovation'], url: 'sustainable-farming.html' },
  { name: 'Marketplace', keywords: ['market', 'marketplace', 'store', 'buy', 'sell', 'shop', 'purchase', 'trade', 'exchange', 'commerce', 'product', 'products', 'technology', 'tech', 'tools', 'equipment'], url: 'marketplace.html' },
    { name: 'Financial Support', keywords: ['financial', 'insurance', 'support', 'loan', 'money', 'fund', 'grant', 'aid', 'credit', 'finance'], url: 'financial-support.html' },
    { name: 'AI Assistant', keywords: ['chat', 'ai', 'assistant', 'bot', 'help', 'virtual', 'support', 'question', 'ask', 'guide'], url: 'chat.html' },
    { name: 'Contact', keywords: ['contact', 'email', 'help', 'reach', 'connect', 'call', 'message', 'query', 'inquiry'], url: 'contact.html' },
    // Add more as needed
  ];

  function normalize(text) {
    return text.toLowerCase().replace(/\s+/g, ' ').trim();
  }

  function showLiveSuggestions(query) {
    if (!query) {
      liveSuggestList.style.display = 'none';
      liveSuggestList.innerHTML = '';
      return;
    }
    const normQuery = normalize(query);
    // Fuzzy match: allow partials anywhere in name or keywords
    const suggestions = sitePages.filter(page => {
      const nameNorm = page.name.toLowerCase();
      if (nameNorm.includes(normQuery) || normQuery.includes(nameNorm)) return true;
      // Fuzzy: match if all query letters appear in order in name (e.g. agr -> agriculture)
      let i = 0, j = 0;
      while (i < normQuery.length && j < nameNorm.length) {
        if (normQuery[i] === nameNorm[j]) i++;
        j++;
      }
      if (i === normQuery.length) return true;
      // Also check keywords
      return page.keywords.some(k => {
        const kNorm = k.toLowerCase();
        if (kNorm.includes(normQuery) || normQuery.includes(kNorm)) return true;
        // Fuzzy in keyword
        let ki = 0, kj = 0;
        while (ki < normQuery.length && kj < kNorm.length) {
          if (normQuery[ki] === kNorm[kj]) ki++;
          kj++;
        }
        return ki === normQuery.length;
      });
    }).slice(0, 6);
    if (suggestions.length === 0) {
      liveSuggestList.innerHTML = `<div class="live-suggest-item" style="color:#888;cursor:default;">No results found</div>`;
      liveSuggestList.style.display = 'block';
      return;
    }
    liveSuggestList.innerHTML = suggestions.map(s => `<div class="live-suggest-item" data-url="${s.url}"><i class="fas fa-search"></i> ${s.name}</div>`).join('');
    liveSuggestList.style.display = 'block';
  }

  if (searchInput) {
    searchInput.addEventListener('input', function(e) {
      showLiveSuggestions(searchInput.value.trim());
    });
    searchInput.addEventListener('focus', function() {
      showLiveSuggestions(searchInput.value.trim());
    });
    searchInput.addEventListener('blur', function() {
      setTimeout(() => {
        liveSuggestList.style.display = 'none';
      }, 120);
    });
    liveSuggestList.addEventListener('mousedown', function(e) {
      const item = e.target.closest('.live-suggest-item');
      if (item && item.dataset.url) {
        window.location.href = item.dataset.url;
      }
    });
    searchInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        const query = searchInput.value.trim();
        const normQuery = normalize(query);
        // Fuzzy match: allow partials anywhere in name or keywords
        const suggestions = sitePages.filter(page => {
          const nameNorm = page.name.toLowerCase();
          if (nameNorm.includes(normQuery) || normQuery.includes(nameNorm)) return true;
          // Fuzzy: match if all query letters appear in order in name (e.g. agr -> agriculture)
          let i = 0, j = 0;
          while (i < normQuery.length && j < nameNorm.length) {
            if (normQuery[i] === nameNorm[j]) i++;
            j++;
          }
          if (i === normQuery.length) return true;
          // Also check keywords
          return page.keywords.some(k => {
            const kNorm = k.toLowerCase();
            if (kNorm.includes(normQuery) || normQuery.includes(kNorm)) return true;
            let ki = 0, kj = 0;
            while (ki < normQuery.length && kj < kNorm.length) {
              if (normQuery[ki] === kNorm[kj]) ki++;
              kj++;
            }
            return ki === normQuery.length;
          });
        });
        if (suggestions.length > 0) {
          window.location.href = suggestions[0].url;
        } else {
          window.location.href = 'notfound.html';
        }
      }
    });
  }

  function handleSearch(e) {
    e.preventDefault();
    const query = searchInput.value.trim();
    if (!query) {
      featureCards.forEach(card => card.style.display = '');
      if (heroContent) heroContent.style.display = '';
      if (ctaContent) ctaContent.style.display = '';
      return;
    }
    const normQuery = normalize(query);
    // Fuzzy match for related pages
    const suggestions = sitePages.filter(page => {
      const nameNorm = page.name.toLowerCase();
      if (nameNorm.includes(normQuery) || normQuery.includes(nameNorm)) return true;
      let i = 0, j = 0;
      while (i < normQuery.length && j < nameNorm.length) {
        if (normQuery[i] === nameNorm[j]) i++;
        j++;
      }
      if (i === normQuery.length) return true;
      return page.keywords.some(k => {
        const kNorm = k.toLowerCase();
        if (kNorm.includes(normQuery) || normQuery.includes(kNorm)) return true;
        let ki = 0, kj = 0;
        while (ki < normQuery.length && kj < kNorm.length) {
          if (normQuery[ki] === kNorm[kj]) ki++;
          kj++;
        }
        return ki === normQuery.length;
      });
    });
    if (suggestions.length > 0) {
      window.location.href = suggestions[0].url;
      return;
    }
    window.location.href = 'notfound.html';
  }
});
// Theme Toggle Logic
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;

    // 1. Load the saved theme from the browser's memory
    const savedTheme = localStorage.getItem('theme') || 'light';
    htmlElement.setAttribute('data-theme', savedTheme);

    // 2. Listen for clicks on the toggle button
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            // Apply new theme
            htmlElement.setAttribute('data-theme', newTheme);
            // Save to localStorage
            localStorage.setItem('theme', newTheme);
        });
    }
});