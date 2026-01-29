// DOM Elements
const hamburgerBtn = document.getElementById('hamburgerBtn');
const mobileMenu = document.querySelector('.mobile-menu');
const mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
const mobileThemeToggle = document.getElementById('mobileThemeToggle');
const mobileServicesToggle = document.getElementById('mobileServicesToggle');
const mobileServicesList = document.getElementById('mobileServicesList');
const themeText = document.getElementById('themeText');
const moonIcon = document.getElementById('moonIcon');
const sunIcon = document.getElementById('sunIcon');

const scrollBtn = document.getElementById('scrollBtn');
const scrollIcon = document.getElementById('scrollIcon');





function showCachedNotice() {
  const notice = document.getElementById('cached-notice');
  notice.classList.remove('hidden');

  // Automatically hide after a while if you want:
  setTimeout(() => {
    notice.classList.add('hidden');
  }, 5000); // hides after 5 seconds (optional)
}


// Theme Management
// Theme Management
const applyTheme = (theme) => {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);

  const themeText = document.getElementById('themeText');
  const moonIcon = document.getElementById('moonIcon');
  const sunIcon = document.getElementById('sunIcon');

  if (theme === 'dark') {
    if (themeText) themeText.textContent = 'Light';

    if (moonIcon) {
      moonIcon.style.display = 'none';
    }

    if (sunIcon) {
      sunIcon.style.display = 'inline-block';
    }
  } else {
    if (themeText) themeText.textContent = 'Dark';

    if (moonIcon) {
      moonIcon.style.display = 'inline-block';
    }

    if (sunIcon) {
      sunIcon.style.display = 'none';
    }
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


document.addEventListener('DOMContentLoaded', () => {
  const statusDiv = document.getElementById('network-status');
  const cachedDiv = document.getElementById('cached-notice');

  function updateNetworkStatus() {
    if (!navigator.onLine) {
      statusDiv.textContent = '⚠️ Offline or poor connection';
      statusDiv.classList.remove('hidden');
    } else {
      // Check if slow/limited connection
      if (navigator.connection && (navigator.connection.effectiveType === '2g' || navigator.connection.effectiveType === '3g')) {
        statusDiv.textContent = '📶 Poor/slow connection';
        statusDiv.classList.remove('hidden');
      } else {
        statusDiv.classList.add('hidden');
        cachedDiv.classList.add('hidden'); // clear cached notice too
      }
    }
  }

  window.addEventListener('online', updateNetworkStatus);
  window.addEventListener('offline', updateNetworkStatus);

  updateNetworkStatus();

  function showCachedNotice() {
    cachedDiv.classList.remove('hidden');
  }

  window.addEventListener('online', () => {
    cachedDiv.classList.add('hidden');
  });

  // Example fetch wrapper
  fetch('/some-api')
    .then(resp => resp.json())
    .then(data => {
      // render data
    })
    .catch(err => {
      showCachedNotice();
    });
});

// --------------------
// My Activity: Single User Profile with Service Usage Chart
// --------------------
const USER_DATA_KEY = 'agritech_user_data';

const sampleUsers = [
  {
    id: 'U001',
    name: 'Rajesh Kumar',
    type: 'farmer',
    location: 'Punjab',
    sold: 45,
    purchased: 12,
    revenue: 125000,
    transactions: [
      { date: '2026-01-23', type: 'sold', item: 'Wheat (500kg)', amount: 15000 },
      { date: '2026-01-22', type: 'purchased', item: 'Fertilizer Bag', amount: -2000 },
      { date: '2026-01-20', type: 'sold', item: 'Rice (300kg)', amount: 12000 },
      { date: '2026-01-18', type: 'purchased', item: 'Tractor Rental', amount: -5000 },
      { date: '2026-01-15', type: 'sold', item: 'Corn (400kg)', amount: 8000 }
    ],
    serviceUsage: {
      'Buyers & Retailers': 35,
      'Equipment Supply': 20,
      'Finance & Insurance': 15,
      'Agronomist & Advisor': 18,
      'Grocery Sellers': 12
    }
  },
  {
    id: 'U002',
    name: 'Sita Devi',
    type: 'farmer',
    location: 'Uttar Pradesh',
    sold: 28,
    purchased: 18,
    revenue: 85000,
    transactions: [
      { date: '2026-01-24', type: 'purchased', item: 'Pest Control', amount: -1500 },
      { date: '2026-01-21', type: 'sold', item: 'Vegetables (200kg)', amount: 6000 },
      { date: '2026-01-19', type: 'purchased', item: 'Seeds Pack', amount: -800 }
    ],
    serviceUsage: {
      'Buyers & Retailers': 28,
      'Equipment Supply': 15,
      'Finance & Insurance': 20,
      'Agronomist & Advisor': 25,
      'Grocery Sellers': 12
    }
  },
  {
    id: 'U003',
    name: 'Green Foods Pvt Ltd',
    type: 'buyer',
    location: 'Delhi',
    sold: 5,
    purchased: 156,
    revenue: -350000,
    transactions: [
      { date: '2026-01-24', type: 'purchased', item: 'Wheat (1000kg)', amount: -50000 },
      { date: '2026-01-22', type: 'sold', item: 'Processed Grains', amount: 8000 },
      { date: '2026-01-20', type: 'purchased', item: 'Rice (800kg)', amount: -40000 }
    ],
    serviceUsage: {
      'Buyers & Retailers': 40,
      'Equipment Supply': 8,
      'Finance & Insurance': 25,
      'Agronomist & Advisor': 10,
      'Grocery Sellers': 17
    }
  }
];

function getUserData() {
  try {
    const saved = JSON.parse(localStorage.getItem(USER_DATA_KEY));
    return saved || sampleUsers;
  } catch (e) {
    return sampleUsers;
  }
}

function saveUserData(data) {
  localStorage.setItem(USER_DATA_KEY, JSON.stringify(data));
}

let currentChart = null;

function renderServiceChart(user) {
  const ctx = document.getElementById('serviceChart');
  if (!ctx) return;

  const labels = Object.keys(user.serviceUsage);
  const data = Object.values(user.serviceUsage);

  if (currentChart) currentChart.destroy();

  currentChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(249, 115, 22, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(236, 72, 153, 0.8)'
        ],
        borderColor: [
          'rgba(34, 197, 94, 1)',
          'rgba(59, 130, 246, 1)',
          'rgba(249, 115, 22, 1)',
          'rgba(168, 85, 247, 1)',
          'rgba(236, 72, 153, 1)'
        ],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: 'var(--text-color)',
            font: { size: 12 }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => `${context.label}: ${context.parsed}%`
          }
        }
      }
    }
  });
}

function renderUserProfile(user) {
  document.getElementById('profileSection').style.display = 'block';
  document.getElementById('profileName').textContent = user.name;
  document.getElementById('profileSold').textContent = user.sold;
  document.getElementById('profilePurchased').textContent = user.purchased;
  document.getElementById('profileRevenue').textContent = '₹' + user.revenue.toLocaleString();

  // Render transactions
  const list = document.getElementById('transactionList');
  list.innerHTML = '';
  user.transactions.forEach(tx => {
    const li = document.createElement('li');
    li.style.padding = '0.5rem';
    li.style.borderBottom = '1px solid var(--border-color)';
    const sign = tx.type === 'sold' ? '+' : '';
    const color = tx.type === 'sold' ? 'var(--accent-color)' : 'var(--text-muted)';
    li.innerHTML = `<div style="font-size:0.85rem;color:var(--text-muted)">${tx.date}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.25rem;">
                      <span style="color:var(--text-color);font-size:0.95rem">${tx.item}</span>
                      <span style="color:${color};font-weight:600;">${sign}₹${Math.abs(tx.amount).toLocaleString()}</span>
                    </div>`;
    list.appendChild(li);
  });

  renderServiceChart(user);
}

document.addEventListener('DOMContentLoaded', () => {
  const selector = document.getElementById('userSelector');
  const users = getUserData();

  // Populate dropdown
  users.forEach(u => {
    const opt = document.createElement('option');
    opt.value = u.id;
    opt.textContent = `${u.name} (${u.type})`;
    selector.appendChild(opt);
  });

  // Load first user by default
  if (users.length > 0) {
    selector.value = users[0].id;
    renderUserProfile(users[0]);
  }

  selector.addEventListener('change', (e) => {
    const uid = e.target.value;
    if (!uid) {
      document.getElementById('profileSection').style.display = 'none';
      return;
    }
    const user = users.find(u => u.id === uid);
    if (user) renderUserProfile(user);
  });

  const clearBtn = document.getElementById('clearUserDataBtn');
  const exportBtn = document.getElementById('exportUserDataBtn');

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      localStorage.removeItem(USER_DATA_KEY);
      location.reload();
    });
  }

  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      const uid = selector.value;
      const user = users.find(u => u.id === uid);
      if (!user) return;
      const data = JSON.stringify(user, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `agritech-user-${user.id}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    });
  }
});
 main
