document.addEventListener("DOMContentLoaded", function () {
  const images = document.querySelectorAll('img[loading="lazy"]');
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.src && img.complete) {
          img.style.opacity = "1";
        } else {
          img.addEventListener("load", () => {
            img.style.opacity = "1";
          });
        }
        observer.unobserve(img);
      }
    });
  });
  images.forEach((img) => {
    img.style.opacity = "0";
    img.style.transition = "opacity 0.3s ease";
    imageObserver.observe(img);
  });
  
  document.querySelectorAll('nav a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
  
  // Add click ripple effect to grid items
  document.querySelectorAll(".grid-item").forEach((item) => {
    item.addEventListener("click", function (e) {
      const ripple = document.createElement("div");
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      ripple.style.cssText = `
                        position: absolute;
                        width: ${size}px;
                        height: ${size}px;
                        left: ${x}px;
                        top: ${y}px;
                        background: rgba(76, 175, 80, 0.3);
                        border-radius: 50%;
                        transform: scale(0);
                        animation: ripple 0.6s ease-out;
                        pointer-events: none;
                        z-index: 1;
                    `;
      this.appendChild(ripple);
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });

  // Header and Nav hide/show on scroll functionality
  let lastScrollTop = 0;
  let scrollTimeout;
  const headerNavWrapper = document.querySelector('.header-nav-wrapper');
  
  // Add CSS for smooth transitions
  if (headerNavWrapper) {
    headerNavWrapper.style.cssText = `
      position: sticky;
      top: 0;
      z-index: 1000;
      transition: transform 0.3s ease-in-out;
      transform: translateY(0);
    `;
  }
  
  function handleScroll() {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
    
    // Clear the timeout if it exists
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }
    
    // Don't hide/show if we're at the very top
    if (currentScroll <= 10) {
      headerNavWrapper.style.transform = 'translateY(0)';
      lastScrollTop = currentScroll;
      return;
    }
    
    // Scrolling down - hide header/nav
    if (currentScroll > lastScrollTop && currentScroll > 100) {
      headerNavWrapper.style.transform = 'translateY(-100%)';
    }
    // Scrolling up - show header/nav
    else if (currentScroll < lastScrollTop) {
      headerNavWrapper.style.transform = 'translateY(0)';
    }
    
    // Set a timeout to show header/nav if user stops scrolling
    scrollTimeout = setTimeout(() => {
      headerNavWrapper.style.transform = 'translateY(0)';
    }, 1500);
    
    lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
  }
  
  // Throttle scroll events for better performance
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
});

// Add ripple animation
const style = document.createElement("style");
style.textContent = `
  @keyframes ripple {
    to {
      transform: scale(2);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);