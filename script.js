document.addEventListener("DOMContentLoaded", function () {
  const elementsToAnimate = document.querySelectorAll(".loading");
  elementsToAnimate.forEach((element, index) => {
    setTimeout(() => {
      element.style.animationDelay = `${index * 0.2}s`;
      element.classList.add("loaded");
    }, index * 100);
  });

  const lazyImages = document.querySelectorAll('img[loading="lazy"]');

  const imageObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const img = entry.target;

          if (img.complete) {
            img.classList.add("loaded");
          } else {
            img.addEventListener("load", () => {
              img.classList.add("loaded");
            });
          }

          observer.unobserve(img);
        }
      });
    },
    {
      rootMargin: "50px",
    }
  );

  lazyImages.forEach((img) => {
    imageObserver.observe(img);
  });

  // Navbar scroll effect
  const navbar = document.querySelector(".navbar");
  let ticking = false;

  function updateNavbar() {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    if (scrollTop > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
    ticking = false;
  }

  function requestTick() {
    if (!ticking) {
      requestAnimationFrame(updateNavbar);
      ticking = true;
    }
  }

  window.addEventListener("scroll", requestTick, { passive: true });
  updateNavbar();

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
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

  // Intersection Observer for feature cards
  const featureCards = document.querySelectorAll(".feature-card");
  const cardObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.animation = "slideInUp 0.6s ease-out forwards";
        }
      });
    },
    {
      threshold: 0.1,
    }
  );

  featureCards.forEach((card) => {
    cardObserver.observe(card);
  });

  // Button hover effects
  const buttons = document.querySelectorAll(".btn, .cta-button");
  buttons.forEach((button) => {
    button.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-2px) scale(1.02)";
    });

    button.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)";
    });
  });

  // Carousel hover effect
  const carousel = document.querySelector(".slide-track");
  carousel.addEventListener("mouseenter", function () {
    this.style.animationPlayState = "paused";
  });

  carousel.addEventListener("mouseleave", function () {
    this.style.animationPlayState = "running";
  });
});

// Debounced resize event listener
let resizeTimeout;
window.addEventListener(
  "resize",
  function () {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(function () {
      console.log("Window resized, recalculating layout...");
    }, 250);
  },
  { passive: true }
);
