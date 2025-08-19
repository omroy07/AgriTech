

document.addEventListener("DOMContentLoaded", function () {
  const wrapper = document.querySelector('.header-navbar-wrapper');
  const main = document.querySelector('main');

  // Calculate height dynamically and set CSS variable
  const updateWrapperHeight = () => {
    const totalHeight = wrapper.offsetHeight;
    document.documentElement.style.setProperty('--header-navbar-height', totalHeight + 'px');
  };
  updateWrapperHeight();
  window.addEventListener('resize', updateWrapperHeight);

  let lastScrollTop = 0;
  let scrollTimeout;

  function handleScroll() {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTimeout) clearTimeout(scrollTimeout);

    if (currentScroll <= 10) {
      wrapper.style.transform = 'translateY(0)';
      lastScrollTop = currentScroll;
      return;
    }

    if (currentScroll > lastScrollTop && currentScroll > 100) {
      // Hide wrapper (header + navbar)
      wrapper.style.transform = 'translateY(-100%)';
    } else if (currentScroll < lastScrollTop) {
      // Show wrapper
      wrapper.style.transform = 'translateY(0)';
    }

    scrollTimeout = setTimeout(() => {
      wrapper.style.transform = 'translateY(0)';
    }, 1500);

    lastScrollTop = Math.max(currentScroll, 0);
  }

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        handleScroll();
        ticking = false;
      });
      ticking = true;
    }
  });

  // Newsletter form submission
  const newsletterForm = document.querySelector('.newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value;
      
      if (email) {
        // Show success message
        showNotification('Thank you for subscribing to our newsletter!', 'success');
        emailInput.value = '';
      }
    });
  }

  // Smooth scrolling for footer links
  const footerLinks = document.querySelectorAll('.footer-links a[href^="#"]');
  footerLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
});

// Notification function
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.textContent = message;
  
  // Add styles
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: ${type === 'success' ? '#4caf50' : '#2196f3'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    max-width: 300px;
    font-weight: 500;
  `;
  
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
  }, 100);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}
