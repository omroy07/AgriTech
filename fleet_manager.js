let fleet = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchFleet();
});

async function fetchFleet() {
    try {
        const response = await fetch('/api/v1/machinery/fleet');
        const data = await response.json();

        if (data.status === 'success') {
            fleet = data.data;
            renderFleet();
            populateSelect();
        }
    } catch (e) {
        console.error('Fleet sync failed');
    }
}

function renderFleet() {
    const container = document.getElementById('fleet-container');
    container.innerHTML = fleet.map(item => `
        <div class="asset-card">
            <div class="health-indicator">
                <div class="status-dot" style="background: ${item.maintenance_needed ? 'var(--danger)' : 'var(--success)'}"></div>
                <span>${item.maintenance_needed ? 'Service Required' : 'Healthy'}</span>
            </div>
            <h2 style="margin:0;">${item.name}</h2>
            <div class="meter-dial">
                <span class="hours-val">${item.total_hours.toFixed(1)}</span>
                <span class="hours-label">Total Engine Hours</span>
            </div>
            <div class="maintenance-list" id="m-list-${item.id}">
                ${renderMaintenance(item.id)}
            </div>
            <button class="btn" style="width:100%; margin-top:2rem; background: rgba(255,255,255,0.05); color: white;" onclick="viewHealth(${item.id})">Lifecycle Detailed Analysis</button>
        </div>
    `).join('');
}

async function renderMaintenance(id) {
    try {
        const response = await fetch(`/api/v1/machinery/health/${id}`);
        const data = await response.json();
        if (data.status === 'success') {
            const list = document.getElementById(`m-list-${id}`);
            list.innerHTML = data.data.maintenance.map(m => `
                <div class="m-item">
                    <span>${m.type}</span>
                    <span class="${m.is_overdue ? 'warning-text' : ''}">${m.is_overdue ? 'OVERDUE' : m.remaining_hours + 'h left'}</span>
                </div>
            `).join('');
        }
    } catch (e) { }
}

function openLogModal() {
    document.getElementById('log-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('log-modal').style.display = 'none';
}

function populateSelect() {
    const select = document.getElementById('swal-eq');
    select.innerHTML = fleet.map(f => `<option value="${f.id}">${f.name}</option>`).join('');
}

async function submitHours() {
    const eq = document.getElementById('swal-eq').value;
    const start = document.getElementById('swal-start').value;
    const end = document.getElementById('swal-end').value;

    if (!start || !end) return;

    try {
        const response = await fetch('/api/v1/machinery/hours', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ equipment_id: eq, start, end })
        });

        if (response.ok) {
            Swal.fire('Meter Synced', 'Machinery health status recalculated.', 'success');
            closeModal();
            fetchFleet();
        }
    } catch (e) { }
}

async function viewHealth(id) {
    Swal.fire({
        title: 'Depreciation & Health Report',
        text: 'Fetching usage analytics and residual value estimation...',
        icon: 'info',
        timer: 2000
    });
}
