

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
});
