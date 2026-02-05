document.addEventListener('DOMContentLoaded', () => {
    const forum = new ForumManager();
    forum.init();
});

class ForumManager {
    constructor() {
        this.apiBase = '/api/v1/forum';
        this.threadsContainer = document.getElementById('threads-feed');
        this.categoriesList = document.getElementById('categories-list');
        this.socket = null;
        this.currentToken = localStorage.getItem('token');
        this.currentUser = JSON.parse(localStorage.getItem('user') || '{}');
        this.currentCategoryId = null;
    }

    async init() {
        this.initSocket();
        await this.loadCategories();
        await this.loadThreads();
        this.setupEventListeners();
        this.loadUserStats();
    }

    initSocket() {
        this.socket = io('/forum', {
            auth: { token: this.currentToken }
        });

        this.socket.on('new_post_comment', (data) => {
            this.handleNewComment(data);
        });

        this.socket.on('user_typing', (data) => {
            this.showTypingIndicator(data);
        });
    }

    async loadCategories() {
        try {
            const resp = await fetch(`${this.apiBase}/categories`);
            const data = await resp.json();

            if (data.status === 'success') {
                this.renderCategories(data.data);
            }
        } catch (err) {
            console.error('Failed to load categories', err);
        }
    }

    async loadThreads(params = {}) {
        try {
            this.threadsContainer.innerHTML = '<div class="loader">Loading conversations...</div>';

            const queryParams = new URLSearchParams(params);
            if (this.currentCategoryId) queryParams.set('category_id', this.currentCategoryId);

            const resp = await fetch(`${this.apiBase}/threads?${queryParams.toString()}`);
            const data = await resp.json();

            if (data.status === 'success') {
                this.renderThreads(data.data);
            }
        } catch (err) {
            console.error('Failed to load threads', err);
        }
    }

    renderCategories(categories) {
        this.categoriesList.innerHTML = categories.map(cat => `
            <div class="category-item ${this.currentCategoryId === cat.id ? 'active' : ''}" 
                 onclick="forum.filterByCategory(${cat.id})">
                <span><i class="fas ${cat.icon || 'fa-folder'}"></i> ${cat.name}</span>
                <span class="count">${cat.thread_count}</span>
            </div>
        `).join('') + `
            <div class="category-item ${!this.currentCategoryId ? 'active' : ''}" 
                 onclick="forum.filterByCategory(null)">
                <span><i class="fas fa-list"></i> All Topics</span>
            </div>
        `;
    }

    renderThreads(threads) {
        if (threads.length === 0) {
            this.threadsContainer.innerHTML = '<div class="empty-state">No discussions found in this category. Start one!</div>';
            return;
        }

        this.threadsContainer.innerHTML = threads.map((thread, index) => `
            <div class="card thread-card ${thread.is_pinned ? 'pinned' : ''}" 
                 style="animation-delay: ${index * 0.1}s"
                 onclick="forum.viewThread(${thread.id})">
                <div class="author-info">
                    <div class="avatar">${thread.user_id ? 'U' : 'AI'}</div>
                    <div class="meta">
                        <div class="name">${thread.user_id ? 'Farmer Community Member' : 'AgriAI'}</div>
                        <div class="date">${formatDate(thread.created_at)}</div>
                    </div>
                </div>
                <h3 class="thread-title">${thread.title}</h3>
                <p class="thread-preview">${thread.content}</p>
                <div class="thread-tags">
                    ${thread.tags.map(tag => `<span class="tag">#${tag}</span>`).join('')}
                </div>
                <div class="thread-footer">
                    <span><i class="far fa-thumbs-up"></i> ${thread.upvote_count} Upvotes</span>
                    <span><i class="far fa-comment"></i> ${thread.comment_count} Replies</span>
                    <span><i class="far fa-eye"></i> ${thread.view_count} Views</span>
                </div>
            </div>
        `).join('');
    }

    setupEventListeners() {
        const searchInput = document.getElementById('forum-search');
        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.loadThreads({ q: e.target.value });
            }, 500);
        });

        document.getElementById('btn-new-thread').addEventListener('click', () => {
            this.toggleModal('create-thread-modal', true);
        });
    }

    async createThread() {
        const title = document.getElementById('thread-title-input').value;
        const content = document.getElementById('thread-content-input').value;
        const category_id = document.getElementById('thread-category-select').value;

        if (!title || !content || !category_id) {
            return Toast.error('Please fill in all required fields');
        }

        try {
            const resp = await fetch(`${this.apiBase}/threads`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.currentToken}`
                },
                body: JSON.stringify({ title, content, category_id, tags: [] })
            });

            const data = await resp.json();
            if (data.status === 'success') {
                Toast.success('Thread posted! AI is analyzing your content...');
                this.toggleModal('create-thread-modal', false);
                this.loadThreads();
            } else {
                Toast.error(data.message);
            }
        } catch (err) {
            Toast.error('Failed to post thread');
        }
    }

    filterByCategory(catId) {
        this.currentCategoryId = catId;
        this.loadCategories();
        this.loadThreads();
    }

    toggleModal(id, show) {
        const modal = document.getElementById(id);
        if (show) modal.classList.add('active');
        else modal.classList.remove('active');
    }

    async loadUserStats() {
        if (!this.currentUser.id) return;

        try {
            const resp = await fetch(`${this.apiBase}/reputation/${this.currentUser.id}`);
            const data = await resp.json();

            if (data.status === 'success') {
                const rep = data.data.reputation;
                document.getElementById('user-score').textContent = rep.total_score;
                document.getElementById('user-badge').innerHTML = rep.is_expert ?
                    '<span class="ai-badge">Expert</span>' : 'Member';
            }
        } catch (err) { }
    }

    // Modal open logic for thread details
    async viewThread(id) {
        // In a real app, this might navigate. For MVP, we'll open a full-page modal/detail view.
        // We'll simulate navigation for now
        window.location.hash = `thread/${id}`;
        // Implement detail view logic...
    }
}

// Helper Utilities
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = (now - date) / 1000;

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}

const Toast = {
    error: (msg) => Swal.fire({ icon: 'error', title: 'Error', text: msg, toast: true, position: 'top-end', showConfirmButton: false, timer: 3000 }),
    success: (msg) => Swal.fire({ icon: 'success', title: 'Success', text: msg, toast: true, position: 'top-end', showConfirmButton: false, timer: 3000 })
};

// Global instance access
window.forum = null;
document.addEventListener('DOMContentLoaded', () => { window.forum = new ForumManager(); window.forum.init(); });
