// Particle System - Enhanced from global.js
const PARTICLE_CONFIG = {
  count: 80,
  size: { min: 1, max: 3 },
  speed: { min: 0.05, max: 0.4 },
  colors: [
    "rgba(42, 122, 42, 0.4)",
    "rgba(76, 175, 80, 0.3)",
    "rgba(107, 191, 89, 0.2)",
  ],
  connections: {
    distance: 120,
    lineWidth: 0.6,
    opacity: 0.1,
  },
  mouseInteraction: {
    distance: 180,
    force: 0.3,
  },
};

class Particle {
  constructor(canvas) {
    this.canvas = canvas;
    this.reset();
    this.opacity = Math.random() * 0.5 + 0.3;
    this.fadeDirection = Math.random() > 0.5 ? 1 : -1;
    this.pulseSpeed = 0.01 + Math.random() * 0.015;
  }

  reset() {
    this.x = Math.random() * this.canvas.width;
    this.y = Math.random() * this.canvas.height;
    this.vx =
      (Math.random() - 0.5) *
        (PARTICLE_CONFIG.speed.max - PARTICLE_CONFIG.speed.min) +
      PARTICLE_CONFIG.speed.min;
    this.vy =
      (Math.random() - 0.5) *
        (PARTICLE_CONFIG.speed.max - PARTICLE_CONFIG.speed.min) +
      PARTICLE_CONFIG.speed.min;
    this.size =
      Math.random() * (PARTICLE_CONFIG.size.max - PARTICLE_CONFIG.size.min) +
      PARTICLE_CONFIG.size.min;
    this.color =
      PARTICLE_CONFIG.colors[
        Math.floor(Math.random() * PARTICLE_CONFIG.colors.length)
      ];
    this.originalVx = this.vx;
    this.originalVy = this.vy;
  }

  update(mouse) {
    if (mouse.x !== null && mouse.y !== null) {
      const dx = mouse.x - this.x;
      const dy = mouse.y - this.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < PARTICLE_CONFIG.mouseInteraction.distance) {
        const force =
          (1 - distance / PARTICLE_CONFIG.mouseInteraction.distance) *
          PARTICLE_CONFIG.mouseInteraction.force;
        this.vx -= (dx / distance) * force;
        this.vy -= (dy / distance) * force;
      } else {
        this.vx += (this.originalVx - this.vx) * 0.03;
        this.vy += (this.originalVy - this.vy) * 0.03;
      }
    }

    this.x += this.vx;
    this.y += this.vy;

    if (this.x < 0 || this.x > this.canvas.width) {
      this.vx = -this.vx;
      this.originalVx = -this.originalVx;
    }
    if (this.y < 0 || this.y > this.canvas.height) {
      this.vy = -this.vy;
      this.originalVy = -this.originalVy;
    }

    this.x = Math.max(0, Math.min(this.canvas.width, this.x));
    this.y = Math.max(0, Math.min(this.canvas.height, this.y));

    this.opacity += this.fadeDirection * this.pulseSpeed;
    if (this.opacity <= 0.2 || this.opacity >= 0.6) {
      this.fadeDirection *= -1;
    }
  }

  draw(ctx) {
    ctx.save();
    ctx.globalAlpha = this.opacity;
    ctx.fillStyle = this.color;
    ctx.shadowBlur = 8;
    ctx.shadowColor = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
}

class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.particles = [];
    this.animationId = null;
    this.mouse = { x: null, y: null };

    this.setupCanvas();
    this.createParticles();
    this.setupEventListeners();
    this.animate();
  }

  setupCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.canvas.style.position = "fixed";
    this.canvas.style.top = "0";
    this.canvas.style.left = "0";
    this.canvas.style.zIndex = "-1";
    this.canvas.style.pointerEvents = "none";
  }

  createParticles() {
    this.particles = [];
    for (let i = 0; i < PARTICLE_CONFIG.count; i++) {
      this.particles.push(new Particle(this.canvas));
    }
  }

  setupEventListeners() {
    window.addEventListener("mousemove", (e) => {
      this.mouse.x = e.clientX;
      this.mouse.y = e.clientY;
    });

    window.addEventListener("mouseleave", () => {
      this.mouse.x = null;
      this.mouse.y = null;
    });

    window.addEventListener("resize", () => this.handleResize());
  }

  handleResize() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
    this.createParticles();
  }

  drawConnections() {
    const particles = this.particles;

    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < PARTICLE_CONFIG.connections.distance) {
          const opacity =
            (1 - distance / PARTICLE_CONFIG.connections.distance) *
            PARTICLE_CONFIG.connections.opacity;

          this.ctx.save();
          this.ctx.globalAlpha = opacity;
          this.ctx.strokeStyle = "rgba(76, 175, 80, 0.3)";
          this.ctx.lineWidth = PARTICLE_CONFIG.connections.lineWidth;
          this.ctx.beginPath();
          this.ctx.moveTo(particles[i].x, particles[i].y);
          this.ctx.lineTo(particles[j].x, particles[j].y);
          this.ctx.stroke();
          this.ctx.restore();
        }
      }
    }
  }

  animate() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach((particle) => {
      particle.update(this.mouse);
      particle.draw(this.ctx);
    });

    this.drawConnections();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  destroy() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
  }
}

// Search functionality
function initializeSearch() {
  const searchInput = document.getElementById("searchInput");
  const dealerCards = document.querySelectorAll(".dealer-card");

  searchInput.addEventListener("input", (e) => {
    const searchTerm = e.target.value.toLowerCase();

    dealerCards.forEach((card) => {
      const text = card.textContent.toLowerCase();
      const section = card.closest(".section");

      if (text.includes(searchTerm)) {
        card.style.display = "block";
        card.style.animation = "fadeInUp 0.3s ease-out";
      } else {
        card.style.display = "none";
      }
    });

    // Hide/show sections based on visible cards
    document.querySelectorAll(".section").forEach((section) => {
      const visibleCards = section.querySelectorAll(
        '.dealer-card[style*="block"]'
      );
      section.style.display = visibleCards.length > 0 ? "block" : "none";
    });
  });
}

// Initialize everything when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Initialize particle system
  const canvas = document.getElementById("particles-js");
  if (canvas) {
    new ParticleSystem(canvas);
  }

  // Initialize search
  initializeSearch();

  // Add intersection observer for scroll animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe all sections
  document.querySelectorAll(".section").forEach((section) => {
    section.style.opacity = "0";
    section.style.transform = "translateY(30px)";
    section.style.transition = "all 0.6s cubic-bezier(0.4, 0, 0.2, 1)";
    observer.observe(section);
  });

  // Add hover effects to dealer cards
  document.querySelectorAll(".dealer-card").forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.style.transform = "translateY(-12px) scale(1.02)";
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "translateY(0) scale(1)";
    });
  });

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

  // Add loading animation completion
  setTimeout(() => {
    document.body.style.opacity = "1";
  }, 100);
});

// Performance optimization: Reduce particles on mobile
if (window.innerWidth < 768) {
  PARTICLE_CONFIG.count = 40;
  PARTICLE_CONFIG.connections.distance = 80;
}

// Add touch support for mobile hover effects
document.addEventListener("touchstart", function () {}, {
  passive: true,
});
