/* =========================================
   FAVORITES MANAGER
   (Restored logic to make the Heart buttons work)
   ========================================= */
class FavoritesManager {
    constructor() {
        this.storageKey = 'agritech_favorite_blogs';
        this.favorites = JSON.parse(localStorage.getItem(this.storageKey)) || [];
        window.favoritesManager = this;
        console.log('✅ FavoritesManager initialized');
    }

    isFavorite(blogId) {
        return this.favorites.some(blog => blog.id === blogId);
    }

    addToFavorites(blogData) {
        if (this.isFavorite(blogData.id)) return false;
        
        // Add timestamp
        blogData.addedAt = new Date().toISOString();
        this.favorites.push(blogData);
        this.save();
        
        this.showNotification(`Added to favorites: ${blogData.title}`, 'success');
        this.dispatchEvent(blogData.id, true);
        return true;
    }

    removeFromFavorites(blogId) {
        this.favorites = this.favorites.filter(blog => blog.id !== blogId);
        this.save();
        
        this.showNotification('Removed from favorites', 'error');
        this.dispatchEvent(blogId, false);
        return true;
    }

    getFavorites() {
        return this.favorites;
    }

    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.favorites));
    }

    dispatchEvent(blogId, isFavorite) {
        const event = new CustomEvent('favoriteToggle', {
            detail: { blogId, isFavorite }
        });
        document.dispatchEvent(event);
    }

    showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.className = `favorite-notification favorite-notification-${type}`;
        
        // Minimal inline styles for notification to ensure it works
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '8px',
            color: 'white',
            fontWeight: '500',
            zIndex: '10000',
            background: type === 'success' ? '#2c5f2d' : '#e74c3c',
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
        });

        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
}

// Initialize immediately so it's ready before the page loads
if (!window.favoritesManager) {
    new FavoritesManager();
}

/* =========================================
   BLOG LOGIC & DATA
   ========================================= */

// Sample blog data - UPDATED with full content for "Read More" functionality
const blogPosts = [
    {
        id: 'sustainable-farming-2025',
        title: "Sustainable Farming Practices for 2025",
        category: "sustainability",
        description: "Discover innovative sustainable farming techniques that are revolutionizing agriculture.",
        image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=250&fit=crop",
        content: `
            <p><strong>Sustainability is no longer a choice; it's a necessity.</strong> As we move into 2025, modern agriculture is seeing a massive shift towards eco-friendly practices that not only protect the environment but also improve long-term yield.</p>
            
            <h4>1. Precision Irrigation</h4>
            <p>Water scarcity is a major concern. New drip irrigation systems powered by IoT sensors can reduce water usage by up to 40% by delivering water directly to the root zone only when moisture levels drop.</p>

            <h4>2. Regenerative Agriculture</h4>
            <p>Farmers are moving away from heavy tilling. No-till farming helps maintain soil structure, retain water, and sequester carbon. Cover crops like clover and rye are being used extensively to restore soil nutrients naturally.</p>
            
            <p>By adopting these methods, farmers can lower their input costs while ensuring their land remains fertile for generations to come.</p>
        `,
        author: "Dr. Sarah Green",
        date: "2025-01-10"
    },
    {
        id: 'ai-agriculture-revolution', 
        title: "AI in Agriculture: The Next Revolution",
        category: "technology",
        description: "How artificial intelligence is transforming farming operations.",
        image: "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=400&h=250&fit=crop",
        content: `
            <p>Artificial Intelligence is not just for tech companies—it is revolutionizing the farm. From predictive analytics to autonomous tractors, AI is helping farmers make smarter decisions.</p>

            <h4>Predictive Analytics</h4>
            <p>Using historical weather data and soil conditions, AI models can now predict crop yields with over 90% accuracy. This allows farmers to plan their supply chain logistics weeks in advance.</p>

            <h4>Drone Technology</h4>
            <p>Drones equipped with multispectral cameras can scan fields to detect early signs of pest infestations or nutrient deficiencies. This "precision spraying" means chemicals are only used exactly where needed, reducing cost and environmental impact.</p>

            <p>The future of farming is data-driven, and AI is the engine driving this change.</p>
        `,
        author: "Tech Farm Review",
        date: "2025-01-08"
    },
    {
        id: 'organic-pest-control',
        title: "Organic Pest Control Methods", 
        category: "sustainability",
        description: "Natural ways to protect crops from pests without chemicals.",
        image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop",
        content: `
            <p>Chemical pesticides have long been the standard, but they come with heavy costs to biodiversity and soil health. Organic pest control is proving to be a powerful alternative.</p>

            <h4>Beneficial Insects</h4>
            <p>Introducing predators like Ladybugs and Lacewings can naturally control aphid populations. This biological warfare creates a balanced ecosystem where pests are managed without toxic sprays.</p>

            <h4>Neem Oil & Natural Sprays</h4>
            <p>Neem oil acts as a powerful repellent for over 200 species of chewing or sucking insects. Unlike synthetic chemicals, it is biodegradable and non-toxic to birds and mammals.</p>

            <p>Transitioning to organic control takes time, but the premium price of organic produce makes it a worthy investment.</p>
        `,
        author: "Organic Farming Association", 
        date: "2025-01-05"
    },
    {
        id: "soil-health-basics",
        title: "Soil Health Basics Every Farmer Should Know",
        category: "farming-tips",
        description: "Healthy soil is the foundation of successful farming. Learn simple ways to improve it.",
        author: "Anita Verma",
        date: "February 10, 2025",
        image: "https://cdn.tractorkarvan.com/tr:f-webp/images/Blogs/soil-health-card-scheme/Soil-Health-Card-Scheme-Blog.jpg",
        content: `
            <p>Healthy soil leads to better crop growth and higher yields.</p>
            <h4>Key Tips</h4>
            <ul>
                <li>Add organic compost regularly</li>
                <li>Avoid over-tilling the land</li>
                <li>Test soil nutrients every season</li>
            </ul>
            <p>Improving soil health ensures long-term farm sustainability.</p>
        `
    },
    {
        id: "water-saving-irrigation",
        title: "Water-Saving Irrigation Techniques",
        category: "farming-tips",
        description: "Reduce water usage while maintaining crop productivity with smart irrigation.",
        author: "Ramesh Patel",
        date: "February 18, 2025",
        image: "https://images.unsplash.com/photo-1524486361537-8ad15938e1a3?w=800&fit=crop",
        content: `
            <p>Water management is crucial, especially in dry regions.</p>
            <h4>Best Practices</h4>
            <ul>
                <li>Use drip irrigation systems</li>
                <li>Water crops early in the morning</li>
                <li>Monitor soil moisture regularly</li>
            </ul>
            <p>Efficient irrigation saves resources and increases profitability.</p>
        `
    },
    {
        id: "natural-pest-control",
        title: "Natural Pest Control Methods",
        category: "farming-tips",
        description: "Protect crops using eco-friendly pest control methods instead of chemicals.",
        author: "Dr. Kunal Mehta",
        date: "March 02, 2025",
        image: "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?w=800&fit=crop",
        content: `
            <p>Chemical pesticides can harm soil and crops.</p>
            <h4>Natural Solutions</h4>
            <ul>
                <li>Neem oil spray</li>
                <li>Introduce beneficial insects</li>
                <li>Practice crop rotation</li>
            </ul>
            <p>Natural pest control keeps farms safe and sustainable.</p>
        `
    },
    {
        id: "seasonal-crop-planning",
        title: "Seasonal Crop Planning for Better Yield",
        category: "farming-tips",
        description: "Choosing the right crop for the right season can significantly boost yield.",
        author: "Sunita Rao",
        date: "March 20, 2025",
        image: "https://i.ytimg.com/vi/v3lFfRBZkxY/maxresdefault.jpg",
        content: `
            <p>Seasonal planning helps farmers avoid losses.</p>
            <h4>Planning Tips</h4>
            <ul>
                <li>Understand local climate patterns</li>
                <li>Choose crops suited to the season</li>
                <li>Rotate crops yearly</li>
            </ul>
            <p>Smart planning leads to stable income and healthy soil.</p>
        `
    },

        {
        id: "maximize-yield-crop-rotation",
        title: "Maximize Yield with Crop Rotation",
        category: "farming-tips",
        description: "Learn how crop rotation improves soil health and boosts crop yield.",
        author: "Dr. R.K. Singh",
        date: "March 15, 2025",
        image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?auto=format&fit=crop&w=800&q=80",
        content: `
            <p>Crop rotation is the practice of planting different crops sequentially on the same plot of land...</p>
        `
    },

    {
        id: 5,
        title: "Agri-Market Trends: Wheat Prices Soar",
        category: "market-trends", // Matches the button data-category="market-trends"
        author: "Market Watch Team",
        date: "March 18, 2025",
        image: "https://images.unsplash.com/photo-1574943320219-553eb213f72d?auto=format&fit=crop&w=800&q=80",
        content: "The global wheat market is experiencing a significant upturn this quarter due to changing climate patterns in major export zones. Farmers in India are seeing a 15% increase in MSP..."
    },
    {
        id: 6,
        title: "Starting an Organic Fertilizer Business",
        category: "business", // Matches the button data-category="business"
        author: "Amit Patel",
        date: "March 20, 2025",
        image: "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&w=800&q=80",
        content: "Turning farm waste into gold! Vermicomposting is one of the most profitable low-investment agri-businesses today. Here is a step-by-step guide to setting up your own unit..."
    }
];

// Global variables
let currentPage = 0;
const postsPerPage = 6;
let filteredPosts = [...blogPosts];
let currentCategory = 'all';
let searchQuery = '';
let currentModalPostId = null;

// Wait for DOM and FavoritesManager to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, initializing blog...');
    
    // Slight delay to ensure FavoritesManager is attached if it wasn't already
    setTimeout(() => {
        if (!window.favoritesManager) {
            console.error('⚠️ FavoritesManager missing, creating fallback...');
            window.favoritesManager = new FavoritesManager();
        }
        
        displayPosts();
        setupEventListeners();
        updateFavoriteCounter();
    }, 50);
});

function setupEventListeners() {
    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            searchQuery = this.value.toLowerCase();
            filterPosts();
        });
    }

    // Filters
    document.querySelectorAll('.filter-btn').forEach(button => {
        button.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.dataset.category;
            filterPosts();
        });
    });

    // Load more
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMorePosts);
    }

    // Modal Close
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
    
    const modal = document.getElementById('blogModal');
    if (modal) {
        window.addEventListener('click', (e) => e.target === modal && closeModal());
    }

    // Modal favorite button
    const modalFavBtn = document.getElementById('modalFavoriteBtn');
    if (modalFavBtn) {
        modalFavBtn.addEventListener('click', toggleModalFavorite);
    }

    // Event delegation for favorite buttons on cards
    document.addEventListener('click', function(e) {
        if (e.target.closest('.favorite-btn')) {
            const button = e.target.closest('.favorite-btn');
            const blogId = button.getAttribute('data-blog-id');
            console.log('🎯 Favorite button clicked:', blogId);
            toggleFavorite(blogId);
        }
    });
}

function updateFavoriteCounter() {
    if (window.favoritesManager) {
        const count = window.favoritesManager.getFavorites().length;
        document.querySelectorAll('.favorite-count').forEach(el => el.textContent = count);
    }
}

function filterPosts() {
    filteredPosts = blogPosts.filter(post => {
        const title = post.title ? post.title.toLowerCase() : '';
        const description = post.description ? post.description.toLowerCase() : '';
        const content = post.content ? post.content.toLowerCase() : '';

        const matchesSearch =
            title.includes(searchQuery) ||
            description.includes(searchQuery) ||
            content.includes(searchQuery);

        const matchesCategory =
            currentCategory === 'all' || post.category === currentCategory;

        return matchesSearch && matchesCategory;
    });

    currentPage = 0;
    const blogGrid = document.getElementById('blogGrid');
    blogGrid.innerHTML = '';
    displayPosts();
}

function displayPosts() {
    const blogGrid = document.getElementById('blogGrid');
    if (!blogGrid) return;

    const startIndex = currentPage * postsPerPage;
    const postsToShow = filteredPosts.slice(startIndex, startIndex + postsPerPage);

    const loadMoreBtn = document.getElementById('loadMoreBtn');

    if (postsToShow.length === 0) {
        blogGrid.innerHTML = `
    <div class="no-results">
        <i class="fas fa-search"></i>
        <h3>No matching blogs found</h3>
        <p>
            We couldn’t find any blog posts for
            <strong>"${searchQuery || 'your search'}"</strong>.
        </p>
        <span>Try different keywords or change the category filter.</span>
    </div>
`;

        if (loadMoreBtn) loadMoreBtn.style.display = 'none';
        return;
    }

    postsToShow.forEach(post => {
        const isFavorite = window.favoritesManager ? window.favoritesManager.isFavorite(post.id) : false;
        const postElement = document.createElement('div');
        postElement.className = 'blog-card';
        postElement.innerHTML = `
            <img src="${post.image}" alt="${post.title}">
            <button class="favorite-btn ${isFavorite ? 'active' : ''}" data-blog-id="${post.id}">
                <i class="${isFavorite ? 'fas' : 'far'} fa-heart"></i>
            </button>
            <div class="card-content">
                <span class="card-category">${post.category.replace('-', ' ')}</span>
                <h3 class="card-title">${post.title}</h3>
                <p class="card-description">${post.description}</p>
                <div class="card-meta">
                    <span class="card-author">By ${post.author}</span>
                    <span class="card-date">${post.date}</span>
                </div>
                <button class="read-more-btn" style="margin-top:16px"onclick="openModal('${post.id}')">Read More</button>
            </div>
        `;
        blogGrid.appendChild(postElement);
    });

    if (loadMoreBtn) {
        loadMoreBtn.style.display = 
            (currentPage + 1) * postsPerPage >= filteredPosts.length ? 'none' : 'inline-block';
    }
}

function toggleFavorite(blogId) {
    if (!window.favoritesManager) {
        // Fallback re-init
        window.favoritesManager = new FavoritesManager();
    }

    const post = blogPosts.find(p => p.id === blogId);
    if (!post) {
        console.error('❌ Post not found:', blogId);
        return;
    }

    const isFavorite = window.favoritesManager.isFavorite(blogId);
    
    if (isFavorite) {
        window.favoritesManager.removeFromFavorites(blogId);
    } else {
        window.favoritesManager.addToFavorites({
            id: blogId,
            title: post.title,
            description: post.description,
            category: post.category,
            image: post.image,
            author: post.author,
            date: post.date,
            content: post.content
        });
    }

    updateFavoriteButtons(blogId);
    updateFavoriteCounter();
}

function updateFavoriteButtons(blogId) {
    const buttons = document.querySelectorAll(`.favorite-btn[data-blog-id="${blogId}"]`);
    const isFavorite = window.favoritesManager.isFavorite(blogId);
    
    buttons.forEach(button => {
        const icon = button.querySelector('i');
        if (icon) {
            button.classList.toggle('active', isFavorite);
            icon.className = isFavorite ? 'fas fa-heart' : 'far fa-heart';
        }
    });

    if (currentModalPostId === blogId) {
        updateModalFavoriteButton();
    }
}

function loadMorePosts() {
    currentPage++;
    displayPosts();
}

function openModal(postId) {
    const post = blogPosts.find(p => p.id === postId);
    if (!post) return;

    currentModalPostId = postId;
    
    // 1. Basic Info
    const titleEl = document.getElementById('modalTitle');
    if (titleEl) titleEl.textContent = post.title;

    const catEl = document.getElementById('modalCategory');
    if (catEl) catEl.textContent = post.category.replace('-', ' ');

    const imgEl = document.getElementById('modalImage');
    if (imgEl) imgEl.src = post.image;

    // 2. Full Content
    const contentEl = document.getElementById('modalContent');
    if (contentEl) contentEl.innerHTML = post.content;

    // 3. Metadata (Author/Date)
    const authorEl = document.getElementById('modalAuthor');
    if (authorEl) {
        authorEl.innerHTML = `<i class="fas fa-user"></i> By ${post.author}`;
    }

    const dateEl = document.getElementById('modalDate');
    if (dateEl) {
        dateEl.innerHTML = `<i class="far fa-calendar-alt"></i> ${post.date}`;
    }

    updateModalFavoriteButton();
    
    const modal = document.getElementById('blogModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal() {
    const modal = document.getElementById('blogModal');
    if (modal) modal.style.display = 'none';
    document.body.style.overflow = 'auto';
    currentModalPostId = null;
}

function updateModalFavoriteButton() {
    if (!window.favoritesManager || !currentModalPostId) return;
    
    const isFavorite = window.favoritesManager.isFavorite(currentModalPostId);
    const button = document.getElementById('modalFavoriteBtn');
    
    if (button) {
        const icon = button.querySelector('i');
        button.classList.toggle('active', isFavorite);
        icon.className = isFavorite ? 'fas fa-heart' : 'far fa-heart';
    }
}

function toggleModalFavorite() {
    if (currentModalPostId) {
        toggleFavorite(currentModalPostId);
    }
}

/* =========================================
   THEME TOGGLE (With Memory)
   ========================================= */

const themeToggleBtn = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');
const themeText = document.getElementById('themeText');

// 1. Function to Apply Theme
function applyTheme(theme) {
    // Set the attribute on the HTML tag
    if (theme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeText) themeText.textContent = 'Light Mode';
    } else {
        document.documentElement.removeAttribute('data-theme');
        if (themeIcon) themeIcon.textContent = '🌙';
        if (themeText) themeText.textContent = 'Dark Mode';
    }
}

// 2. Check for saved preference on load
const savedTheme = localStorage.getItem('agritech-theme') || 'dark'; // Default to dark
applyTheme(savedTheme);

// 3. Toggle Logic
if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', function() {
        const isDark = document.documentElement.hasAttribute('data-theme');
        const newTheme = isDark ? 'light' : 'dark';
        
        applyTheme(newTheme);
        
        // Save to browser memory
        localStorage.setItem('agritech-theme', newTheme);
    });
}

// Listen for favorite changes from other components
document.addEventListener('favoriteToggle', function(event) {
    if (event.detail) {
        updateFavoriteButtons(event.detail.blogId);
        updateFavoriteCounter();
    }
});
