/**
 * Favorite Button Component
 * Reusable component for adding/removing blogs from favorites
 * Accessibility updated for Issue #617
 */
import languages from "../i18n/languages.js";

let currentLang = localStorage.getItem("lang") || "en";

function t(key) {
  return languages[currentLang][key] || key;
}


class FavoriteButton {
    constructor(blogId, blogData = {}) {
        this.blogId = blogId;
        this.blogData = blogData;
        this.isFavorite = this.checkIfFavorite();
        this.button = null;
        this.onChangeCallbacks = [];
        this.handleClick = this.handleClick.bind(this);
        this.handleKeydown = this.handleKeydown.bind(this);
        this.init();
    }

    init() {
        this.createButton();
        this.updateButtonState();
    }

    createButton() {
        this.button = document.createElement('button');
        this.button.type = 'button';
        this.button.className = `favorite-btn ${this.isFavorite ? 'active' : ''}`;
        this.button.setAttribute(
            'aria-label',
            this.isFavorite ? 't("remove_favorite")' : 't("add_favorite")'
        );

        /* ACCESSIBILITY: announce toggle state */
        this.button.setAttribute('aria-pressed', String(this.isFavorite));

        this.button.setAttribute('data-blog-id', this.blogId);

        this.button.innerHTML = `
            <i class="${this.isFavorite ? 'fas' : 'far'} fa-heart" aria-hidden="true"></i>
        `;

        /* Mouse interaction */
        this.button.addEventListener('click', this.handleClick);

        /* Keyboard interaction (Space support) */
        this.button.addEventListener('keydown', this.handleKeydown);
    }

    handleClick(e) {
        e.preventDefault();
        e.stopPropagation();
        this.toggleFavorite();
    }

    handleKeydown(e) {
        if (e.key === ' ' || e.key === 'Spacebar') {
            e.preventDefault();
            this.toggleFavorite();
        }
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

        this.onChangeCallbacks.forEach(callback => {
            callback(this.isFavorite, this.blogId);
        });

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

        /* ACCESSIBILITY: update toggle state */
        this.button.setAttribute('aria-pressed', String(this.isFavorite));
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
            this.button.removeEventListener('click', this.handleClick);
            this.button.removeEventListener('keydown', this.handleKeydown);
            this.button.remove();
        }
    }
}

/* Auto-initialize favorite buttons on page load */
document.addEventListener('DOMContentLoaded', function () {
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
        const buttonContainer =
            card.querySelector('.favorite-btn-container') || card;

        buttonContainer.appendChild(favoriteBtn.getButton());
    });
});
