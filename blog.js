// Sample blog data
const blogPosts = [
    {
        id: 'sustainable-farming-2025',
        title: "Sustainable Farming Practices for 2025",
        category: "sustainability",
        description: "Discover innovative sustainable farming techniques that are revolutionizing agriculture.",
        image: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&h=250&fit=crop",
        content: `<p>Sustainable farming practices for modern agriculture.</p>`,
        author: "Dr. Sarah Green",
        date: "2025-01-10"
    },
    {
        id: 'ai-agriculture-revolution', 
        title: "AI in Agriculture: The Next Revolution",
        category: "technology",
        description: "How artificial intelligence is transforming farming operations.",
        image: "https://images.unsplash.com/photo-1555255707-c07966088b7b?w=400&h=250&fit=crop",
        content: `<p>AI applications in modern farming.</p>`,
        author: "Tech Farm Review",
        date: "2025-01-08"
    },
    {
        id: 'organic-pest-control',
        title: "Organic Pest Control Methods", 
        category: "sustainability",
        description: "Natural ways to protect crops from pests without chemicals.",
        image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&h=250&fit=crop",
        content: `<p>Organic pest control methods.</p>`,
        author: "Organic Farming Association", 
        date: "2025-01-05"
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
    
    // Wait a bit for FavoritesManager to initialize
    setTimeout(() => {
        if (!window.favoritesManager) {
            console.error('❌ FavoritesManager not found! Check file paths.');
            // Create a fallback
            window.favoritesManager = {
                isFavorite: () => false,
                addToFavorites: () => console.log('Favorites not available'),
                removeFromFavorites: () => console.log('Favorites not available'),
                getFavorites: () => []
            };
        }
        
        displayPosts();
        setupEventListeners();
        updateFavoriteCounter();
    }, 100);
});

function setupEventListeners() {
    // Search
    document.getElementById('searchInput').addEventListener('input', function() {
        searchQuery = this.value.toLowerCase();
        filterPosts();
    });

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
    document.getElementById('loadMoreBtn').addEventListener('click', loadMorePosts);

    // Modal
    document.querySelector('.close').addEventListener('click', closeModal);
    window.addEventListener('click', (e) => e.target === modal && closeModal());

    // Modal favorite button
    document.getElementById('modalFavoriteBtn').addEventListener('click', toggleModalFavorite);

    // Event delegation for favorite buttons
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
        const matchesSearch = post.title.toLowerCase().includes(searchQuery) || 
                            post.description.toLowerCase().includes(searchQuery);
        const matchesCategory = currentCategory === 'all' || post.category === currentCategory;
        return matchesSearch && matchesCategory;
    });

    currentPage = 0;
    document.getElementById('blogGrid').innerHTML = '';
    displayPosts();
}

function displayPosts() {
    const blogGrid = document.getElementById('blogGrid');
    const startIndex = currentPage * postsPerPage;
    const postsToShow = filteredPosts.slice(startIndex, startIndex + postsPerPage);

    if (postsToShow.length === 0) {
        blogGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem;">No posts found.</div>';
        document.getElementById('loadMoreBtn').style.display = 'none';
        return;
    }

    postsToShow.forEach(post => {
        const isFavorite = window.favoritesManager.isFavorite(post.id);
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
                <button class="read-more-btn" onclick="openModal('${post.id}')">Read More</button>
            </div>
        `;
        blogGrid.appendChild(postElement);
    });
    //Changes for issue #478
    let BlGrid = document.getElementById('blogGrid');
    let array = BlGrid.children;
    
        let card2 = array[1]; // second card
        let cardcontent = card2.children[2]; // card content of second card
        let cardmeta = cardcontent.querySelector(".card-meta");
        cardmeta.style.transform = "translateY(20px)";
        let btn = cardcontent.children[4]; // read more button of second card
        btn.style.transform = "translateY(20px)";

        let card3 = array[2]; // third card
        let cardcontent2 = card3.children[2]; // card content of second card
        let cardmeta2 = cardcontent2.querySelector(".card-meta");
        cardmeta2.style.transform = "translateY(20px)";
        let btn2 = cardcontent2.children[4]; // read more button of second card
        btn2.style.transform = "translateY(20px)";
    

    document.getElementById('loadMoreBtn').style.display = 
        (currentPage + 1) * postsPerPage >= filteredPosts.length ? 'none' : 'inline-block';
}

function toggleFavorite(blogId) {
    console.log('🔄 Toggling favorite for:', blogId);
    
    if (!window.favoritesManager) {
        alert('❌ Favorites feature not loaded. Check browser console for errors.');
        return;
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
        button.classList.toggle('active', isFavorite);
        icon.className = isFavorite ? 'fas fa-heart' : 'far fa-heart';
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
    document.getElementById('modalTitle').textContent = post.title;
    document.getElementById('modalCategory').textContent = post.category.replace('-', ' ');
    document.getElementById('modalImage').src = post.image;
    document.getElementById('modalContent').innerHTML = post.content;

    updateModalFavoriteButton();
    document.getElementById('blogModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('blogModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    currentModalPostId = null;
}

function updateModalFavoriteButton() {
    if (!window.favoritesManager || !currentModalPostId) return;
    
    const isFavorite = window.favoritesManager.isFavorite(currentModalPostId);
    const button = document.getElementById('modalFavoriteBtn');
    const icon = button.querySelector('i');
    
    button.classList.toggle('active', isFavorite);
    icon.className = isFavorite ? 'fas fa-heart' : 'far fa-heart';
}

function toggleModalFavorite() {
    if (currentModalPostId) {
        toggleFavorite(currentModalPostId);
    }
}

// Theme toggle
document.getElementById('themeToggle').addEventListener('click', function() {
    const isDark = document.documentElement.hasAttribute('data-theme');
    const icon = document.getElementById('themeIcon');
    const text = document.getElementById('themeText');
    
    if (isDark) {
        document.documentElement.removeAttribute('data-theme');
        icon.textContent = '🌙';
        text.textContent = 'Dark Mode';
    } else {
        document.documentElement.setAttribute('data-theme', 'dark');
        icon.textContent = '☀️';
        text.textContent = 'Light Mode';
    }
});

// Listen for favorite changes
document.addEventListener('favoriteToggle', function(event) {
    console.log('📢 Favorite event received:', event.detail);
    updateFavoriteButtons(event.detail.blogId);
    updateFavoriteCounter();
});

// Debug function
window.debugFavorites = function() {
    console.log('=== DEBUG INFO ===');
    console.log('FavoritesManager:', window.favoritesManager);
    console.log('Favorites:', window.favoritesManager?.getFavorites());
};