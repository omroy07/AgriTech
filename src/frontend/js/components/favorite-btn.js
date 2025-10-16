/**
 * Favorite Button Component
 * Reusable component for adding/removing blogs from favorites
 */
class FavoriteButton {
    constructor(blogId, blogData = {}) {
        this.blogId = blogId;
        this.blogData = blogData;
        this.isFavorite = this.checkIfFavorite();
        this.button = null;
        this.onChangeCallbacks = [];
        this.init();
    }

    init() {
        this.createButton();
        this.updateButtonState();
    }

    createButton() {
        this.button = document.createElement('button');
        this.button.className = `favorite-btn ${this.isFavorite ? 'active' : ''}`;
        this.button.setAttribute('aria-label', this.isFavorite ? 'Remove from favorites' : 'Add to favorites');
        this.button.setAttribute('data-blog-id', this.blogId);
        
        this.button.innerHTML = `
            <i class="${this.isFavorite ? 'fas' : 'far'} fa-heart"></i>
        `;
        
        this.button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.toggleFavorite();
        });
    }

    toggleFavorite() {
        const favoritesManager = window.favoritesManager || new FavoritesManager();
        
        if (this.isFavorite) {
            favoritesManager.removeFromFavorites(this.blogId);
        } else {
            favoritesManager.addToFavorites({
                id: this.blogId,
                ...this.blogData
            });
        }

        this.isFavorite = !this.isFavorite;
        this.updateButtonState();
        
        // Notify all callbacks
        this.onChangeCallbacks.forEach(callback => {
            callback(this.isFavorite, this.blogId);
        });

        // Dispatch custom event
        const event = new CustomEvent('favoriteToggle', {
            detail: {
                blogId: this.blogId,
                isFavorite: this.isFavorite,
                blogData: this.blogData
            }
        });
        document.dispatchEvent(event);
    }

    updateButtonState() {
        if (!this.button) return;
        
        const icon = this.button.querySelector('i');
        if (this.isFavorite) {
            icon.className = 'fas fa-heart';
            this.button.classList.add('active');
            this.button.setAttribute('aria-label', 'Remove from favorites');
        } else {
            icon.className = 'far fa-heart';
            this.button.classList.remove('active');
            this.button.setAttribute('aria-label', 'Add to favorites');
        }
    }

    checkIfFavorite() {
        const favoritesManager = window.favoritesManager || new FavoritesManager();
        return favoritesManager.isFavorite(this.blogId);
    }

    // Public methods
    getButton() {
        return this.button;
    }

    onChange(callback) {
        this.onChangeCallbacks.push(callback);
    }

    destroy() {
        if (this.button) {
            this.button.removeEventListener('click', this.toggleFavorite);
            this.button.remove();
        }
    }
}

// Auto-initialize favorite buttons on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize favorite buttons for existing blog cards
    const blogCards = document.querySelectorAll('[data-blog-id]');
    blogCards.forEach(card => {
        const blogId = card.getAttribute('data-blog-id');
        const blogData = {
            title: card.querySelector('.blog-title')?.textContent || '',
            excerpt: card.querySelector('.blog-excerpt')?.textContent || '',
            author: card.querySelector('.blog-author')?.textContent || '',
            date: card.querySelector('.blog-date')?.textContent || '',
            image: card.querySelector('.blog-image')?.src || '',
            url: card.querySelector('.blog-link')?.href || ''
        };

        const favoriteBtn = new FavoriteButton(blogId, blogData);
        const buttonContainer = card.querySelector('.favorite-btn-container') || card;
        buttonContainer.appendChild(favoriteBtn.getButton());
    });
});