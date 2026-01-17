// Favorites Manager - Simple Version
class FavoritesManager {
    constructor() {
        this.storageKey = 'agritech_favorite_blogs';
        this.favorites = this.loadFavorites();
        this.init();
    }

    init() {
        window.favoritesManager = this;
        console.log('✅ FavoritesManager loaded with', this.favorites.length, 'favorites');
    }

    loadFavorites() {
        try {
            const favs = JSON.parse(localStorage.getItem(this.storageKey)) || [];
            console.log('📁 Loaded favorites:', favs);
            return favs;
        } catch (error) {
            console.error('❌ Error loading favorites:', error);
            return [];
        }
    }

    saveFavorites() {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(this.favorites));
            console.log('💾 Saved favorites:', this.favorites);
        } catch (error) {
            console.error('❌ Error saving favorites:', error);
        }
    }

    addToFavorites(blogData) {
        if (!blogData.id) {
            console.error('❌ Blog data must have an id');
            return false;
        }

        if (this.isFavorite(blogData.id)) {
            console.log('⚠️ Blog already in favorites');
            return false;
        }

        blogData.addedAt = new Date().toISOString();
        this.favorites.push(blogData);
        this.saveFavorites();

        this.showNotification(`Added to favorites: ${blogData.title}`);
        this.dispatchFavoriteToggle(blogData.id, true, blogData);
        return true;
    }

    removeFromFavorites(blogId) {
        const initialLength = this.favorites.length;
        this.favorites = this.favorites.filter(blog => blog.id !== blogId);

        if (this.favorites.length < initialLength) {
            this.saveFavorites();
            this.showNotification('Removed from favorites');
            this.dispatchFavoriteToggle(blogId, false);
            return true;
        }
        return false;
    }

    isFavorite(blogId) {
        const isFav = this.favorites.some(blog => blog.id === blogId);
        console.log('🔍 Checking favorite:', blogId, '->', isFav);
        return isFav;
    }

    getFavorites() {
        return [...this.favorites].sort(
            (a, b) => new Date(b.addedAt) - new Date(a.addedAt)
        );
    }

    dispatchFavoriteToggle(blogId, isFavorite, blogData = null) {
        const event = new CustomEvent('favoriteToggle', {
            detail: { blogId, isFavorite, blogData }
        });
        document.dispatchEvent(event);
        console.log('📢 Dispatched favorite event:', blogId, isFavorite);
    }

    /* =====================================================
       ACCESSIBILITY FIX – Issue #617
       Screen reader announcement for notifications
       ===================================================== */
    showNotification(message) {
        // Remove existing notifications
        const existing = document.querySelectorAll('.favorite-notification');
        existing.forEach(note => note.remove());

        const notification = document.createElement('div');
        notification.className = 'favorite-notification';
        notification.textContent = message;

        // ✅ Accessibility additions
        notification.setAttribute('role', 'status');
        notification.setAttribute('aria-live', 'polite');
        notification.setAttribute('aria-atomic', 'true');

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #2c5f2d;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🚀 Initializing FavoritesManager...');
        new FavoritesManager();
    });
} else {
    console.log('🚀 DOM already loaded, initializing FavoritesManager...');
    new FavoritesManager();
}
