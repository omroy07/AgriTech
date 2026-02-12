// DOM Elements
const hamburgerBtn = document.getElementById('hamburgerBtn');
const mobileMenu = document.querySelector('.mobile-menu');
const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
const mobileThemeToggle = document.getElementById('mobileThemeToggle');
const mobileServicesToggle = document.getElementById('mobileServicesToggle');
const mobileServicesList = document.getElementById('mobileServicesList');
const themeToggle = document.querySelector('.theme-toggle');
const themeText = document.querySelector('.theme-text');
const sunIcon = document.querySelector('.sun-icon');
const moonIcon = document.querySelector('.moon-icon');
const scrollBtn = document.getElementById('scrollBtn');
const scrollIcon = document.getElementById('scrollIcon');

// Theme Management
const applyTheme = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    if (theme === 'dark') {
        if (themeText) themeText.textContent = 'Light';
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'inline-block';
    } else {
        if (themeText) themeText.textContent = 'Dark';
        if (moonIcon) moonIcon.style.display = 'inline-block';
        if (sunIcon) sunIcon.style.display = 'none';
    }
};

const savedTheme = localStorage.getItem('theme') || 'dark';
applyTheme(savedTheme);

// Desktop Theme Toggle
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
    });
}

// Mobile Theme Toggle
if (mobileThemeToggle) {
    mobileThemeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'light' ? 'dark' : 'light';
        applyTheme(next);
    });
}

// Mobile Menu Functions
function openMobileMenu() {
    if (hamburgerBtn) hamburgerBtn.classList.add('active');
    if (mobileMenu) mobileMenu.classList.add('active');
    if (mobileMenuOverlay) mobileMenuOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeMobileMenu() {
    if (hamburgerBtn) hamburgerBtn.classList.remove('active');
    if (mobileMenu) mobileMenu.classList.remove('active');
    if (mobileMenuOverlay) mobileMenuOverlay.classList.remove('active');
    document.body.style.overflow = '';
    
    // Close services dropdown if open
    if (mobileServicesList && mobileServicesList.classList.contains('active')) {
        mobileServicesList.classList.remove('active');
        const mobileServicesArrow = document.querySelector('.mobile-services-toggle .services-arrow');
        if (mobileServicesArrow) {
            mobileServicesArrow.classList.remove('rotated');
        }
    }
}

// Hamburger Menu Toggle
if (hamburgerBtn) {
    hamburgerBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (hamburgerBtn.classList.contains('active')) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });
}

// Close menu when clicking overlay
if (mobileMenuOverlay) {
    mobileMenuOverlay.addEventListener('click', closeMobileMenu);
}

// Close menu when clicking links
const mobileLinks = document.querySelectorAll('.mobile-menu a:not(.mobile-services-toggle)');
mobileLinks.forEach(link => {
    link.addEventListener('click', closeMobileMenu);
});

// Mobile Services Toggle
if (mobileServicesToggle && mobileServicesList) {
    mobileServicesToggle.addEventListener('click', (e) => {
        e.preventDefault();
        mobileServicesList.classList.toggle('active');
        const arrow = mobileServicesToggle.querySelector('.services-arrow');
        if (arrow) {
            arrow.classList.toggle('rotated');
        }
    });
}

// Desktop Services Toggle
const servicesToggle = document.querySelector('.services-toggle');
const servicesDropdown = document.querySelector('.services-dropdown');
const servicesArrow = document.querySelector('.services-arrow');

if (servicesToggle && servicesDropdown && servicesArrow) {
    servicesToggle.addEventListener('click', (event) => {
        event.stopPropagation();
        servicesDropdown.classList.toggle('active');
        servicesArrow.classList.toggle('rotated');
        servicesDropdown.style.left = 'auto';
        servicesDropdown.style.right = '0';
    });

    document.addEventListener('click', (e) => {
        const container = document.querySelector('.services-toggle-container');
        if (container && !container.contains(e.target) && servicesDropdown.classList.contains('active')) {
            servicesDropdown.classList.remove('active');
            servicesArrow.classList.remove('rotated');
        }
    });
}

// Scroll Button
if (scrollBtn && scrollIcon) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 300) {
            scrollBtn.classList.add('visible');
            scrollIcon.classList.remove("fa-arrow-down");
            scrollIcon.classList.add("fa-arrow-up");
        } else {
            scrollBtn.classList.remove('visible');
            scrollIcon.classList.remove("fa-arrow-up");
            scrollIcon.classList.add("fa-arrow-down");
        }
    });

    scrollBtn.addEventListener("click", () => {
        if (scrollIcon.classList.contains("fa-arrow-up")) {
            window.scrollTo({top: 0, behavior: "smooth"});
        } else {
            window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"});
        }
    });
}

// Mobile Search
const mobileSearchInput = document.querySelector('.mobile-search-input');
if (mobileSearchInput) {
    mobileSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            alert('Searching for: ' + mobileSearchInput.value);
            closeMobileMenu();
        }
    });
}

// Close menu on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
        closeMobileMenu();
    }
});

// Close menu on window resize (if resized to desktop size)
window.addEventListener('resize', () => {
    if (window.innerWidth > 1024 && mobileMenu && mobileMenu.classList.contains('active')) {
        closeMobileMenu();
    }
});

// Initialize Three.js animation
function initThreeJS() {
    // Your Three.js code here
}

// ================================
// 🌱 Farming Roadmap Feature (FINAL)
// ================================

import cropRoadmaps from "./roadmap.js";

// --------------------
// 1️⃣ Today calculation
// --------------------
function getTodayDay() {
  const start = localStorage.getItem("roadmapStartDate");

  if (!start) {
    localStorage.setItem("roadmapStartDate", new Date().toISOString());
    return 1;
  }

  const diff =
    new Date() - new Date(start);

  return Math.floor(diff / (1000 * 60 * 60 * 24)) + 1;
}

// --------------------
// 2️⃣ Task generation
// --------------------
function generateDailyTasks(roadmap) {
  let day = 1;
  const tasks = [];

  Object.values(roadmap).forEach(month => {
    Object.values(month.weeks).forEach(week => {
      week.forEach(task => {
        tasks.push({
          task,
          baseDay: day,
          day: day,
          completed: false
        });
        day++;
      });
    });
  });

  return tasks;
}

// --------------------
// 3️⃣ ✅ REAL rescheduling
// --------------------
function rescheduleTasks(tasks) {
  const today = getTodayDay();

  // ❗ MISSED = unchecked + scheduled before today
  const missedCount = tasks.filter(
    t => !t.completed && t.day < today
  ).length;
   
  return tasks.map(t => ({
    ...t,
    day: t.baseDay + missedCount
  }));
}

// --------------------
// 4️⃣ Render UI
// --------------------
function renderRoadmap(tasks) {
  const container = document.getElementById("roadmap");
  if (!container) return;

  container.innerHTML = "";

  tasks
    .sort((a, b) => a.day - b.day)
    .forEach(task => {
      const row = document.createElement("div");
      row.style.display = "flex";
      row.style.gap = "10px";
      row.style.marginBottom = "10px";

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.checked = task.completed;

      checkbox.onchange = () => {
        task.completed = checkbox.checked;

        // 🔁 Recalculate immediately
        const updatedTasks = rescheduleTasks(tasks);
        localStorage.setItem(
          "roadmapProgress",
          JSON.stringify(updatedTasks)
        );
        renderRoadmap(updatedTasks);
      };

      const overdue =
        !task.completed && task.day < getTodayDay()
          ? " 🔴 Overdue"
          : "";

      const label = document.createElement("span");
      label.innerHTML = `
        <strong>Day ${task.baseDay}</strong>
        (Scheduled: Day ${task.day})
        ${overdue}
        : ${task.task}
      `;

      row.appendChild(checkbox);
      row.appendChild(label);
      container.appendChild(row);
    });
}

// --------------------
// 🚀 Init (ONCE)
// --------------------
const selectedCrop = "tomato";

let tasks =
  JSON.parse(localStorage.getItem("roadmapProgress")) ||
  generateDailyTasks(
    cropRoadmaps[selectedCrop].roadmap
  );

tasks = rescheduleTasks(tasks);
localStorage.setItem(
  "roadmapProgress",
  JSON.stringify(tasks)
);

renderRoadmap(tasks);
// ===== Farmer Visual Dashboard =====

// Yield Prediction Graph
const yieldCanvas = document.getElementById("yieldChart");

if (yieldCanvas) {
  new Chart(yieldCanvas, {
    type: "line",
    data: {
      labels: ["Week 1", "Week 2", "Week 3", "Week 4"],
      datasets: [{
        label: "Expected Yield",
        data: [1.8, 2.4, 3.0, 3.6],
        borderColor: "green",
        borderWidth: 2,
        fill: false
      }]
    },
    options: {
      responsive: true
    }
  });
}

// Crop Health Status
const healthDiv = document.getElementById("healthStatus");
const healthStatus = "good"; // good | warning | bad

if (healthDiv) {
  healthDiv.className = `health ${healthStatus}`;

  if (healthStatus === "good") {
    healthDiv.innerText = "Crop Health: Good";
  } else if (healthStatus === "warning") {
    healthDiv.innerText = "Crop Health: Attention Needed";
  } else {
    healthDiv.innerText = "Crop Health: Disease Risk";
  }
}
