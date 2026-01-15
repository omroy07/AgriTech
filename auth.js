// Authentication System for AgriTech
class AuthManager {
  constructor() {
    this.users = this.loadUsers();
    this.currentUser = this.getCurrentUser();
  }

  // Load users from localStorage
  loadUsers() {
    try {
      const users = localStorage.getItem('agritech_users');
      return users ? JSON.parse(users) : [];
    } catch (error) {
      console.error('Error loading users:', error);
      return [];
    }
  }

  // Save users to localStorage
  saveUsers() {
    try {
      localStorage.setItem('agritech_users', JSON.stringify(this.users));
    } catch (error) {
      console.error('Error saving users:', error);
    }
  }

  // Simple password hashing (in production, use proper bcrypt)
  hashPassword(password) {
    // Simple hash function for demo - in production use proper bcrypt
    let hash = 0;
    for (let i = 0; i < password.length; i++) {
      const char = password.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }

  // Validate email format
  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Validate password strength
  validatePassword(password) {
    if (password.length < 8) {
      return { valid: false, message: 'Password must be at least 8 characters long' };
    }
    if (!/[a-z]/.test(password)) {
      return { valid: false, message: 'Password must contain at least one lowercase letter' };
    }
    if (!/[A-Z]/.test(password)) {
      return { valid: false, message: 'Password must contain at least one uppercase letter' };
    }
    if (!/\d/.test(password)) {
      return { valid: false, message: 'Password must contain at least one number' };
    }
    return { valid: true, message: 'Password is strong' };
  }

  // Register new user
  register(userData) {
    const { role, fullname, email, password } = userData;

    // Validate input
    if (!role || !fullname || !email || !password) {
      return { success: false, message: 'All fields are required' };
    }

    if (!this.validateEmail(email)) {
      return { success: false, message: 'Please enter a valid email address' };
    }

    const passwordValidation = this.validatePassword(password);
    if (!passwordValidation.valid) {
      return { success: false, message: passwordValidation.message };
    }

    // Check if user already exists
    const existingUser = this.users.find(user => user.email.toLowerCase() === email.toLowerCase());
    if (existingUser) {
      return { success: false, message: 'An account with this email already exists' };
    }

    // Create new user
    const newUser = {
      id: Date.now().toString(),
      role: role,
      fullname: fullname.trim(),
      email: email.toLowerCase().trim(),
      password: this.hashPassword(password),
      createdAt: new Date().toISOString(),
      isActive: true
    };

    this.users.push(newUser);
    this.saveUsers();

    return { success: true, message: 'Account created successfully!', user: newUser };
  }

  // Login user
  login(email, password) {
    if (!email || !password) {
      return { success: false, message: 'Email and password are required' };
    }

    if (!this.validateEmail(email)) {
      return { success: false, message: 'Please enter a valid email address' };
    }

    // Find user
    const user = this.users.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (!user) {
      return { success: false, message: 'Invalid email or password' };
    }

    // Check password
    const hashedPassword = this.hashPassword(password);
    if (user.password !== hashedPassword) {
      return { success: false, message: 'Invalid email or password' };
    }

    if (!user.isActive) {
      return { success: false, message: 'Account is deactivated. Please contact support.' };
    }

    // Update last login
    user.lastLogin = new Date().toISOString();
    this.saveUsers();

    // Set current user session
    this.setCurrentUser(user);

    return { success: true, message: 'Login successful!', user: user };
  }

  // Set current user session
  setCurrentUser(user) {
    try {
      const userSession = {
        id: user.id,
        email: user.email,
        fullname: user.fullname,
        role: user.role,
        loginTime: new Date().toISOString()
      };
      localStorage.setItem('agritech_current_user', JSON.stringify(userSession));
      this.currentUser = userSession;
    } catch (error) {
      console.error('Error setting current user:', error);
    }
  }

  // Get current user session
  getCurrentUser() {
    try {
      const user = localStorage.getItem('agritech_current_user');
      return user ? JSON.parse(user) : null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  // Check if user is logged in
  isLoggedIn() {
    return this.currentUser !== null;
  }

  // Logout user
  logout() {
    try {
      localStorage.removeItem('agritech_current_user');
      this.currentUser = null;
      return { success: true, message: 'Logged out successfully' };
    } catch (error) {
      console.error('Error during logout:', error);
      return { success: false, message: 'Error during logout' };
    }
  }

  // Get user by email
  getUserByEmail(email) {
    return this.users.find(user => user.email.toLowerCase() === email.toLowerCase());
  }

  // Update user profile
  updateUser(userId, updates) {
    const userIndex = this.users.findIndex(user => user.id === userId);
    if (userIndex === -1) {
      return { success: false, message: 'User not found' };
    }

    // Update user data
    this.users[userIndex] = { ...this.users[userIndex], ...updates, updatedAt: new Date().toISOString() };
    this.saveUsers();

    // Update current session if it's the same user
    if (this.currentUser && this.currentUser.id === userId) {
      this.setCurrentUser(this.users[userIndex]);
    }

    return { success: true, message: 'Profile updated successfully', user: this.users[userIndex] };
  }

  // Get all users (admin function)
  getAllUsers() {
    return this.users.map(user => ({
      id: user.id,
      role: user.role,
      fullname: user.fullname,
      email: user.email,
      createdAt: user.createdAt,
      lastLogin: user.lastLogin,
      isActive: user.isActive
    }));
  }

  // Delete user account
  deleteUser(userId) {
    const userIndex = this.users.findIndex(user => user.id === userId);
    if (userIndex === -1) {
      return { success: false, message: 'User not found' };
    }

    this.users.splice(userIndex, 1);
    this.saveUsers();

    // Logout if current user is deleted
    if (this.currentUser && this.currentUser.id === userId) {
      this.logout();
    }

    return { success: true, message: 'Account deleted successfully' };
  }

  // Change password
  changePassword(userId, currentPassword, newPassword) {
    const user = this.users.find(u => u.id === userId);
    if (!user) {
      return { success: false, message: 'User not found' };
    }

    // Verify current password
    const hashedCurrentPassword = this.hashPassword(currentPassword);
    if (user.password !== hashedCurrentPassword) {
      return { success: false, message: 'Current password is incorrect' };
    }

    // Validate new password
    const passwordValidation = this.validatePassword(newPassword);
    if (!passwordValidation.valid) {
      return { success: false, message: passwordValidation.message };
    }

    // Update password
    user.password = this.hashPassword(newPassword);
    user.updatedAt = new Date().toISOString();
    this.saveUsers();

    return { success: true, message: 'Password changed successfully' };
  }

  // Reset password (simplified - in production, use email verification)
  resetPassword(email) {
    const user = this.users.find(u => u.email.toLowerCase() === email.toLowerCase());
    if (!user) {
      return { success: false, message: 'No account found with this email address' };
    }

    // Generate temporary password
    const tempPassword = Math.random().toString(36).slice(-8);
    user.password = this.hashPassword(tempPassword);
    user.updatedAt = new Date().toISOString();
    this.saveUsers();

    // In production, send this via email
    return {
      success: true,
      message: 'Password reset successfully',
      tempPassword: tempPassword
    };
  }
}

// Initialize global auth manager
window.authManager = new AuthManager();

// Utility functions for UI
function showAuthMessage(message, type = 'info') {
  // Remove existing messages
  const existingMessage = document.querySelector('.auth-message');
  if (existingMessage) {
    existingMessage.remove();
  }

  const messageDiv = document.createElement('div');
  messageDiv.className = `auth-message auth-message-${type}`;
  messageDiv.innerHTML = `
    <div class="auth-message-content">
      <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
      <span>${message}</span>
    </div>
  `;

  // Add styles
  messageDiv.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    padding: 15px 20px;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    animation: slideInRight 0.3s ease-out;
    max-width: 400px;
  `;

  if (type === 'success') {
    messageDiv.style.background = 'linear-gradient(135deg, #4caf50, #45a049)';
  } else if (type === 'error') {
    messageDiv.style.background = 'linear-gradient(135deg, #f44336, #e53935)';
  } else {
    messageDiv.style.background = 'linear-gradient(135deg, #2196f3, #1976d2)';
  }

  document.body.appendChild(messageDiv);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (messageDiv.parentNode) {
      messageDiv.style.animation = 'slideOutRight 0.3s ease-out';
      setTimeout(() => {
        if (messageDiv.parentNode) {
          messageDiv.remove();
        }
      }, 300);
    }
  }, 5000);
}

// Add CSS animations
const authStyles = document.createElement('style');
authStyles.textContent = `
  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(100%);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes slideOutRight {
    from {
      opacity: 1;
      transform: translateX(0);
    }
    to {
      opacity: 0;
      transform: translateX(100%);
    }
  }

  .auth-message-content {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .auth-message-content i {
    font-size: 1.2rem;
  }
`;
document.head.appendChild(authStyles);

// Check authentication on protected pages
function requireAuth() {
  if (!window.authManager.isLoggedIn()) {
    showAuthMessage('Please log in to access this page', 'error');
    setTimeout(() => {
      window.location.href = 'login.html';
    }, 2000);
    return false;
  }
  return true;
}

// Redirect if already logged in
function redirectIfLoggedIn() {
  if (window.authManager.isLoggedIn()) {
    window.location.href = 'main.html';
  }
}

// Update UI based on auth state
AuthManager.prototype.updateAuthUI = function () {
  const isLoggedIn = this.isLoggedIn();
  const user = this.currentUser;

  // Desktop Header Elements
  const loginBtn = document.querySelector('.login-btn-desktop'); // Add this class to HTML
  const registerBtn = document.querySelector('.register-btn-desktop'); // Add this class to HTML
  const logoutBtn = document.querySelector('.logout-button');
  const profileLink = document.querySelector('.profile-link'); // Optional: Add profile link

  // Mobile Menu Elements
  const mobileLoginLink = document.querySelector('a[href="login.html"].mobile-link');
  const mobileRegisterLink = document.querySelector('a[href="register.html"].mobile-link');
  const mobileLogoutLink = document.getElementById('mobile-logout-link'); // Add this to HTML

  if (isLoggedIn) {
    // Desktop: Hide Login/Register, Show Logout
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
    if (logoutBtn) {
      logoutBtn.style.display = 'inline-flex';
      logoutBtn.onclick = (e) => {
        e.preventDefault();
        this.logout();
        window.location.reload();
      };
    }

    // Mobile: Hide Login/Register, Show Logout
    if (mobileLoginLink) mobileLoginLink.style.display = 'none';
    if (mobileRegisterLink) mobileRegisterLink.style.display = 'none';

    // Check if mobile logout link exists, if not create it in mobile menu
    if (!mobileLogoutLink) {
      const mobileLinksContainer = document.querySelector('.mobile-links');
      if (mobileLinksContainer) {
        const logoutLink = document.createElement('a');
        logoutLink.href = "#";
        logoutLink.id = "mobile-logout-link";
        logoutLink.className = "mobile-link";
        logoutLink.innerHTML = `
                <i class="fas fa-sign-out-alt"></i>
                <span>Logout</span>
                <i class="fas fa-chevron-right link-arrow"></i>
            `;
        logoutLink.onclick = (e) => {
          e.preventDefault();
          this.logout();
          window.location.reload();
        };
        mobileLinksContainer.appendChild(logoutLink);
      }
    } else {
      mobileLogoutLink.style.display = 'flex';
    }

  } else {
    // Desktop: Show Login/Register, Hide Logout
    if (loginBtn) loginBtn.style.display = 'inline-flex';
    if (registerBtn) registerBtn.style.display = 'inline-flex';
    if (logoutBtn) logoutBtn.style.display = 'none';

    // Mobile: Show Login/Register, Hide Logout
    if (mobileLoginLink) mobileLoginLink.style.display = 'flex';
    if (mobileRegisterLink) mobileRegisterLink.style.display = 'flex';
    if (mobileLogoutLink) mobileLogoutLink.style.display = 'none';
  }
};

// Initialize global auth manager and UI
window.authManager = new AuthManager();

// Run UI update on load
document.addEventListener('DOMContentLoaded', () => {
  window.authManager.updateAuthUI();
});
