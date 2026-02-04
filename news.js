// News Data - Sample agricultural news articles
const newsArticles = [
    {
        id: 1,
        title: "New AI Technology Revolutionizes Crop Yield Prediction",
        description: "Researchers develop advanced AI models that can predict crop yields with 95% accuracy, helping farmers make informed decisions.",
        content: "Scientists have developed a groundbreaking AI system that analyzes soil data, weather patterns, and historical crop information to predict yield outcomes. This technology is expected to help farmers optimize their planting strategies and increase productivity by up to 30%. The system uses machine learning algorithms trained on data from thousands of farms across different regions.",
        category: "technology",
        source: "AgriTech Daily",
        date: "2024-01-24",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%2322c55e' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EAI Crop Prediction%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 2,
        title: "Global Agricultural Markets Show Strong Growth",
        description: "Agricultural commodity prices surge as demand increases worldwide, offering opportunities for farmers to maximize profits.",
        content: "The global agricultural market has experienced significant growth this quarter, with prices for major commodities like wheat, corn, and soybeans reaching five-year highs. This surge is driven by increased global demand, supply chain improvements, and favorable weather conditions in key producing regions.",
        category: "market-trends",
        source: "Farm Economics Weekly",
        date: "2024-01-23",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%2316a34a' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EMarket Growth%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 3,
        title: "Sustainable Farming Practices Reduce Environmental Impact by 40%",
        description: "New sustainable farming methods significantly reduce carbon emissions and water usage while maintaining crop productivity.",
        content: "A comprehensive study conducted across 50 farms demonstrates that implementing sustainable agricultural practices can reduce environmental impact by 40% without compromising crop yields. These practices include crop rotation, precision irrigation, and organic pest management techniques.",
        category: "sustainability",
        source: "Green Farming Initiative",
        date: "2024-01-22",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%2310b981' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3ESustainable Farming%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 4,
        title: "Weather Alert: Monsoon Predictions for This Season",
        description: "Meteorological department releases early predictions for upcoming monsoon season, crucial for agricultural planning.",
        content: "The Meteorological Department has issued early predictions for the upcoming monsoon season, expecting 15% above-average rainfall in agricultural regions. This forecast is critical for farmers to plan their planting schedules and water management strategies effectively.",
        category: "weather",
        source: "Weather & Climate Bureau",
        date: "2024-01-21",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%233b82f6' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EWeather Forecast%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 5,
        title: "Government Announces New Subsidy Program for Organic Farming",
        description: "Latest policy includes incentives for farmers transitioning to organic agriculture, supporting sustainable practices.",
        content: "The government has launched a comprehensive subsidy program offering financial incentives for farmers who transition to organic farming. The program includes grants, low-interest loans, and technical support to help farmers adopt sustainable practices.",
        category: "policy",
        source: "Government Agriculture Ministry",
        date: "2024-01-20",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%238b5cf6' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EPolicy News%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 6,
        title: "Drone Technology Transforms Precision Agriculture",
        description: "Agricultural drones equipped with advanced sensors enable real-time crop monitoring and targeted interventions.",
        content: "The adoption of drone technology in agriculture has revolutionized how farmers monitor and manage their crops. Drones equipped with multispectral cameras and AI analysis can identify plant diseases, pest infestations, and irrigation issues with unprecedented accuracy.",
        category: "innovation",
        source: "Precision Agriculture Today",
        date: "2024-01-19",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%23ec4899' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EDrone Technology%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 7,
        title: "Vertical Farming Shows Promise in Urban Agriculture",
        description: "Indoor vertical farms in cities produce fresh vegetables year-round with minimal water usage and no pesticides.",
        content: "Urban vertical farms are gaining traction as a sustainable solution for local food production. These innovative facilities use LED lighting and hydroponic systems to grow vegetables year-round, reducing transportation costs and environmental impact.",
        category: "innovation",
        source: "Urban Farming News",
        date: "2024-01-18",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%238b5cf6' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EVertical Farming%3C/text%3E%3C/svg%3E",
        link: "#"
    },
    {
        id: 8,
        title: "Water Conservation Techniques Save Farmers Millions",
        description: "Advanced irrigation systems reduce water consumption by 50% while improving crop health and yield.",
        content: "Farmers implementing advanced irrigation technologies like drip irrigation and soil moisture sensors have reported significant water savings and improved crop productivity. These systems provide precise water delivery, reducing waste and lowering agricultural costs.",
        category: "sustainability",
        source: "Water Conservation Alliance",
        date: "2024-01-17",
        image: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 300'%3E%3Crect fill='%234f46e5' width='400' height='300'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white' font-weight='bold'%3EWater Conservation%3C/text%3E%3C/svg%3E",
        link: "#"
    }
];

// DOM Elements
const newsGrid = document.getElementById('newsGrid');
const searchInput = document.getElementById('searchInput');
const categoryButtons = document.querySelectorAll('.filter-btn');
const newsModal = document.getElementById('newsModal');
const closeModal = document.getElementById('closeNewsModal');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const refreshBtn = document.getElementById('refreshBtn');
const emptyState = document.getElementById('empty-news-state');
const themeToggle = document.getElementById('themeToggle');

// State
let currentCategory = 'all';
let currentSearchTerm = '';
let displayedArticles = 6;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    renderNews();
    setupEventListeners();
});

// Initialize theme based on system preference
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const theme = savedTheme || (prefersDark ? 'dark' : 'light');
    
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeIcon(theme);
}

// Update theme icon and text
function updateThemeIcon(theme) {
    const icon = document.getElementById('themeIcon');
    const text = document.getElementById('themeText');
    if (theme === 'dark') {
        icon.textContent = '☀️';
        text.textContent = 'Light Mode';
    } else {
        icon.textContent = '🌙';
        text.textContent = 'Dark Mode';
    }
}

// Setup Event Listeners
function setupEventListeners() {
    // Category filter
    categoryButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            categoryButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = btn.getAttribute('data-category');
            displayedArticles = 6;
            renderNews();
        });
    });

    // Search
    searchInput.addEventListener('input', (e) => {
        currentSearchTerm = e.target.value.toLowerCase();
        displayedArticles = 6;
        renderNews();
    });

    // Load More
    loadMoreBtn.addEventListener('click', () => {
        displayedArticles += 6;
        renderNews();
    });

    // Refresh
    refreshBtn.addEventListener('click', () => {
        displayedArticles = 6;
        currentCategory = 'all';
        currentSearchTerm = '';
        searchInput.value = '';
        categoryButtons.forEach(b => b.classList.remove('active'));
        categoryButtons[0].classList.add('active');
        renderNews();
    });

    // Theme Toggle
    themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeIcon(newTheme);
    });

    // Close Modal
    closeModal.addEventListener('click', () => {
        newsModal.classList.remove('active');
    });

    newsModal.addEventListener('click', (e) => {
        if (e.target === newsModal) {
            newsModal.classList.remove('active');
        }
    });
}

// Filter News
function getFilteredNews() {
    let filtered = newsArticles;

    // Category filter
    if (currentCategory !== 'all') {
        filtered = filtered.filter(article => article.category === currentCategory);
    }

    // Search filter
    if (currentSearchTerm) {
        filtered = filtered.filter(article =>
            article.title.toLowerCase().includes(currentSearchTerm) ||
            article.description.toLowerCase().includes(currentSearchTerm) ||
            article.content.toLowerCase().includes(currentSearchTerm)
        );
    }

    return filtered;
}

// Render News
function renderNews() {
    const filtered = getFilteredNews();
    const toDisplay = filtered.slice(0, displayedArticles);

    // Show/hide empty state
    if (toDisplay.length === 0) {
        emptyState.style.display = 'block';
        newsGrid.innerHTML = '';
        loadMoreBtn.style.display = 'none';
        return;
    }

    emptyState.style.display = 'none';

    // Render articles
    newsGrid.innerHTML = toDisplay.map(article => `
        <div class="news-card" onclick="openNewsModal(${article.id})">
            <img src="${article.image}" alt="${article.title}" class="news-card-image">
            <div class="news-card-content">
                <span class="news-card-category">${capitalizeCategory(article.category)}</span>
                <h3 class="news-card-title">${article.title}</h3>
                <p class="news-card-description">${article.description}</p>
                <div class="news-card-meta">
                    <span class="news-card-source">
                        <i class="fas fa-globe"></i> ${article.source}
                    </span>
                    <span class="news-card-date">
                        <i class="far fa-calendar-alt"></i> ${formatDate(article.date)}
                    </span>
                </div>
            </div>
        </div>
    `).join('');

    // Show/hide load more button
    loadMoreBtn.style.display = displayedArticles < filtered.length ? 'block' : 'none';
}

// Open News Modal
function openNewsModal(id) {
    const article = newsArticles.find(a => a.id === id);
    if (!article) return;

    document.getElementById('modalTitle').textContent = article.title;
    document.getElementById('modalImage').src = article.image;
    document.getElementById('modalContent').textContent = article.content;
    document.getElementById('modal-source').innerHTML = `<i class="fas fa-globe"></i> Source: ${article.source}`;
    document.getElementById('modal-date').innerHTML = `<i class="far fa-calendar-alt"></i> ${formatDate(article.date)}`;
    document.getElementById('modalCategory').textContent = capitalizeCategory(article.category);
    document.getElementById('modalLink').href = article.link;

    newsModal.classList.add('active');
}

// Helper Functions
function capitalizeCategory(category) {
    return category.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Add keyboard support
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        newsModal.classList.remove('active');
    }
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