/**
 * AgriTech - Footer Newsletter & Subscription Handler + Global Logo Redirect
 * Provides seamless client-side subscription validation, localStorage persistence,
 * confirmation notifications, email marketing compliance with an Unsubscribe modal,
 * and automatic homepage redirection when clicking website logos.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'agritech_newsletter_subscribers';

  // Helper: Retrieve subscribers list
  function getSubscribers() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      console.warn('LocalStorage error:', e);
      return [];
    }
  }

  // Helper: Save subscribers list
  function saveSubscribers(list) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {
      console.warn('LocalStorage error:', e);
    }
  }

  // Helper: Validate email format
  function isValidEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase().trim());
  }

  // Display feedback message in a form
  function showFeedback(form, message, type) {
    let feedbackEl = form.querySelector('.newsletter-feedback') || form.querySelector('.newsletter-message');
    if (!feedbackEl) {
      feedbackEl = document.createElement('div');
      feedbackEl.className = 'newsletter-feedback';
      form.appendChild(feedbackEl);
    }

    feedbackEl.className = `newsletter-feedback newsletter-${type}`;
    let icon = 'fas fa-info-circle';
    if (type === 'success') icon = 'fas fa-check-circle';
    if (type === 'error') icon = 'fas fa-exclamation-circle';

    feedbackEl.innerHTML = `<i class="${icon}"></i> <span>${message}</span>`;
    feedbackEl.style.display = 'flex';

    // Auto-hide error/info after 6s, keep success visible slightly longer
    setTimeout(() => {
      if (feedbackEl && type !== 'success') {
        feedbackEl.style.display = 'none';
      }
    }, 6000);
  }

  // Handle Newsletter Form Submit
  function handleNewsletterSubmit(event, formElement) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    const form = formElement || (event ? event.target : null);
    if (!form) return false;

    const emailInput = form.querySelector('input[type="email"]') || form.querySelector('.newsletter-input');
    const submitBtn = form.querySelector('button[type="submit"]') || form.querySelector('.newsletter-btn');

    if (!emailInput) return false;

    const email = emailInput.value.trim().toLowerCase();

    if (!email) {
      showFeedback(form, 'Please enter your email address.', 'error');
      emailInput.focus();
      return false;
    }

    if (!isValidEmail(email)) {
      showFeedback(form, 'Please enter a valid email address.', 'error');
      emailInput.focus();
      return false;
    }

    // Button loading animation
    const originalBtnHTML = submitBtn ? submitBtn.innerHTML : 'Subscribe';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subscribing...';
    }

    setTimeout(() => {
      const subscribers = getSubscribers();
      const existing = subscribers.find(s => s.email === email);

      if (existing) {
        showFeedback(form, 'You are already subscribed to our newsletter! 🌱', 'info');
      } else {
        subscribers.push({
          email: email,
          subscribedAt: new Date().toISOString()
        });
        saveSubscribers(subscribers);
        showFeedback(form, 'Thank you for subscribing! Welcome to AgriTech.', 'success');
        emailInput.value = '';
      }

      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnHTML;
      }
    }, 450);

    return false;
  }

  // Ensure Unsubscribe Modal exists in DOM
  function ensureUnsubscribeModal() {
    let modal = document.getElementById('agritechUnsubscribeModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'agritechUnsubscribeModal';
      modal.className = 'agritech-modal';
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-labelledby', 'unsubModalTitle');
      modal.innerHTML = `
        <div class="agritech-modal-backdrop" onclick="window.closeUnsubscribeModal()"></div>
        <div class="agritech-modal-dialog">
          <div class="agritech-modal-header">
            <h3 id="unsubModalTitle"><i class="fas fa-envelope-open-text"></i> Newsletter Preferences</h3>
            <button type="button" class="agritech-modal-close" onclick="window.closeUnsubscribeModal()" aria-label="Close dialog">&times;</button>
          </div>
          <div class="agritech-modal-body">
            <p>Enter your email address below to unsubscribe from AgriTech newsletter and product updates.</p>
            <form id="unsubForm" onsubmit="return window.handleNewsletterUnsubscribeSubmit(event, this)">
              <div class="newsletter-input-group modal-input-group">
                <input type="email" id="unsubEmailInput" class="newsletter-input" placeholder="Enter your registered email..." required aria-label="Unsubscribe email address">
              </div>
              <div id="unsubFeedback" class="newsletter-feedback" style="display:none;" role="status"></div>
              <div class="agritech-modal-actions">
                <button type="button" class="agritech-btn-secondary" onclick="window.closeUnsubscribeModal()">Cancel</button>
                <button type="submit" class="agritech-btn-danger" id="unsubSubmitBtn">
                  <i class="fas fa-user-minus"></i> Unsubscribe
                </button>
              </div>
            </form>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      // Close on Esc key
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
          window.closeUnsubscribeModal();
        }
      });
    }
    return modal;
  }

  // Open Unsubscribe Modal
  function openUnsubscribeModal(e) {
    if (e && e.preventDefault) e.preventDefault();
    const modal = ensureUnsubscribeModal();
    modal.classList.add('active');
    const input = document.getElementById('unsubEmailInput');
    const feedback = document.getElementById('unsubFeedback');
    if (feedback) feedback.style.display = 'none';
    if (input) {
      input.value = '';
      setTimeout(() => input.focus(), 100);
    }
  }

  // Close Unsubscribe Modal
  function closeUnsubscribeModal() {
    const modal = document.getElementById('agritechUnsubscribeModal');
    if (modal) {
      modal.classList.remove('active');
    }
  }

  // Handle Unsubscribe submit
  function handleNewsletterUnsubscribeSubmit(event, formElement) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    const form = formElement || document.getElementById('unsubForm');
    const input = document.getElementById('unsubEmailInput');
    const feedback = document.getElementById('unsubFeedback');
    const btn = document.getElementById('unsubSubmitBtn');

    if (!input || !feedback) return false;
    const email = input.value.trim().toLowerCase();

    if (!email || !isValidEmail(email)) {
      feedback.className = 'newsletter-feedback newsletter-error';
      feedback.innerHTML = '<i class="fas fa-exclamation-circle"></i> <span>Please enter a valid email address.</span>';
      feedback.style.display = 'flex';
      return false;
    }

    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    }

    setTimeout(() => {
      const subscribers = getSubscribers();
      const index = subscribers.findIndex(s => s.email === email);

      if (index !== -1) {
        subscribers.splice(index, 1);
        saveSubscribers(subscribers);
        feedback.className = 'newsletter-feedback newsletter-success';
        feedback.innerHTML = '<i class="fas fa-check-circle"></i> <span>You have been unsubscribed successfully.</span>';
        feedback.style.display = 'flex';
        input.value = '';
        setTimeout(() => {
          closeUnsubscribeModal();
        }, 2200);
      } else {
        feedback.className = 'newsletter-feedback newsletter-info';
        feedback.innerHTML = '<i class="fas fa-info-circle"></i> <span>This email was not found in our active subscriber list.</span>';
        feedback.style.display = 'flex';
      }

      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-user-minus"></i> Unsubscribe';
      }
    }, 400);

    return false;
  }

  // Handle Logo Click Redirect to Homepage
  function initLogoRedirect() {
    const logoSelectors = [
      '.brand',
      '.nav-brand',
      '.brand-header',
      '.logo',
      '.nav-logo',
      '.footer-logo',
      '.brand-logo',
      '.site-logo',
      '.header-logo',
      '.sidebar-brand',
      'img[src*="logo.png"]',
      'img[alt*="logo" i]',
      'img[alt*="AgriTech" i]'
    ];

    let homeUrl = 'index.html';
    const scriptEl = document.querySelector('script[src*="footer.js"]');
    if (scriptEl) {
      const src = scriptEl.getAttribute('src') || '';
      homeUrl = src.replace('footer.js', 'index.html');
      if (homeUrl === '') homeUrl = 'index.html';
    }

    document.querySelectorAll(logoSelectors.join(',')).forEach(el => {
      const parentLink = el.closest('a');
      if (parentLink) {
        const href = parentLink.getAttribute('href');
        if (!href || href === '#' || href === '' || href === 'javascript:void(0)') {
          parentLink.setAttribute('href', homeUrl);
        }
        parentLink.style.cursor = 'pointer';
        return;
      }

      if (el.tagName.toLowerCase() === 'a') {
        const href = el.getAttribute('href');
        if (!href || href === '#' || href === '' || href === 'javascript:void(0)') {
          el.setAttribute('href', homeUrl);
        }
        el.style.cursor = 'pointer';
        return;
      }

      el.style.cursor = 'pointer';
      el.setAttribute('role', 'link');
      el.setAttribute('tabindex', '0');
      el.setAttribute('title', 'Go to AgriTech Homepage');
      el.setAttribute('aria-label', 'AgriTech Homepage');

      if (!el.dataset.logoRedirectAttached) {
        el.dataset.logoRedirectAttached = 'true';
        el.addEventListener('click', function (e) {
          if (e.target.closest('button') || e.target.closest('input') || (e.target.closest('a') && e.target.closest('a') !== el)) {
            return;
          }
          window.location.href = homeUrl;
        });
        el.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            window.location.href = homeUrl;
          }
        });
      }
    });
  }

  // Initialize all newsletter forms and logo redirects on page
  function initNewsletter() {
    // Dynamic Year updater
    const year = new Date().getFullYear();
    document.querySelectorAll('#current-year, .current-year').forEach(el => {
      el.textContent = year;
    });

    // Initialize logo redirect
    initLogoRedirect();

    // Attach submit handlers
    const forms = document.querySelectorAll('.newsletter-form, [data-newsletter-form]');
    forms.forEach(form => {
      if (!form.dataset.initialized) {
        form.dataset.initialized = 'true';
        form.addEventListener('submit', function (e) {
          handleNewsletterSubmit(e, form);
        });
      }
    });
  }

  // Expose methods to global scope
  window.handleNewsletterSubmit = handleNewsletterSubmit;
  window.handleNewsletterSubscribe = handleNewsletterSubmit;
  window.openUnsubscribeModal = openUnsubscribeModal;
  window.closeUnsubscribeModal = closeUnsubscribeModal;
  window.handleNewsletterUnsubscribeSubmit = handleNewsletterUnsubscribeSubmit;
  window.handleNewsletterUnsubscribe = function (e) {
    if (e && e.preventDefault) e.preventDefault();
    openUnsubscribeModal(e);
  };
  window.initLogoRedirect = initLogoRedirect;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNewsletter);
  } else {
    initNewsletter();
  }
})();
