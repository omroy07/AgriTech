let lastScrollTop = 0;
const wrapper = document.querySelector(".header-nav-wrapper");

window.addEventListener("scroll", () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

  if (scrollTop > lastScrollTop && scrollTop > 100) {
    wrapper.style.transform = "translateY(-100%)";
  } else {
    wrapper.style.transform = "translateY(0)";
  }

  lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});

// DOM Content Loaded
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

  const buttons = document.querySelectorAll('.calendar-button, .feedback-button, .logout-button');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px) scale(1.05)';
    });
    
    button.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
    });
  });

  const gridItems = document.querySelectorAll('.grid-item');
  const gridObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }, index * 100);
        gridObserver.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  });

  gridItems.forEach(item => {
    item.style.opacity = '0';
    item.style.transform = 'translateY(20px)';
    item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    gridObserver.observe(item);
  });

  // Header button click effects
  const headerButtons = document.querySelectorAll('.header-buttons a');
  headerButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      this.style.transform = 'scale(0.95)';
      setTimeout(() => {
        this.style.transform = 'scale(1)';
      }, 150);
    });
  });

  // Add loading states for navigation
  const navLinks = document.querySelectorAll('nav a');
  navLinks.forEach(link => {
    link.addEventListener('click', function() {
      if (!this.href.includes('#')) {
        const loadingText = this.innerHTML;
        this.innerHTML = '<span style="opacity: 0.7;">Loading...</span>';
        
        setTimeout(() => {
          this.innerHTML = loadingText;
        }, 3000);
      }
    });
  });

  window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const header = document.querySelector('header');
    if (header) {
      header.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
  });

  const header = document.querySelector('header h1');
  const currentHour = new Date().getHours();
  let greeting = 'Welcome to AgriTech';
  
  if (currentHour >= 5 && currentHour < 12) {
    greeting = 'Good Morning, AgriTech Farmers';
  } else if (currentHour >= 12 && currentHour < 17) {
    greeting = 'Good Afternoon, AgriTech Community';
  } else if (currentHour >= 17 && currentHour < 21) {
    greeting = 'Good Evening, Agricultural Innovators';
  } else {
    greeting = 'Welcome to AgriTech';
  }
  
  if (header) {
    header.textContent = greeting;
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-navigation');
    }
  });

  document.addEventListener('mousedown', function() {
    document.body.classList.remove('keyboard-navigation');
  });

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  const debouncedScroll = debounce(() => {
    console.log('Scroll event optimized');
  }, 10);

  window.addEventListener('scroll', debouncedScroll);
});

document.addEventListener('error', function(e) {
  if (e.target.tagName === 'IMG') {
    e.target.style.background = 'linear-gradient(135deg, #f0f9f0, #e8f5e8)';
    e.target.style.display = 'flex';
    e.target.style.alignItems = 'center';
    e.target.style.justifyContent = 'center';
    e.target.innerHTML = '<span style="color: #666; font-size: 0.9rem;">🌱 Image Loading...</span>';
  }
}, true);

document.addEventListener('mouseover', function(e) {
  if (e.target.closest('.grid-item') || e.target.closest('nav a') || e.target.closest('.header-buttons a')) {
    document.body.style.cursor = 'pointer';
  }
});

document.addEventListener('mouseout', function(e) {
  if (!e.relatedTarget || (!e.relatedTarget.closest('.grid-item') && !e.relatedTarget.closest('nav a') && !e.relatedTarget.closest('.header-buttons a'))) {
    document.body.style.cursor = 'default';
  }
});