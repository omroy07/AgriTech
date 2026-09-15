/**
 * AgriTech - Footer Newsletter & Subscription Handler
 */
(function () {
  'use strict';
  // If root footer.js already executed, return
  if (window.handleNewsletterSubmit) return;
  
  const STORAGE_KEY = 'agritech_newsletter_subscribers';

  function getSubscribers() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (e) {
      return [];
    }
  }

  function saveSubscribers(list) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    } catch (e) {}
  }

  function isValidEmail(email) {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return re.test(String(email).toLowerCase().trim());
  }

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

    setTimeout(() => {
      if (feedbackEl && type !== 'success') {
        feedbackEl.style.display = 'none';
      }
    }, 6000);
  }

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

    if (!email || !isValidEmail(email)) {
      showFeedback(form, 'Please enter a valid email address.', 'error');
      emailInput.focus();
      return false;
    }

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

      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
          window.closeUnsubscribeModal();
        }
      });
    }
    return modal;
  }

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

  function closeUnsubscribeModal() {
    const modal = document.getElementById('agritechUnsubscribeModal');
    if (modal) {
      modal.classList.remove('active');
    }
  }

  function handleNewsletterUnsubscribeSubmit(event, formElement) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
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

  function initNewsletter() {
    const year = new Date().getFullYear();
    document.querySelectorAll('#current-year, .current-year').forEach(el => {
      el.textContent = year;
    });

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

  window.handleNewsletterSubmit = handleNewsletterSubmit;
  window.handleNewsletterSubscribe = handleNewsletterSubmit;
  window.openUnsubscribeModal = openUnsubscribeModal;
  window.closeUnsubscribeModal = closeUnsubscribeModal;
  window.handleNewsletterUnsubscribeSubmit = handleNewsletterUnsubscribeSubmit;
  window.handleNewsletterUnsubscribe = function (e) {
    if (e && e.preventDefault) e.preventDefault();
    openUnsubscribeModal(e);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNewsletter);
  } else {
    initNewsletter();
  }
})();
