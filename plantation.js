window.addEventListener("scroll", () => {
  const scrollIndicator = document.getElementById("scrollIndicator");
  const scrollTop = document.documentElement.scrollTop;
  const scrollHeight =
    document.documentElement.scrollHeight -
    document.documentElement.clientHeight;
  const scrollPercent = (scrollTop / scrollHeight) * 100;
  scrollIndicator.style.width = scrollPercent + "%";
});

document.querySelectorAll("nav ul li a").forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    document.querySelector(this.getAttribute("href")).scrollIntoView({
      behavior: "smooth",
    });
  });
});

// Add active state to nav links
window.addEventListener("scroll", () => {
  const sections = document.querySelectorAll("section");
  const navLinks = document.querySelectorAll("nav ul li a");

  let current = "";
  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (scrollY >= sectionTop - 200) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href").substring(1) === current) {
      link.classList.add("active");
    }
  });
});

// Scroll to Top Button Logic
const scrollTopBtn = document.getElementById('scrollTopBtn');
const scrollThreshold = 250; // px

const toggleScrollTopBtn = () => {
  const scrollY = window.scrollY || document.documentElement.scrollTop;
  if (scrollY > scrollThreshold) {
    scrollTopBtn.classList.add('show');
  } else {
    scrollTopBtn.classList.remove('show');
  }
};

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
  // Optional: move focus to header for accessibility
  const header = document.querySelector('header');
  if (header) header.setAttribute('tabindex', '-1');
  if (header) header.focus();
};

window.addEventListener('scroll', toggleScrollTopBtn, { passive: true });
scrollTopBtn.addEventListener('click', scrollToTop);
