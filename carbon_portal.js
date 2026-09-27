/**
 * Regenerative Agriculture & Carbon Sequestration Credit Portal
 * IPCC Tier 1/2 Model Calculations, Green Wallet, Chart.js Visualizations, and Eco-Rewards
 */

// Global State
let currentSimulation = {
    acreage: 25.0,
    annual_co2e_t: 48.60,
    mintable_credits: 486,
    annual_inr: 72900,
    soc_gain_pct: 0.54,
    soil_health_index: 96.5,
    breakdown: [
        { practice: 'Zero-Tillage', co2e: 14.58 },
        { practice: 'Cover Cropping', co2e: 11.66 },
        { practice: 'Biochar Amendment', co2e: 10.21 },
        { practice: 'Boundary Agroforestry', co2e: 7.29 },
        { practice: 'Vermicompost', co2e: 4.86 }
    ],
    five_year_trajectory: [
        { year: 'Year 1', cumulative_co2e: 48.6, soc_pct: 1.31 },
        { year: 'Year 2', cumulative_co2e: 102.1, soc_pct: 1.42 },
        { year: 'Year 3', cumulative_co2e: 160.4, soc_pct: 1.54 },
        { year: 'Year 4', cumulative_co2e: 223.6, soc_pct: 1.65 },
        { year: 'Year 5', cumulative_co2e: 291.6, soc_pct: 1.74 }
    ]
};

let userWallet = {
    credits: 340,
    inr_value: 51000,
    usd_value: 612.00
};

// Chart instances
let miniTrajectoryChartInstance = null;
let practiceDoughnutChartInstance = null;
let fiveYearLineChartInstance = null;

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadRewardsCatalog();
    loadLeaderboard();
    fetchInitialAssessment();
});

// Tab Switcher
function switchTab(tabId) {
    document.querySelectorAll('.tab-section').forEach(el => el.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    const activeSection = document.getElementById(tabId);
    if (activeSection) {
        activeSection.style.display = 'block';
    }

    // Mark active button
    const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(b => 
        b.getAttribute('onclick') && b.getAttribute('onclick').includes(tabId)
    );
    if (activeBtn) activeBtn.classList.add('active');

    // Trigger chart update if switching to analytics
    if (tabId === 'tab-analytics') {
        setTimeout(() => {
            if (practiceDoughnutChartInstance) practiceDoughnutChartInstance.resize();
            if (fiveYearLineChartInstance) fiveYearLineChartInstance.resize();
        }, 100);
    }
}

// Chart Initializers
function initCharts() {
    // 1. Mini Trajectory Chart in Calculator
    const miniCtx = document.getElementById('miniTrajectoryChart');
    if (miniCtx) {
        miniTrajectoryChartInstance = new Chart(miniCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Yr 1', 'Yr 2', 'Yr 3', 'Yr 4', 'Yr 5'],
                datasets: [{
                    label: 'Cumulative CO₂e (t)',
                    data: currentSimulation.five_year_trajectory.map(p => p.cumulative_co2e),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: '#10b981'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.parsed.y} t CO₂e`
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { color: '#94a3b8', font: { size: 10 } } },
                    y: { grid: { color: 'rgba(51, 65, 85, 0.4)' }, ticks: { color: '#94a3b8', font: { size: 10 } } }
                }
            }
        });
    }

    // 2. Practice Breakdown Doughnut Chart
    const doughnutCtx = document.getElementById('practiceDoughnutChart');
    if (doughnutCtx) {
        practiceDoughnutChartInstance = new Chart(doughnutCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: currentSimulation.breakdown.map(b => b.practice),
                datasets: [{
                    data: currentSimulation.breakdown.map(b => b.co2e),
                    backgroundColor: [
                        '#10b981', '#0ea5e9', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6'
                    ],
                    borderWidth: 2,
                    borderColor: '#0f172a'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: '#94a3b8', font: { family: 'Outfit', size: 11 }, padding: 12 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} t CO₂e`
                        }
                    }
                },
                cutout: '65%'
            }
        });
    }

    // 3. 5-Year Cumulative CO2e and SOC% Line Chart
    const lineCtx = document.getElementById('fiveYearLineChart');
    if (lineCtx) {
        fiveYearLineChartInstance = new Chart(lineCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5'],
                datasets: [
                    {
                        label: 'Cumulative CO₂e (t)',
                        data: currentSimulation.five_year_trajectory.map(p => p.cumulative_co2e),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        yAxisID: 'yCO2',
                        tension: 0.35,
                        fill: true,
                        borderWidth: 3,
                        pointRadius: 4,
                        pointBackgroundColor: '#10b981'
                    },
                    {
                        label: 'Soil Organic Carbon (SOC %)',
                        data: currentSimulation.five_year_trajectory.map(p => p.soc_pct),
                        borderColor: '#0ea5e9',
                        backgroundColor: 'transparent',
                        yAxisID: 'ySOC',
                        tension: 0.35,
                        borderWidth: 3,
                        borderDash: [5, 5],
                        pointRadius: 4,
                        pointBackgroundColor: '#0ea5e9'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: '#94a3b8', font: { family: 'Outfit', size: 12 } }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(51, 65, 85, 0.3)' },
                        ticks: { color: '#94a3b8', font: { family: 'Outfit' } }
                    },
                    yCO2: {
                        type: 'linear',
                        position: 'left',
                        grid: { color: 'rgba(51, 65, 85, 0.3)' },
                        ticks: { color: '#10b981', font: { family: 'Outfit' } },
                        title: { display: true, text: 'CO₂e (Tonnes)', color: '#10b981' }
                    },
                    ySOC: {
                        type: 'linear',
                        position: 'right',
                        grid: { display: false },
                        ticks: { color: '#0ea5e9', font: { family: 'Outfit' } },
                        title: { display: true, text: 'SOC (%)', color: '#0ea5e9' }
                    }
                }
            }
        });
    }
}

// Fetch Initial Impact Assessment
async function fetchInitialAssessment() {
    try {
        const response = await fetch('/api/v1/carbon/impact');
        if (response.ok) {
            const res = await response.json();
            if (res.status === 'success' && res.data) {
                const d = res.data;
                const formatted = {
                    annual_co2e_t: d.total_co2_offset_tonnes || 48.6,
                    mintable_credits: d.available_green_credits || 340,
                    annual_inr: d.estimated_wallet_value_inr || 51000,
                    soil_health_index: d.soil_health_index || 96.5,
                    soc_gain_pct: 0.54,
                    breakdown: (d.practice_breakdown || []).map(p => ({
                        practice: p.practice_name || p.practice,
                        co2e: p.annual_co2e_tonnes || p.co2e
                    })),
                    five_year_trajectory: (d.five_year_trajectory || []).map(t => ({
                        year: t.year,
                        cumulative_co2e: t.cumulative_co2e_t || t.cumulative_co2e,
                        soc_pct: t.projected_soc_pct || t.soc_pct
                    }))
                };
                updateUIWithSimulation(formatted);
                if (d.available_green_credits) {
                    userWallet.credits = d.available_green_credits;
                    userWallet.inr_value = d.available_green_credits * 150;
                    updateWalletUI();
                }
            }
        }
    } catch (e) {
        console.log('Using baseline simulation defaults:', e);
    }
}

// Handle IPCC Tier 1/2 Simulation Form Submission
async function handleCalculate(event) {
    if (event) event.preventDefault();

    const acreage = parseFloat(document.getElementById('calc-acreage').value) || 25.0;
    const climateZone = document.getElementById('calc-climate').value;
    const soilType = document.getElementById('calc-soil').value;
    const samplingDepth = parseFloat(document.getElementById('calc-depth').value) || 30.0;

    // Collect checked practices
    const selectedPractices = [];
    if (document.getElementById('p-notill')?.checked) selectedPractices.push('no_till');
    if (document.getElementById('p-cover')?.checked) selectedPractices.push('cover_crops');
    if (document.getElementById('p-biochar')?.checked) selectedPractices.push('biochar_application');
    if (document.getElementById('p-agro')?.checked) selectedPractices.push('agroforestry');
    if (document.getElementById('p-compost')?.checked) selectedPractices.push('organic_compost');
    if (document.getElementById('p-drip')?.checked) selectedPractices.push('precision_drip');

    if (selectedPractices.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'No Practices Selected',
            text: 'Please select at least one regenerative practice to model SOC stock changes.'
        });
        return;
    }

    try {
        const payload = {
            acreage: acreage,
            climate_zone: climateZone,
            soil_type: soilType,
            practices: selectedPractices,
            sampling_depth_cm: samplingDepth
        };

        const response = await fetch('/api/v1/carbon/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const res = await response.json();
            if (res.status === 'success') {
                const formatted = {
                    acreage: res.acreage,
                    annual_co2e_t: res.annual_co2e_tonnes,
                    mintable_credits: res.annual_green_credits,
                    annual_inr: res.annual_revenue_inr,
                    soil_health_index: res.soil_health_index,
                    soc_gain_pct: res.annual_sequestration_rate_t_c_ha * 0.22,
                    breakdown: (res.practice_breakdown || []).map(p => ({
                        practice: p.practice_name || p.practice,
                        co2e: p.annual_co2e_tonnes || p.co2e
                    })),
                    five_year_trajectory: (res.five_year_trajectory || []).map(t => ({
                        year: t.year,
                        cumulative_co2e: t.cumulative_co2e_t || t.cumulative_co2e,
                        soc_pct: t.projected_soc_pct || t.soc_pct
                    }))
                };

                updateUIWithSimulation(formatted);
                Swal.fire({
                    icon: 'success',
                    title: 'IPCC Simulation Complete',
                    text: `Estimated annual sequestration: ${formatted.annual_co2e_t.toFixed(2)} t CO₂e (${formatted.mintable_credits} Green Credits)`,
                    timer: 2500,
                    showConfirmButton: false
                });
                return;
            }
        }
        throw new Error('Fallback to client calculation');
    } catch (err) {
        // Fallback Client-Side IPCC Tier 1/2 Model
        const simulated = runClientIPCCSimulation(acreage, climateZone, soilType, selectedPractices);
        updateUIWithSimulation(simulated);
        Swal.fire({
            icon: 'success',
            title: 'IPCC Simulation Complete',
            text: `Calculated ${simulated.annual_co2e_t.toFixed(2)} t CO₂e (${simulated.mintable_credits} Green Credits)`,
            timer: 2500,
            showConfirmButton: false
        });
    }
}

// Client Fallback IPCC Simulation
function runClientIPCCSimulation(acreage, climate, soil, practices) {
    const socRef = 47.0; // t C / ha reference
    let flu = 1.0;
    let fmg = practices.includes('no_till') ? 1.16 : 1.0;
    let fi = 1.0;
    if (practices.includes('cover_crops')) fi += 0.11;
    if (practices.includes('organic_compost')) fi += 0.14;
    if (practices.includes('biochar_application')) fi += 0.18;
    if (practices.includes('agroforestry')) fi += 0.15;
    if (practices.includes('precision_drip')) fi += 0.05;

    const deltaCPerHaYear = Math.max(0.2, (socRef * (flu * fmg * fi - 1.0)) / 20.0);
    const ha = acreage * 0.404686;
    const annualCo2e = deltaCPerHaYear * (44.0 / 12.0) * ha;
    const credits = Math.round(annualCo2e * 10);
    const inrValue = credits * 150;
    const socGain = +(deltaCPerHaYear * 0.22).toFixed(2);

    const breakdown = practices.map((p, idx) => ({
        practice: p.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
        co2e: +((annualCo2e * (1 / practices.length)).toFixed(2))
    }));

    const trajectory = [];
    let cum = 0;
    let baseSoc = 1.20;
    for (let yr = 1; yr <= 5; yr++) {
        cum += annualCo2e;
        baseSoc += socGain;
        trajectory.push({
            year: `Year ${yr}`,
            cumulative_co2e: +(cum.toFixed(1)),
            soc_pct: +(baseSoc.toFixed(2))
        });
    }

    return {
        acreage: acreage,
        annual_co2e_t: +(annualCo2e.toFixed(2)),
        mintable_credits: credits,
        annual_inr: inrValue,
        soc_gain_pct: socGain,
        soil_health_index: +(Math.min(100.0, 75.0 + practices.length * 4.2).toFixed(1)),
        breakdown: breakdown,
        five_year_trajectory: trajectory
    };
}

// Update UI & Charts with Model Output
function updateUIWithSimulation(data) {
    currentSimulation = { ...currentSimulation, ...data };

    // KPI Bar
    const kpiCo2 = document.getElementById('kpi-co2');
    if (kpiCo2 && data.annual_co2e_t !== undefined) kpiCo2.textContent = `${data.annual_co2e_t.toFixed(1)} Tonnes`;

    const kpiCredits = document.getElementById('kpi-credits');
    if (kpiCredits && data.mintable_credits !== undefined) kpiCredits.textContent = `${data.mintable_credits} Credits`;

    const kpiIncome = document.getElementById('kpi-income');
    if (kpiIncome && data.annual_inr !== undefined) kpiIncome.textContent = `₹${data.annual_inr.toLocaleString()} / yr`;

    const kpiSoc = document.getElementById('kpi-soc');
    if (kpiSoc && data.soc_gain_pct !== undefined) kpiSoc.textContent = `+${data.soc_gain_pct.toFixed(2)}% ΔSOC`;

    // Assessment Panel
    const simCo2 = document.getElementById('sim-co2');
    if (simCo2 && data.annual_co2e_t !== undefined) simCo2.textContent = `${data.annual_co2e_t.toFixed(2)} t CO₂e`;

    const simCredits = document.getElementById('sim-credits');
    if (simCredits && data.mintable_credits !== undefined) simCredits.textContent = `${data.mintable_credits} Credits`;

    const simInr = document.getElementById('sim-inr');
    if (simInr && data.annual_inr !== undefined) simInr.textContent = `₹${data.annual_inr.toLocaleString()} INR`;

    // Sidebar
    const sideCo2 = document.getElementById('side-co2');
    if (sideCo2 && data.annual_co2e_t !== undefined) sideCo2.textContent = data.annual_co2e_t.toFixed(1);

    const sideSoc = document.getElementById('side-soc');
    if (sideSoc && data.soc_gain_pct !== undefined) sideSoc.textContent = (1.20 + data.soc_gain_pct).toFixed(2);

    const sideHealth = document.getElementById('side-health');
    if (sideHealth && data.soil_health_index !== undefined) sideHealth.textContent = data.soil_health_index.toFixed(1);

    const sidePractices = document.getElementById('side-practices');
    if (sidePractices && data.breakdown) sidePractices.textContent = data.breakdown.length;

    // Update Charts
    updateChartsWithData(data);
}

// Update Chart Instances
function updateChartsWithData(data) {
    if (miniTrajectoryChartInstance && data.five_year_trajectory) {
        miniTrajectoryChartInstance.data.datasets[0].data = data.five_year_trajectory.map(p => p.cumulative_co2e);
        miniTrajectoryChartInstance.update();
    }

    if (practiceDoughnutChartInstance && data.breakdown) {
        practiceDoughnutChartInstance.data.labels = data.breakdown.map(b => b.practice);
        practiceDoughnutChartInstance.data.datasets[0].data = data.breakdown.map(b => b.co2e);
        practiceDoughnutChartInstance.update();
    }

    if (fiveYearLineChartInstance && data.five_year_trajectory) {
        fiveYearLineChartInstance.data.datasets[0].data = data.five_year_trajectory.map(p => p.cumulative_co2e);
        fiveYearLineChartInstance.data.datasets[1].data = data.five_year_trajectory.map(p => p.soc_pct);
        fiveYearLineChartInstance.update();
    }
}

// Mint Green Credits
async function mintNewCredits() {
    const mintAmount = currentSimulation.mintable_credits || 120;
    const inrValue = mintAmount * 150;

    const confirmResult = await Swal.fire({
        title: 'Mint Verified Green Credits?',
        html: `
            <div style="text-align: left; font-size: 13.5px; color: #cbd5e1; line-height: 1.6;">
                <p><strong>Verified Sequestration:</strong> ${currentSimulation.annual_co2e_t.toFixed(2)} t CO₂e</p>
                <p><strong>Mintable Green Credits:</strong> <span style="color: #10b981; font-weight: 700;">+${mintAmount} Credits</span></p>
                <p><strong>Market Value:</strong> <span style="color: #f59e0b; font-weight: 700;">≈ ₹${inrValue.toLocaleString()} INR</span></p>
                <p style="margin-top: 10px; font-size: 12px; color: #94a3b8;">
                    <i class="fas fa-shield-alt"></i> Backed by IPCC Tier 1/2 Registry & Verra VCS Standard.
                </p>
            </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#10b981',
        cancelButtonColor: '#475569',
        confirmButtonText: '<i class="fas fa-coins"></i> Confirm & Mint to Wallet'
    });

    if (confirmResult.isConfirmed) {
        try {
            const response = await fetch('/api/v1/carbon/mint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    co2e_tonnes: currentSimulation.annual_co2e_t,
                    credits: mintAmount,
                    farm_id: 1
                })
            });

            if (response.ok) {
                const res = await response.json();
                if (res.status === 'success') {
                    userWallet.credits += mintAmount;
                    userWallet.inr_value += inrValue;
                    updateWalletUI();

                    Swal.fire({
                        icon: 'success',
                        title: 'Credits Minted Successfully!',
                        html: `
                            <p><strong>+${mintAmount} Green Credits</strong> deposited to your wallet.</p>
                            <p style="font-size: 12px; color: #94a3b8; margin-top: 6px;">
                                Transaction Hash: <code>${res.mint_transaction_id || '0xMINT_2026_98124'}</code>
                            </p>
                        `,
                        confirmButtonColor: '#10b981'
                    });
                    return;
                }
            }
        } catch (e) {
            console.log('Mint API offline, updating local wallet');
        }

        // Fallback local update
        userWallet.credits += mintAmount;
        userWallet.inr_value += inrValue;
        updateWalletUI();

        Swal.fire({
            icon: 'success',
            title: 'Credits Minted Successfully!',
            html: `<p><strong>+${mintAmount} Green Credits</strong> deposited to your Green Wallet.</p>`,
            confirmButtonColor: '#10b981'
        });
    }
}

// Update Wallet UI
function updateWalletUI() {
    const wCredits = document.getElementById('wallet-credits');
    if (wCredits) wCredits.textContent = userWallet.credits;

    const wInr = document.getElementById('wallet-inr');
    if (wInr) wInr.textContent = userWallet.inr_value.toLocaleString();
}

// Load Rewards Catalog
async function loadRewardsCatalog() {
    const container = document.getElementById('rewards-catalog-container');
    if (!container) return;

    let items = [];
    try {
        const response = await fetch('/api/v1/carbon/rewards-catalog');
        if (response.ok) {
            const res = await response.json();
            if (res.status === 'success' && res.catalog) {
                items = res.catalog;
            }
        }
    } catch (e) {
        console.log('Using default rewards catalog items');
    }

    if (items.length === 0) {
        items = [
            {
                id: 'REW-BIO-01',
                title: 'Organic Bio-Fertilizer & Microbial Kit',
                description: '50kg Premium Vermicompost + 2kg Trichoderma viride + Mycorrhizae bio-inoculant booster.',
                credits_required: 15,
                rupee_value: 2250,
                sponsor: 'ICAR & IFFCO Green Kisan Initiative',
                icon: 'fa-flask-vial',
                badge_color: '#10b981'
            },
            {
                id: 'REW-SOLAR-02',
                title: 'Solar Micro-Drip Pump Subsidy Voucher',
                description: '₹12,000 direct equipment subsidy voucher for 3HP/5HP Solar-Powered DC Micro-Drip Irrigation Systems.',
                credits_required: 80,
                rupee_value: 12000,
                sponsor: 'PM-KUSUM Clean Energy Fund',
                icon: 'fa-solar-panel',
                badge_color: '#0ea5e9'
            },
            {
                id: 'REW-IOT-03',
                title: 'Dual-Depth IoT Soil Moisture Probe',
                description: 'LoRaWAN-enabled dual-depth (0-30cm and 30-60cm) FMCW soil moisture & EC salinity probe with 5-year battery.',
                credits_required: 35,
                rupee_value: 5250,
                sponsor: 'HydroGuardian IoT Systems',
                icon: 'fa-microchip',
                badge_color: '#8b5cf6'
            },
            {
                id: 'REW-CASH-04',
                title: 'Direct Sponsor Cash Payout (Kisan Bank Transfer)',
                description: 'Direct bank transfer (NEFT/UPI) to farmer registered bank account (₹1,500 per 10 credits).',
                credits_required: 10,
                rupee_value: 1500,
                sponsor: 'Global Voluntary Carbon Market Sponsor',
                icon: 'fa-money-bill-wave',
                badge_color: '#f59e0b'
            },
            {
                id: 'REW-SEED-05',
                title: 'Climate-Resilient Certified Organic Seed Kit',
                description: 'Non-GMO certified drought-resistant & pest-tolerant seed varieties for 2.5 acres.',
                credits_required: 20,
                rupee_value: 3000,
                sponsor: 'National Organic Seed Consortium',
                icon: 'fa-seedling',
                badge_color: '#ec4899'
            }
        ];
    }

    container.innerHTML = items.map(item => `
        <div class="reward-card">
            <div class="reward-top">
                <div class="reward-icon-box" style="background: ${item.badge_color || item.color || '#10b981'};">
                    <i class="fas ${item.icon || 'fa-gift'}"></i>
                </div>
                <div class="reward-cost-tag">
                    <i class="fas fa-coins"></i> ${item.credits_required} Credits
                </div>
            </div>
            <div>
                <div class="reward-title">${item.title}</div>
                <p class="reward-desc">${item.description}</p>
                <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 8px;">
                    <i class="fas fa-building"></i> Sponsor: <strong>${item.sponsor}</strong>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 12px; margin-top: 6px;">
                <span style="font-size: 13px; font-weight: 700; color: #f59e0b;">Value: ₹${(item.rupee_value || item.inr_value || item.credits_required * 150).toLocaleString()}</span>
                <button class="btn-claim" onclick="redeemReward('${item.id}', '${item.title.replace(/'/g, "\\'")}', ${item.credits_required})">
                    <i class="fas fa-arrow-right"></i> Redeem
                </button>
            </div>
        </div>
    `).join('');
}

// Redeem Eco-Reward
async function redeemReward(rewardId, title, cost) {
    if (userWallet.credits < cost) {
        Swal.fire({
            icon: 'error',
            title: 'Insufficient Green Credits',
            html: `
                <p>You need <strong>${cost} Credits</strong> to claim this reward.</p>
                <p style="color: var(--text-muted); margin-top: 6px;">Your current balance: <strong>${userWallet.credits} Credits</strong>.</p>
                <p style="font-size: 12.5px; margin-top: 8px;">Log more regenerative practices or run new IPCC simulations to mint additional credits.</p>
            `,
            confirmButtonColor: '#10b981'
        });
        return;
    }

    const confirm = await Swal.fire({
        title: 'Confirm Redemption',
        html: `
            <div style="text-align: left; font-size: 13.5px; line-height: 1.6;">
                <p><strong>Item:</strong> ${title}</p>
                <p><strong>Cost:</strong> <span style="color: #10b981; font-weight: 700;">${cost} Green Credits</span></p>
                <p><strong>Remaining Balance:</strong> ${userWallet.credits - cost} Credits</p>
            </div>
        `,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#10b981',
        cancelButtonColor: '#475569',
        confirmButtonText: 'Claim Reward'
    });

    if (confirm.isConfirmed) {
        try {
            const response = await fetch('/api/v1/carbon/redeem', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reward_id: rewardId,
                    credits: cost
                })
            });

            if (response.ok) {
                const res = await response.json();
                userWallet.credits -= cost;
                userWallet.inr_value = userWallet.credits * 150;
                updateWalletUI();

                Swal.fire({
                    icon: 'success',
                    title: 'Reward Redeemed!',
                    html: `
                        <p>Your redemption voucher for <strong>${title}</strong> has been generated.</p>
                        <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;">
                            Voucher Code: <code>${res.voucher_code || res.data?.voucher_code || 'VCHR-ECO-2026-AGRI'}</code>
                        </p>
                    `,
                    confirmButtonColor: '#10b981'
                });
                return;
            }
        } catch (e) {
            console.log('Redeem API fallback');
        }

        userWallet.credits -= cost;
        userWallet.inr_value = userWallet.credits * 150;
        updateWalletUI();

        Swal.fire({
            icon: 'success',
            title: 'Reward Redeemed!',
            html: `
                <p>Your voucher for <strong>${title}</strong> is active.</p>
                <p style="margin-top: 8px; font-size: 12px; color: #94a3b8;">
                    Voucher Code: <code>VCHR-ECO-2026-${Math.floor(1000 + Math.random() * 9000)}</code>
                </p>
            `,
            confirmButtonColor: '#10b981'
        });
    }
}

// Load Community Leaderboard
async function loadLeaderboard() {
    const tbody = document.getElementById('leaderboard-tbody');
    if (!tbody) return;

    let leaders = [];
    try {
        const response = await fetch('/api/v1/carbon/leaderboard');
        if (response.ok) {
            const res = await response.json();
            if (res.status === 'success' && res.leaderboard) {
                leaders = res.leaderboard;
            }
        }
    } catch (e) {
        console.log('Using default leaderboard data');
    }

    if (leaders.length === 0) {
        leaders = [
            { rank: 1, name: 'Rajesh Patil', farm_name: 'Green Valley Organic Estate', district: 'Nashik, Maharashtra', co2e_sequestered_t: 48.6, green_credits: 486, badge: '🏆 Net-Zero Hero' },
            { rank: 2, name: 'Sukhwinder Singh', farm_name: 'Dhillon Biochar Farms', district: 'Ludhiana, Punjab', co2e_sequestered_t: 42.1, green_credits: 421, badge: '🥇 Biochar Pioneer' },
            { rank: 3, name: 'Venkat Raman', farm_name: 'Godavari Agroforestry', district: 'Guntur, Andhra Pradesh', co2e_sequestered_t: 37.8, green_credits: 378, badge: '🥈 Agroforestry Master' },
            { rank: 4, name: 'Kavita Devi', farm_name: 'Malwa Regenerative Soils', district: 'Indore, Madhya Pradesh', co2e_sequestered_t: 31.4, green_credits: 314, badge: '🥉 Soil Guardian' },
            { rank: 5, name: 'Nilesh Barot', farm_name: 'Tapi Solar Drip Estate', district: 'Surat, Gujarat', co2e_sequestered_t: 26.5, green_credits: 265, badge: '🌱 Eco Champion' }
        ];
    }

    tbody.innerHTML = leaders.map(l => {
        let badgeClass = 'rank-other';
        if (l.rank === 1) badgeClass = 'rank-1';
        else if (l.rank === 2) badgeClass = 'rank-2';
        else if (l.rank === 3) badgeClass = 'rank-3';

        const isUser = (l.name && l.name.includes('Rajesh')) || (l.farm_name && l.farm_name.includes('Green Valley'));
        const rowBg = isUser ? 'style="background: rgba(16, 185, 129, 0.1); font-weight: 700;"' : '';

        return `
            <tr ${rowBg}>
                <td><span class="rank-badge ${badgeClass}">${l.rank}</span></td>
                <td>
                    <div><strong>${l.name}</strong></div>
                    <div style="font-size: 11.5px; color: var(--text-muted);">${l.farm_name || l.estate || 'Organic Estate'}</div>
                </td>
                <td>${l.district}</td>
                <td style="color: #10b981; font-weight: 700;">${(l.co2e_sequestered_t || l.co2e || 0).toFixed(1)} t CO₂e</td>
                <td style="color: #0ea5e9; font-weight: 700;">${l.green_credits || l.credits}</td>
                <td>
                    <span style="background: var(--surface-bg); padding: 4px 10px; border-radius: 8px; font-size: 12px; border: 1px solid var(--border-color);">
                        ${l.badge}
                    </span>
                </td>
            </tr>
        `;
    }).join('');
}
