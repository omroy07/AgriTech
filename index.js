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
  // ============================================
// PROFIT & LOSS ANALYTICS - ADDON SCRIPT
// Add this to your existing main.js file
// ============================================

// P&L Sample Data
const plSampleData = [
  {
    id: 'U003',
    name: 'Green Foods Pvt Ltd',
    type: 'buyer',
    location: 'Delhi',
    weekly: [
      { period: 'Week 1', revenue: 105000, expenses: 82000, profit: 23000, transactions: 38 },
      { period: 'Week 2', revenue: 112000, expenses: 87000, profit: 25000, transactions: 41 },
      { period: 'Week 3', revenue: 118000, expenses: 91000, profit: 27000, transactions: 39 },
      { period: 'Week 4', revenue: 123000, expenses: 90000, profit: 33000, transactions: 38 }
    ],
    monthly: [
      { period: 'Nov 2025', revenue: 398000, expenses: 315000, profit: 83000, transactions: 134 },
      { period: 'Dec 2025', revenue: 420000, expenses: 335000, profit: 85000, transactions: 142 },
      { period: 'Jan 2026', revenue: 458000, expenses: 350000, profit: 108000, transactions: 156 }
    ],
    quarterly: [
      { period: 'Q3 2025', revenue: 1180000, expenses: 945000, profit: 235000, transactions: 398 },
      { period: 'Q4 2025', revenue: 1276000, expenses: 1000000, profit: 276000, transactions: 432 }
    ],
    categories: {
      'Purchase Costs': -350000,
      'Transportation': -25000,
      'Storage': -15000,
      'Sales Revenue': 458000,
      'Processing': -20000,
      'Labor': -18000,
      'Utilities': -12000
    }
  },
  {
    id: 'U004',
    name: 'FreshMart Retail Chain',
    type: 'retailer',
    location: 'Mumbai',
    weekly: [
      { period: 'Week 1', revenue: 85000, expenses: 68000, profit: 17000, transactions: 45 },
      { period: 'Week 2', revenue: 92000, expenses: 72000, profit: 20000, transactions: 48 },
      { period: 'Week 3', revenue: 88000, expenses: 70000, profit: 18000, transactions: 46 },
      { period: 'Week 4', revenue: 95000, expenses: 73000, profit: 22000, transactions: 50 }
    ],
    monthly: [
      { period: 'Nov 2025', revenue: 310000, expenses: 245000, profit: 65000, transactions: 165 },
      { period: 'Dec 2025', revenue: 342000, expenses: 268000, profit: 74000, transactions: 178 },
      { period: 'Jan 2026', revenue: 360000, expenses: 283000, profit: 77000, transactions: 189 }
    ],
    quarterly: [
      { period: 'Q3 2025', revenue: 895000, expenses: 715000, profit: 180000, transactions: 485 },
      { period: 'Q4 2025', revenue: 1012000, expenses: 796000, profit: 216000, transactions: 532 }
    ],
    categories: {
      'Purchase Costs': -283000,
      'Transportation': -18000,
      'Store Operations': -22000,
      'Sales Revenue': 360000,
      'Staff Salaries': -28000,
      'Utilities': -15000,
      'Marketing': -12000
    }
  },
  {
    id: 'U005',
    name: 'Organic Buyers Co',
    type: 'buyer',
    location: 'Bangalore',
    weekly: [
      { period: 'Week 1', revenue: 72000, expenses: 58000, profit: 14000, transactions: 28 },
      { period: 'Week 2', revenue: 78000, expenses: 62000, profit: 16000, transactions: 31 },
      { period: 'Week 3', revenue: 75000, expenses: 60000, profit: 15000, transactions: 29 },
      { period: 'Week 4', revenue: 82000, expenses: 65000, profit: 17000, transactions: 33 }
    ],
    monthly: [
      { period: 'Nov 2025', revenue: 265000, expenses: 212000, profit: 53000, transactions: 102 },
      { period: 'Dec 2025', revenue: 285000, expenses: 225000, profit: 60000, transactions: 115 },
      { period: 'Jan 2026', revenue: 307000, expenses: 245000, profit: 62000, transactions: 121 }
    ],
    quarterly: [
      { period: 'Q3 2025', revenue: 752000, expenses: 602000, profit: 150000, transactions: 298 },
      { period: 'Q4 2025', revenue: 857000, expenses: 682000, profit: 175000, transactions: 338 }
    ],
    categories: {
      'Purchase Costs': -245000,
      'Transportation': -15000,
      'Quality Testing': -8000,
      'Sales Revenue': 307000,
      'Packaging': -10000,
      'Storage': -12000,
      'Admin': -7000
    }
  }
];

// Chart instances
let plTrendChart = null;
let plCategoryChart = null;

// Initialize P&L Trend Chart
function renderPLTrendChart(userData, timeRange) {
  const ctx = document.getElementById('plTrendChart');
  if (!ctx) return;

  const periods = userData[timeRange];
  const labels = periods.map(p => p.period);
  const revenue = periods.map(p => p.revenue);
  const expenses = periods.map(p => p.expenses);
  const profit = periods.map(p => p.profit);

  if (plTrendChart) plTrendChart.destroy();

  plTrendChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Revenue',
          data: revenue,
          backgroundColor: 'rgba(34, 197, 94, 0.7)',
          borderColor: 'rgba(34, 197, 94, 1)',
          borderWidth: 2,
          borderRadius: 4
        },
        {
          label: 'Expenses',
          data: expenses,
          backgroundColor: 'rgba(239, 68, 68, 0.7)',
          borderColor: 'rgba(239, 68, 68, 1)',
          borderWidth: 2,
          borderRadius: 4
        },
        {
          label: 'Profit/Loss',
          data: profit,
          type: 'line',
          borderColor: 'rgba(34, 197, 94, 1)',
          backgroundColor: 'rgba(34, 197, 94, 0.1)',
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: 'rgba(34, 197, 94, 1)',
          pointBorderColor: '#fff',
          pointBorderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
            padding: 15,
            font: {
              size: 12,
              family: 'Open Sans'
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          padding: 12,
          borderColor: 'rgba(34, 197, 94, 0.5)',
          borderWidth: 1,
          callbacks: {
            label: (context) => {
              const label = context.dataset.label || '';
              const value = context.parsed.y;
              return `${label}: ₹${value.toLocaleString('en-IN')}`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
            callback: (value) => '₹' + (value / 1000) + 'K',
            font: {
              size: 11
            }
          },
          grid: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim(),
            drawBorder: false
          }
        },
        x: {
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
            font: {
              size: 11
            }
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// Initialize P&L Category Chart
function renderPLCategoryChart(categories) {
  const ctx = document.getElementById('plCategoryChart');
  if (!ctx) return;

  const labels = Object.keys(categories);
  const data = Object.values(categories);
  const colors = data.map(v => v < 0 ? 'rgba(239, 68, 68, 0.8)' : 'rgba(34, 197, 94, 0.8)');
  const borderColors = data.map(v => v < 0 ? 'rgba(239, 68, 68, 1)' : 'rgba(34, 197, 94, 1)');

  if (plCategoryChart) plCategoryChart.destroy();

  plCategoryChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        borderColor: borderColors,
        borderWidth: 2,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          padding: 12,
          callbacks: {
            label: (context) => {
              const value = context.parsed.x;
              const type = value < 0 ? 'Expense' : 'Revenue';
              return `${type}: ₹${Math.abs(value).toLocaleString('en-IN')}`;
            }
          }
        }
      },
      scales: {
        x: {
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
            callback: (value) => {
              const absValue = Math.abs(value);
              return (value < 0 ? '-' : '+') + '₹' + (absValue / 1000) + 'K';
            },
            font: {
              size: 10
            }
          },
          grid: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim(),
            drawBorder: false
          }
        },
        y: {
          ticks: {
            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
            font: {
              size: 10
            }
          },
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// Update P&L Summary Cards
function updatePLSummary(userData, timeRange) {
  const periods = userData[timeRange];
  const latest = periods[periods.length - 1];

  document.getElementById('plRevenue').textContent = '₹' + latest.revenue.toLocaleString('en-IN');
  document.getElementById('plExpenses').textContent = '₹' + latest.expenses.toLocaleString('en-IN');
  document.getElementById('plProfit').textContent = '₹' + latest.profit.toLocaleString('en-IN');
  document.getElementById('plTransactions').textContent = latest.transactions;

  const profitEl = document.getElementById('plProfit');
  profitEl.className = 'pl-card-value ' + (latest.profit >= 0 ? 'positive' : 'negative');
}

// Generate CSV Export
function generatePLCSV(user, timeRange) {
  const periods = user[timeRange];
  let csv = 'Period,Revenue,Expenses,Profit,Transactions\n';
  periods.forEach(p => {
    csv += `${p.period},${p.revenue},${p.expenses},${p.profit},${p.transactions}\n`;
  });
  return csv;
}

// Initialize P&L Section
document.addEventListener('DOMContentLoaded', () => {
  const plSelector = document.getElementById('plUserSelector');
  if (!plSelector) return;

  // Populate dropdown with buyers and retailers only
  plSampleData.forEach(u => {
    const opt = document.createElement('option');
    opt.value = u.id;
    opt.textContent = `${u.name} (${u.type})`;
    plSelector.appendChild(opt);
  });

  let currentTimeRange = 'monthly';
  let currentUser = null;

  // Load first user by default
  if (plSampleData.length > 0) {
    currentUser = plSampleData[0];
    plSelector.value = currentUser.id;
    updatePLSummary(currentUser, currentTimeRange);
    renderPLTrendChart(currentUser, currentTimeRange);
    renderPLCategoryChart(currentUser.categories);
  }

  // User selection change handler
  plSelector.addEventListener('change', (e) => {
    const user = plSampleData.find(u => u.id === e.target.value);
    if (user) {
      currentUser = user;
      updatePLSummary(user, currentTimeRange);
      renderPLTrendChart(user, currentTimeRange);
      renderPLCategoryChart(user.categories);
    }
  });

  // Time range toggle handlers
  document.querySelectorAll('.pl-time-toggle .btn').forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state
      document.querySelectorAll('.pl-time-toggle .btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      currentTimeRange = btn.dataset.range;

      if (currentUser) {
        updatePLSummary(currentUser, currentTimeRange);
        renderPLTrendChart(currentUser, currentTimeRange);
      }
    });
  });

  // Export functionality
  const exportBtn = document.getElementById('exportPLBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (!currentUser) {
        alert('Please select a user first');
        return;
      }

      const csv = generatePLCSV(currentUser, currentTimeRange);
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `pl-report-${currentUser.name.replace(/\s+/g, '-')}-${currentTimeRange}-${Date.now()}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    });
  }

  // Update chart colors on theme change
  const observer = new MutationObserver(() => {
    if (currentUser) {
      renderPLTrendChart(currentUser, currentTimeRange);
      renderPLCategoryChart(currentUser.categories);
    }
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['data-theme']
  });
});
});
