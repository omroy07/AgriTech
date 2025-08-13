document.addEventListener("DOMContentLoaded", function () {
  if (typeof initializeParticles === "function") {
    initializeParticles();
  }

  // Scroll progress indicator
  const scrollProgress = document.getElementById("scrollProgress");
  window.addEventListener("scroll", () => {
    const scrollTop = window.pageYOffset;
    const docHeight = document.body.offsetHeight - window.innerHeight;
    const scrollPercent = (scrollTop / docHeight) * 100;
    scrollProgress.style.width = scrollPercent + "%";
  });

  // Smooth scroll for navigation links
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

  // Enhanced loading animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.animation = "fadeInUp 0.8s ease-out forwards";
      }
    });
  }, observerOptions);

  document.querySelectorAll(".animate-in").forEach((el) => {
    observer.observe(el);
  });

  // Add hover effects for better interactivity
  document.querySelectorAll(".crop-item, section").forEach((item) => {
    item.addEventListener("mouseenter", function () {
      this.style.transform = this.classList.contains("crop-item")
        ? "translateY(-4px)"
        : "translateY(-8px)";
    });

    item.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });
});
