/**
 * AgriTech Unified Alert Manager
 * Manages real-time alerts, notifications, and cross-module communications.
 */

class AlertManager {
    constructor() {
        this.socket = null;
        this.userId = null;
        this.alerts = [];
        this.unreadCount = 0;
        this.containerId = 'alert-notification-hub';
        this.badgeId = 'alert-badge-count';

        this.init();
    }

    init() {
        // Try to get user from global session or local storage
        const userStr = localStorage.getItem('user');
        if (userStr) {
            try {
                const user = JSON.parse(userStr);
                this.userId = user.id;
            } catch (e) {
                console.error('Failed to parse user data:', e);
            }
        }

        // Initialize Socket.IO connection
        this.socket = typeof io !== 'undefined' ? io() : null;
        if (this.socket) {
            this.setupSocketHandlers();
        } else {
            console.warn('Socket.IO not found. Real-time alerts disabled.');
        }

        // Load historical alerts
        this.fetchAlerts();

        // Setup UI listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.updateUI();
        });
    }

    setupSocketHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to Alert System');
            if (this.userId) {
                this.socket.emit('subscribe_alerts', { user_id: this.userId });
            } else {
                this.socket.emit('subscribe_alerts', {}); // Global only
            }
        });

        this.socket.on('new_alert', (alert) => {
            console.log('New Alert Received:', alert);
            this.handleIncomingAlert(alert);
        });

        this.socket.on('subscription_success', (data) => {
            console.log('Subscribed to room:', data.room);
        });
    }

    async fetchAlerts() {
        if (!this.userId) return;

        try {
            const response = await fetch(`/api/v1/alerts/?user_id=${this.userId}`);
            if (response.ok) {
                const data = await response.json();
                this.alerts = data.alerts || [];
                this.updateMetadata();
                this.updateUI();
            }
        } catch (error) {
            console.error('Failed to fetch alerts:', error);
        }
    }

    handleIncomingAlert(alert) {
        // Add to list
        this.alerts.unshift(alert);

        // Play sound if high priority
        if (['HIGH', 'CRITICAL'].includes(alert.priority)) {
            this.playAlertSound();
        }

        // Show toast
        this.showToast(alert);

        // Update state
        this.updateMetadata();
        this.updateUI();
    }

    updateMetadata() {
        this.unreadCount = this.alerts.filter(a => !a.read_at).length;
    }

    updateUI() {
        // Update badge
        const badge = document.getElementById(this.badgeId);
        if (badge) {
            badge.textContent = this.unreadCount;
            badge.style.display = this.unreadCount > 0 ? 'inline-flex' : 'none';
        }

        // Update list if open
        const container = document.getElementById(this.containerId);
        if (container) {
            this.renderAlertList(container);
        }
    }

    renderAlertList(container) {
        if (this.alerts.length === 0) {
            container.innerHTML = '<div class="alert-empty">No new alerts</div>';
            return;
        }

        const html = this.alerts.map(alert => `
            <div class="alert-item ${alert.read_at ? 'read' : 'unread'} priority-${alert.priority.toLowerCase()}" 
                 onclick="alertManager.markAsRead(${alert.id})">
                <div class="alert-meta">
                    <span class="alert-category">${alert.category}</span>
                    <span class="alert-time">${this.formatTime(alert.created_at)}</span>
                </div>
                <div class="alert-title">${alert.title}</div>
                <div class="alert-message">${alert.message}</div>
                ${alert.action_url ? `<a href="${alert.action_url}" class="alert-action">Take Action</a>` : ''}
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async markAsRead(alertId) {
        try {
            const response = await fetch(`/api/v1/alerts/${alertId}/read`, { method: 'POST' });
            if (response.ok) {
                const alert = this.alerts.find(a => a.id === alertId);
                if (alert) {
                    alert.read_at = new Date().toISOString();
                    this.updateMetadata();
                    this.updateUI();
                }
            }
        } catch (error) {
            console.error('Error marking alert as read:', error);
        }
    }

    showToast(alert) {
        const toast = document.createElement('div');
        toast.className = `alert-toast priority-${alert.priority.toLowerCase()}`;
        toast.innerHTML = `
            <div class="toast-body">
                <strong>${alert.title}</strong>
                <p>${alert.message}</p>
            </div>
        `;
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 500);
            }, 5000);
        }, 100);
    }

    playAlertSound() {
        // Audio implementation placeholder
        console.log('Playing alert sound...');
    }

    formatTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}

// Initialize globally
const alertManager = new AlertManager();
window.alertManager = alertManager;
