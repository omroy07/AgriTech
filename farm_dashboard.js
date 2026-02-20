let selectedFarmId = null;
let allFarms = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchFarms();
});

async function fetchFarms() {
    try {
        const response = await fetch('/api/v1/farms/');
        const data = await response.json();

        if (data.status === 'success') {
            allFarms = data.data;
            if (allFarms.length > 0) {
                switchFarm(allFarms[0].id);
            } else {
                showNoFarmView();
            }
        }
    } catch (error) {
        console.error('Failed to fetch farms:', error);
    }
}

function switchFarm(farmId) {
    selectedFarmId = farmId;
    const farm = allFarms.find(f => f.id === farmId);
    if (!farm) return;

    document.getElementById('current-farm-name').querySelector('span').textContent = farm.name;
    document.getElementById('dashboard-title').textContent = `${farm.name} Overview`;
    document.getElementById('farm-data-view').style.display = 'block';
    document.getElementById('no-farm-message').style.display = 'none';

    fetchFarmAnalytics(farmId);
    fetchFarmAssets(farmId);
    fetchFarmTeam(farmId);
}

async function fetchFarmAnalytics(farmId) {
    try {
        const response = await fetch(`/api/v1/farms/${farmId}/analytics`);
        const data = await response.json();
        if (data.status === 'success') {
            const stats = data.data;
            document.getElementById('stat-asset-value').textContent = `₹${stats.total_asset_value.toLocaleString()}`;
            document.getElementById('stat-production').textContent = `${stats.production_volume} kg`;
        }
    } catch (e) { }
}

async function fetchFarmAssets(farmId) {
    const list = document.getElementById('asset-list');
    list.innerHTML = '<div style="padding: 1rem;">Scanning inventory...</div>';

    // Simulating fetching assets (real endpoint implemented in farms.py)
    // Here we'd fetch from /api/v1/farms/${farmId}/assets
    setTimeout(() => {
        list.innerHTML = `
            <div class="asset-item">
                <div>
                    <strong>Mahindra Tractor</strong><br>
                    <small style="color: #64748b;">Category: Equipment</small>
                </div>
                <div class="condition-badge" style="color: #059669; font-weight: 600;">Good</div>
            </div>
            <div class="asset-item">
                <div>
                    <strong>Pumping Station A</strong><br>
                    <small style="color: #64748b;">Category: Infrastructure</small>
                </div>
                <div class="condition-badge" style="color: #f59e0b; font-weight: 600;">Review</div>
            </div>
        `;
    }, 500);
}

async function fetchFarmTeam(farmId) {
    const list = document.getElementById('team-list');
    list.innerHTML = '';

    try {
        const response = await fetch(`/api/v1/farm_teams/${farmId}/members`);
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('stat-team').textContent = data.data.length;
            data.data.forEach(m => {
                const item = document.createElement('div');
                item.style.cssText = "display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;";
                item.innerHTML = `
                    <div class="member-avatar">${m.user_id}</div>
                    <div>
                        <div style="font-weight: 600;">Member #${m.user_id}</div>
                        <div style="font-size: 0.8rem; color: #64748b; text-transform: uppercase;">${m.role}</div>
                    </div>
                `;
                list.appendChild(item);
            });
        }
    } catch (e) { }
}

function showNoFarmView() {
    document.getElementById('farm-data-view').style.display = 'none';
    document.getElementById('no-farm-message').style.display = 'block';
    document.getElementById('current-farm-name').querySelector('span').textContent = 'No Farms Found';
}

function openNewFarmModal() {
    document.getElementById('new-farm-modal').style.display = 'flex';
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
}

async function createFarm() {
    const name = document.getElementById('farm-name').value;
    const location = document.getElementById('farm-loc').value;

    if (!name || !location) return Swal.fire('Error', 'Name and location are required', 'error');

    try {
        const response = await fetch('/api/v1/farms/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, location })
        });
        const data = await response.json();
        if (data.status === 'success') {
            closeModals();
            Swal.fire('Success', 'Farm registered successfully!', 'success');
            fetchFarms();
        }
    } catch (e) {
        Swal.fire('Error', 'Communication error', 'error');
    }
}
