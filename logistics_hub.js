let activeRoutes = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchActiveRoutes();
    setInterval(fetchActiveRoutes, 15000); // 15s refresh
});

async function fetchStats() {
    try {
        const response = await fetch('/api/v1/logistics-v2/fleet/stats');
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('fleet-util').textContent = `${data.data.utilization}%`;
            document.getElementById('active-count').textContent = data.data.active;
        }
    } catch (e) { }
}

async function fetchActiveRoutes() {
    try {
        const response = await fetch('/api/v1/logistics-v2/routes/active');
        const data = await response.json();
        if (data.status === 'success') {
            activeRoutes = data.data;
            renderRoutes();
        }
    } catch (e) { }
}

function renderRoutes() {
    const container = document.getElementById('routes-container');
    if (activeRoutes.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 5rem; opacity: 0.3;">All vehicles are back at base.</p>';
        return;
    }

    container.innerHTML = activeRoutes.map(r => `
        <div class="route-card">
            <div class="route-header">
                <div>
                    <div class="route-path">
                        <span>${r.origin}</span>
                        <i class="fas fa-long-arrow-alt-right" style="color: var(--primary);"></i>
                        <span>${r.destination}</span>
                    </div>
                    <div style="font-size: 0.85rem; opacity: 0.5; margin-top: 0.5rem;">
                        Dispatch ID: #00${r.id} | Cargo: ${r.weight}kg
                    </div>
                </div>
                <span class="status-chip ${r.status === 'IN_TRANSIT' ? 'status-transit' : 'status-pending'}">
                    ${r.status.replace('_', ' ')}
                </span>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar" style="width: ${r.status === 'IN_TRANSIT' ? '65%' : '5%'}"></div>
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 0.8rem; opacity: 0.6;">
                    Est. Distance: ${r.distance}km
                </div>
                <div>
                    ${r.status === 'PENDING' ?
            `<button class="btn btn-primary" onclick="startRoute(${r.id})">Start Route</button>` :
            `<button class="btn btn-primary" style="background: var(--success);" onclick="completeRoute(${r.id})">Mark Delivered</button>`
        }
                </div>
            </div>
        </div>
    `).join('');
}

async function startRoute(id) {
    try {
        const res = await fetch(`/api/v1/logistics-v2/route/${id}/start`, { method: 'POST' });
        if (res.ok) {
            Swal.fire('Dispatch Active', 'Driver has initiated the route.', 'success');
            fetchActiveRoutes();
            fetchStats();
        }
    } catch (e) { }
}

async function completeRoute(id) {
    const { value: dist } = await Swal.fire({
        title: 'Confirm Delivery',
        input: 'number',
        inputLabel: 'Total Odometer Reading (km)',
        showCancelButton: true
    });

    if (dist) {
        try {
            const res = await fetch(`/api/v1/logistics-v2/route/${id}/complete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ actual_distance: parseFloat(dist) })
            });
            if (res.ok) {
                Swal.fire('Delivered', 'Route finalized and fleet status updated.', 'success');
                fetchActiveRoutes();
                fetchStats();
            }
        } catch (e) { }
    }
}

async function newDispatch() {
    // Conceptual creation
    Swal.fire({
        title: 'New Dispatch Manifest',
        text: 'This will initiate a vehicle pairing suggestion from the routing engine.',
        icon: 'info'
    });
}
