document.addEventListener('DOMContentLoaded', function() {
  const feedbackForm = document.getElementById('feedbackForm');
  const thankYouMessage = document.getElementById('thankYouMessage');
  const feedbackTitle = document.querySelector('.feedback-title');
  const allFeedbacksSection = document.getElementById('allFeedbacks');
  const viewFeedbacksBtn = document.getElementById('viewFeedbacks');
  const feedbacksList = document.getElementById('feedbacksList');
  const feedbackTextarea = document.getElementById('feedback');
  const charCountElement = document.getElementById('charCount');

  // Initialize storage if it doesn't exist
  if (!window.localStorage || !localStorage.getItem('agritechFeedbacks')) {
    if (window.localStorage) {
      localStorage.setItem('agritechFeedbacks', JSON.stringify([]));
    } else {
      if (window.sessionStorage) {
        sessionStorage.setItem('agritechFeedbacks', JSON.stringify([]));
      } else {
        window.agritechFeedbacks = [];
      }
    }
  }

  // Character count functionality
  if (feedbackTextarea && charCountElement) {
    feedbackTextarea.addEventListener('input', function() {
      const charCount = this.value.length;
      charCountElement.textContent = charCount;
      
      if (charCount > 500) {
        charCountElement.style.color = '#f44336';
      } else if (charCount > 300) {
        charCountElement.style.color = '#ff9800';
      } else {
        charCountElement.style.color = '#999';
      }
    });
  }

  // Animate loading elements
  const inputs = document.querySelectorAll('input, textarea');
  inputs.forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
      if (this.value === '') {
        this.parentElement.classList.remove('focused');
      }
    });

    // Add input validation styling
    input.addEventListener('input', function() {
      if (this.checkValidity()) {
        this.classList.remove('invalid');
        this.classList.add('valid');
      } else {
        this.classList.remove('valid');
        this.classList.add('invalid');
      }
    });
  });

  // Button ripple effect
  const buttons = document.querySelectorAll('.submit-button');
  buttons.forEach(button => {
    button.addEventListener('click', function(e) {
      const ripple = this.querySelector('.button-ripple');
      if (ripple) {
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        
        ripple.style.animation = 'none';
        ripple.offsetHeight;
        ripple.style.animation = 'ripple 0.6s linear';
      }
    });
  });

  // Feedback form submission
  feedbackForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const submitButton = this.querySelector('.submit-button');
    const originalText = submitButton.innerHTML;
    
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Submitting...</span>';
    submitButton.disabled = true;
    
    setTimeout(() => {
      const feedbackData = {
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim() || 'Not provided',
        feedback: document.getElementById('feedback').value.trim(),
        date: new Date().toLocaleString(),
        id: Date.now() 
      };

      // Save to storage (localStorage, sessionStorage, or memory)
      let allFeedbacks = [];
      
      try {
        if (window.localStorage && localStorage.getItem('agritechFeedbacks')) {
          allFeedbacks = JSON.parse(localStorage.getItem('agritechFeedbacks'));
          allFeedbacks.push(feedbackData);
          localStorage.setItem('agritechFeedbacks', JSON.stringify(allFeedbacks));
        } else if (window.sessionStorage && sessionStorage.getItem('agritechFeedbacks')) {
          allFeedbacks = JSON.parse(sessionStorage.getItem('agritechFeedbacks'));
          allFeedbacks.push(feedbackData);
          sessionStorage.setItem('agritechFeedbacks', JSON.stringify(allFeedbacks));
        } else {
          window.agritechFeedbacks = window.agritechFeedbacks || [];
          window.agritechFeedbacks.push(feedbackData);
        }
      } catch (error) {
        console.warn('Storage not available, using in-memory storage');
        window.agritechFeedbacks = window.agritechFeedbacks || [];
        window.agritechFeedbacks.push(feedbackData);
      }

      feedbackForm.classList.add('hidden');
      document.querySelector('.feedback-header').classList.add('hidden');
      thankYouMessage.classList.remove('hidden');
      feedbackForm.reset();
      
      if (charCountElement) {
        charCountElement.textContent = '0';
        charCountElement.style.color = '#999';
      }
      
      submitButton.innerHTML = originalText;
      submitButton.disabled = false;
      
      inputs.forEach(input => {
        input.classList.remove('valid', 'invalid');
        input.parentElement.classList.remove('focused');
      });
      
    }, 1500); 
  });

  viewFeedbacksBtn.addEventListener('click', function() {
    thankYouMessage.classList.add('hidden');
    displayAllFeedbacks();
  });

  // Enhanced email validation
  const emailInput = document.getElementById('email');
  if (emailInput) {
    emailInput.addEventListener('blur', function() {
      if (this.value && !validateEmail(this.value)) {
        this.classList.add('invalid');
        showTooltip(this, 'Please enter a valid email address');
      } else {
        this.classList.remove('invalid');
        hideTooltip(this);
      }
    });
    
    emailInput.addEventListener('input', function() {
      if (this.value === '' || validateEmail(this.value)) {
        this.classList.remove('invalid');
        hideTooltip(this);
      }
    });
  }

  // Enhanced display all feedbacks function
  function displayAllFeedbacks() {
    let allFeedbacks = [];
    
    try {
      if (window.localStorage && localStorage.getItem('agritechFeedbacks')) {
        allFeedbacks = JSON.parse(localStorage.getItem('agritechFeedbacks'));
      } else if (window.sessionStorage && sessionStorage.getItem('agritechFeedbacks')) {
        allFeedbacks = JSON.parse(sessionStorage.getItem('agritechFeedbacks'));
      } else {
        allFeedbacks = window.agritechFeedbacks || [];
      }
    } catch (error) {
      allFeedbacks = window.agritechFeedbacks || [];
    }
    
    allFeedbacksSection.classList.remove('hidden');
    
    if (allFeedbacks.length === 0) {
      feedbacksList.innerHTML = `
        <div class="no-feedback">
          <i class="fas fa-inbox" style="font-size: 3rem; color: #ccc; margin-bottom: 20px;"></i>
          <p style="color: #999; font-size: 1.1rem;">No feedback submissions yet.</p>
          <p style="color: #666; font-size: 0.9rem;">Be the first to share your thoughts!</p>
        </div>
      `;
      return;
    }

    // Sort feedbacks by date (newest first)
    allFeedbacks.sort((a, b) => new Date(b.date) - new Date(a.date));

    feedbacksList.innerHTML = allFeedbacks.map((fb, index) => `
      <div class="feedback-item" style="animation-delay: ${index * 0.1}s">
        <div class="feedback-header-item">
          <h4><i class="fas fa-user-circle" style="color: #4caf50; margin-right: 8px;"></i>${escapeHtml(fb.name)}</h4>
          ${fb.email !== 'Not provided' ? `<p style="color: #666; font-size: 0.9rem; margin: 5px 0;"><i class="fas fa-envelope" style="color: #4caf50; margin-right: 8px;"></i>${escapeHtml(fb.email)}</p>` : ''}
        </div>
        <div class="feedback-content">
          <p><i class="fas fa-quote-left" style="color: #4caf50; margin-right: 8px;"></i>${escapeHtml(fb.feedback)}</p>
        </div>
        <div class="feedback-meta">
          <span>Submission #${allFeedbacks.length - index}</span>
          <span>•</span>
          <span>${formatDate(fb.date)}</span>
        </div>
      </div>
    `).join('');

    const items = feedbacksList.querySelectorAll('.feedback-item');
    items.forEach((item, index) => {
      setTimeout(() => {
        item.style.opacity = '1';
        item.style.transform = 'translateY(0)';
      }, index * 100);
    });
  }

  // Utility functions
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
      return 'Today';
    } else if (diffDays === 2) {
      return 'Yesterday';
    } else if (diffDays <= 7) {
      return `${diffDays - 1} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  function showTooltip(element, message) {
    hideTooltip(element); 
    
    const tooltip = document.createElement('div');
    tooltip.className = 'validation-tooltip';
    tooltip.textContent = message;
    tooltip.style.cssText = `
      position: absolute;
      background: #f44336;
      color: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
      white-space: nowrap;
      z-index: 1000;
      opacity: 0;
      transform: translateY(-5px);
      transition: all 0.3s ease;
      pointer-events: none;
    `;
    
    element.parentElement.style.position = 'relative';
    element.parentElement.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    tooltip.style.top = '-35px';
    tooltip.style.left = '0';
    
    // Add arrow
    const arrow = document.createElement('div');
    arrow.style.cssText = `
      position: absolute;
      top: 100%;
      left: 20px;
      border: 6px solid transparent;
      border-top-color: #f44336;
    `;
    tooltip.appendChild(arrow);
    
    // Animate in
    setTimeout(() => {
      tooltip.style.opacity = '1';
      tooltip.style.transform = 'translateY(0)';
    }, 10);
  }

  function hideTooltip(element) {
    const existingTooltip = element.parentElement.querySelector('.validation-tooltip');
    if (existingTooltip) {
      existingTooltip.style.opacity = '0';
      existingTooltip.style.transform = 'translateY(-5px)';
      setTimeout(() => {
        existingTooltip.remove();
      }, 300);
    }
  }

  // Add smooth scrolling for better UX
  function smoothScrollTo(element) {
    element.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });
  }

  // Add keyboard navigation support
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      if (!allFeedbacksSection.classList.contains('hidden')) {
        allFeedbacksSection.classList.add('hidden');
        thankYouMessage.classList.remove('hidden');
      } else if (!thankYouMessage.classList.contains('hidden')) {
        thankYouMessage.classList.add('hidden');
        feedbackForm.classList.remove('hidden');
        document.querySelector('.feedback-header').classList.remove('hidden');
      }
    }
  });

  // Initialize character count on page load
  if (feedbackTextarea && charCountElement) {
    charCountElement.textContent = feedbackTextarea.value.length;
  }

  // Add focus trap for better accessibility
  function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', function(e) {
      if (e.key === 'Tab') {
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    });
  }

  // Apply focus trap to main container
  trapFocus(document.querySelector('.feedback-container'));

  console.log('Enhanced AgriTech Feedback System loaded successfully!');
});