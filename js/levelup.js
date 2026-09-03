/**
 * Level Up - Contributor Growth Hub JS
 * Dynamic statistics, leaderboard tabs, contributor cards, and feature impact tracking.
 */

document.addEventListener("DOMContentLoaded", () => {
  initLevelUpPage();
});

// Fallback Contributor Data
const MOCK_CONTRIBUTORS = [
  {
    username: "omroy07",
    name: "Om Roy",
    avatar: "https://avatars.githubusercontent.com/u/74621533?v=4",
    commits: 142,
    prs: 28,
    issues: 14,
    streak: 21,
    tier: "Elite",
    points: 3450,
    role: "Project Maintainer & Lead Dev",
    heatmap: [3, 2, 3, 1, 3, 2, 3, 3, 1, 2, 3, 2, 3, 3]
  },
  {
    username: "Rushabh-Mahajan",
    name: "Rushabh Mahajan",
    avatar: "https://avatars.githubusercontent.com/u/9919?v=4",
    commits: 96,
    prs: 18,
    issues: 9,
    streak: 14,
    tier: "Master",
    points: 1980,
    role: "Core Platform Engineer",
    heatmap: [2, 3, 1, 2, 3, 2, 2, 3, 1, 0, 2, 3, 2, 2]
  },
  {
    username: "agri-dev-pro",
    name: "Aarav Sharma",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200",
    commits: 54,
    prs: 12,
    issues: 6,
    streak: 9,
    tier: "Pro",
    points: 920,
    role: "UI/UX & Frontend Specialist",
    heatmap: [1, 2, 0, 2, 2, 1, 3, 1, 2, 1, 0, 2, 1, 2]
  },
  {
    username: "green-code-bot",
    name: "Priya Patel",
    avatar: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&q=80&w=200",
    commits: 38,
    prs: 9,
    issues: 4,
    streak: 7,
    tier: "Contributor",
    points: 480,
    role: "AI & Disease Model Contributor",
    heatmap: [0, 1, 2, 1, 0, 2, 1, 2, 1, 1, 2, 0, 1, 1]
  },
  {
    username: "crop-wizard",
    name: "Karan Verma",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&q=80&w=200",
    commits: 22,
    prs: 5,
    issues: 3,
    streak: 4,
    tier: "Beginner",
    points: 210,
    role: "Marketplace & Schemes Docs",
    heatmap: [1, 0, 1, 0, 1, 1, 0, 1, 2, 0, 1, 0, 1, 0]
  }
];

const MOCK_IMPACT_ITEMS = [
  {
    title: "Cart Sidebar Responsive Viewport Fix",
    contributor: "Om Roy",
    handle: "omroy07",
    pr: "#342",
    category: "UI/UX",
    points: 150,
    status: "Merged & Verified",
    date: "2026-09-03"
  },
  {
    title: "Interactive Level Up Contributor Growth Hub",
    contributor: "Rushabh Mahajan",
    handle: "Rushabh-Mahajan",
    pr: "#345",
    category: "Core Platform",
    points: 250,
    status: "Merged & Verified",
    date: "2026-09-03"
  },
  {
    title: "AI Disease Prediction Model Precision Enhancement",
    contributor: "Priya Patel",
    handle: "green-code-bot",
    pr: "#328",
    category: "AI/ML",
    points: 200,
    status: "Merged & Verified",
    date: "2026-08-28"
  },
  {
    title: "Dark/Light Theme Contrast Accessibility Overhaul",
    contributor: "Aarav Sharma",
    handle: "agri-dev-pro",
    pr: "#315",
    category: "UI/UX",
    points: 120,
    status: "Merged & Verified",
    date: "2026-08-20"
  },
  {
    title: "Government Schemes Localization & i18n Translation",
    contributor: "Karan Verma",
    handle: "crop-wizard",
    pr: "#299",
    category: "Documentation",
    points: 80,
    status: "Merged & Verified",
    date: "2026-08-14"
  }
];

let currentTab = "month";
let allContributors = [...MOCK_CONTRIBUTORS];

async function initLevelUpPage() {
  await fetchGitHubContributors();
  renderHeroStats();
  renderPodium();
  renderLeaderboardTable();
  renderContributorCards();
  renderImpactTable();
  setupEventListeners();
}

async function fetchGitHubContributors() {
  try {
    const res = await fetch("https://api.github.com/repos/omroy07/AgriTech/contributors?per_page=10");
    if (!res.ok) throw new Error("GitHub API rate limit or error");
    const data = await res.json();
    
    if (Array.isArray(data) && data.length > 0) {
      allContributors = data.map((item, idx) => {
        const commits = item.contributions || 10;
        const prs = Math.floor(commits / 3) || 2;
        const pts = commits * 15 + prs * 50;
        let tier = "Beginner";
        if (pts >= 2000) tier = "Elite";
        else if (pts >= 1000) tier = "Master";
        else if (pts >= 500) tier = "Pro";
        else if (pts >= 250) tier = "Contributor";

        return {
          username: item.login,
          name: item.login,
          avatar: item.avatar_url,
          commits: commits,
          prs: prs,
          issues: Math.floor(prs / 2),
          streak: 15 - idx,
          tier: tier,
          points: pts,
          role: "GitHub Open Source Contributor",
          heatmap: [2, 3, 1, 2, 3, 2, 3, 1, 2, 3, 2, 1, 3, 2]
        };
      });
    }
  } catch (err) {
    console.warn("Using fallback local contributor data for Level Up page:", err);
  }
}

function renderHeroStats() {
  const totalContribs = allContributors.length;
  const totalPRs = allContributors.reduce((acc, curr) => acc + curr.prs, 0);
  const totalPts = allContributors.reduce((acc, curr) => acc + curr.points, 0);
  const maxStreak = Math.max(...allContributors.map(c => c.streak));

  const totalContribsEl = document.getElementById("statTotalContributors");
  const totalPRsEl = document.getElementById("statTotalPRs");
  const totalPtsEl = document.getElementById("statTotalPoints");
  const maxStreakEl = document.getElementById("statActiveStreak");

  if (totalContribsEl) totalContribsEl.textContent = totalContribs;
  if (totalPRsEl) totalPRsEl.textContent = totalPRs;
  if (totalPtsEl) totalPtsEl.textContent = totalPts.toLocaleString();
  if (maxStreakEl) maxStreakEl.textContent = `${maxStreak} Days 🔥`;
}

function renderPodium() {
  const sorted = [...allContributors].sort((a, b) => b.points - a.points);
  const top1 = sorted[0];
  const top2 = sorted[1];
  const top3 = sorted[2];

  const podiumEl = document.getElementById("podiumContainer");
  if (!podiumEl) return;

  podiumEl.innerHTML = `
    <!-- Rank 2: Silver -->
    ${top2 ? `
    <div class="lu-podium-card lu-podium-2">
      <div class="lu-podium-rank">2</div>
      <img class="lu-podium-avatar" src="${top2.avatar}" alt="${top2.name}" />
      <h3 class="lu-podium-name">${top2.name}</h3>
      <div class="lu-podium-handle">@${top2.username}</div>
      <div class="lu-podium-score">${top2.points} pts</div>
    </div>` : ""}

    <!-- Rank 1: Gold -->
    ${top1 ? `
    <div class="lu-podium-card lu-podium-1">
      <div class="lu-podium-rank">👑 1</div>
      <img class="lu-podium-avatar" src="${top1.avatar}" alt="${top1.name}" />
      <h3 class="lu-podium-name">${top1.name}</h3>
      <div class="lu-podium-handle">@${top1.username}</div>
      <div class="lu-podium-score">${top1.points} pts</div>
    </div>` : ""}

    <!-- Rank 3: Bronze -->
    ${top3 ? `
    <div class="lu-podium-card lu-podium-3">
      <div class="lu-podium-rank">3</div>
      <img class="lu-podium-avatar" src="${top3.avatar}" alt="${top3.name}" />
      <h3 class="lu-podium-name">${top3.name}</h3>
      <div class="lu-podium-handle">@${top3.username}</div>
      <div class="lu-podium-score">${top3.points} pts</div>
    </div>` : ""}
  `;
}

function renderLeaderboardTable(filterText = "") {
  const tbody = document.getElementById("leaderboardTableBody");
  if (!tbody) return;

  let sorted = [...allContributors].sort((a, b) => b.points - a.points);
  
  if (filterText) {
    const q = filterText.toLowerCase();
    sorted = sorted.filter(c => c.name.toLowerCase().includes(q) || c.username.toLowerCase().includes(q) || c.tier.toLowerCase().includes(q));
  }

  tbody.innerHTML = sorted.map((c, idx) => `
    <tr>
      <td>
        <span class="lu-rank-badge" style="background:${idx === 0 ? '#f59e0b' : idx === 1 ? '#94a3b8' : idx === 2 ? '#d97706' : 'rgba(148,163,184,0.2)'}; color:${idx < 3 ? '#fff' : 'var(--lu-text)'}">
          ${idx + 1}
        </span>
      </td>
      <td>
        <div class="lu-user-cell">
          <img class="lu-user-avatar" src="${c.avatar}" alt="${c.name}" />
          <div>
            <span class="lu-user-name">${c.name}</span>
            <span class="lu-user-handle">@${c.username}</span>
          </div>
        </div>
      </td>
      <td>
        <span class="lu-tier-badge ${c.tier === 'Elite' ? 'tier-elite' : ''}">
          <i class="fas ${c.tier === 'Elite' ? 'fa-crown' : 'fa-award'}"></i> ${c.tier}
        </span>
      </td>
      <td><strong>${c.points} pts</strong></td>
      <td>${c.prs} PRs</td>
      <td><span class="lu-streak-pill">🔥 ${c.streak} days</span></td>
    </tr>
  `).join("");
}

function renderContributorCards() {
  const grid = document.getElementById("contributorCardsGrid");
  if (!grid) return;

  grid.innerHTML = allContributors.map(c => `
    <div class="lu-contrib-card">
      <div class="lu-card-header">
        <img class="lu-card-avatar" src="${c.avatar}" alt="${c.name}" />
        <div class="lu-card-userinfo">
          <h3>${c.name}</h3>
          <p>@${c.username} • ${c.role}</p>
        </div>
      </div>

      <div class="lu-card-stats">
        <div>
          <div class="lu-cstat-num">${c.commits}</div>
          <div class="lu-cstat-lbl">Commits</div>
        </div>
        <div>
          <div class="lu-cstat-num">${c.prs}</div>
          <div class="lu-cstat-lbl">PRs</div>
        </div>
        <div>
          <div class="lu-cstat-num">🔥 ${c.streak}</div>
          <div class="lu-cstat-lbl">Streak</div>
        </div>
      </div>

      <div class="lu-activity-graph">
        <div class="lu-activity-title">
          <span>Recent Activity</span>
          <span style="color:var(--lu-accent);">${c.points} pts</span>
        </div>
        <div class="lu-heatmap-grid">
          ${c.heatmap.map(lvl => `<div class="lu-heatmap-cell lvl-${lvl}"></div>`).join("")}
        </div>
      </div>

      <a href="https://github.com/${c.username}" target="_blank" rel="noopener noreferrer" class="lu-btn lu-btn-secondary" style="width:100%; justify-content:center; box-sizing:border-box; margin-top:auto;">
        <i class="fab fa-github"></i> GitHub Profile
      </a>
    </div>
  `).join("");
}

function renderImpactTable(filterText = "", category = "all") {
  const tbody = document.getElementById("impactTableBody");
  if (!tbody) return;

  let items = [...MOCK_IMPACT_ITEMS];

  if (category !== "all") {
    items = items.filter(item => item.category.toLowerCase() === category.toLowerCase());
  }

  if (filterText) {
    const q = filterText.toLowerCase();
    items = items.filter(item => item.title.toLowerCase().includes(q) || item.contributor.toLowerCase().includes(q) || item.pr.toLowerCase().includes(q));
  }

  tbody.innerHTML = items.map(item => `
    <tr>
      <td><strong>${item.title}</strong></td>
      <td>
        <span class="lu-user-name">${item.contributor}</span>
        <span class="lu-user-handle">@${item.handle}</span>
      </td>
      <td><a href="https://github.com/omroy07/AgriTech" target="_blank" style="color:var(--lu-accent-secondary); text-decoration:none; font-weight:600;">${item.pr}</a></td>
      <td><span class="lu-tier-badge">${item.category}</span></td>
      <td><span class="lu-pts-badge">+${item.points} pts</span></td>
      <td><span class="lu-status-tag"><i class="fas fa-check-circle"></i> ${item.status}</span></td>
    </tr>
  `).join("");
}

function setupEventListeners() {
  const searchInput = document.getElementById("leaderboardSearch");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      renderLeaderboardTable(e.target.value);
    });
  }

  const impactSearch = document.getElementById("impactSearch");
  const impactCategory = document.getElementById("impactCategory");

  if (impactSearch) {
    impactSearch.addEventListener("input", () => {
      renderImpactTable(impactSearch.value, impactCategory ? impactCategory.value : "all");
    });
  }

  if (impactCategory) {
    impactCategory.addEventListener("change", () => {
      renderImpactTable(impactSearch ? impactSearch.value : "", impactCategory.value);
    });
  }

  const tabBtns = document.querySelectorAll(".lu-tab");
  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentTab = btn.dataset.tab;
      renderLeaderboardTable(searchInput ? searchInput.value : "");
    });
  });
}
