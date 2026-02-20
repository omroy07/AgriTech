let activeZoneId = null;
let telemetryChart = null;
let syncInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchZones();
});

async function fetchZones() {
    // Demo Farm ID 1
    const farmId = 1;
    try {
        const response = await fetch(`/api/v1/climate/zones/${farmId}`);
        const data = await response.json();

        if (data.status === 'success') {
            const list = document.getElementById('zone-list');
            list.innerHTML = data.data.map(z => `
                <div class="zone-pill" id="zone-pill-${z.id}" onclick="selectZone(${z.id}, '${z.name}')">
                    <div style="font-weight: 700;">${z.name}</div>
                    <div style="font-size: 0.75rem; opacity: 0.5;">ID: ${z.id} | Nodes: ${z.node_count || 1}</div>
                </div>
            `).join('');

            if (data.data.length > 0) {
                selectZone(data.data[0].id, data.data[0].name);
            }
        }
    } catch (e) { console.error("API sync failed"); }
}

async function selectZone(id, name) {
    activeZoneId = id;
    document.querySelectorAll('.zone-pill').forEach(p => p.classList.remove('active'));
    document.getElementById(`zone-pill-${id}`).classList.add('active');
    document.getElementById('active-zone-title').textContent = name;

    // Start real-time sync
    if (syncInterval) clearInterval(syncInterval);
    fetchAnalytics();
    syncInterval = setInterval(fetchAnalytics, 10000); // 10s polling
}

async function fetchAnalytics() {
    if (!activeZoneId) return;

    try {
        const response = await fetch(`/api/v1/climate/analytics/${activeZoneId}`);
        const data = await response.json();

        if (data.status === 'success') {
            const analytical = data.data;
            updateGauges(analytical);
            updateChart(analytical.history);
            updateScientificBlock(analytical);
        }
    } catch (e) { }
}

function updateGauges(data) {
    const latest = data.latest;
    document.getElementById('stat-temp').textContent = latest.temp.toFixed(1);
    document.getElementById('stat-hum').textContent = latest.humidity.toFixed(1);
    document.getElementById('stat-co2').textContent = latest.co2.toFixed(0);
    document.getElementById('stat-vpd').textContent = data.vpd.toFixed(2);
}

function updateScientificBlock(data) {
    const tag = document.getElementById('vpd-tag');
    const desc = document.getElementById('vpd-desc');

    tag.textContent = data.vpd_status.replace('_', ' ');
    tag.className = 'status-chip ' + (data.vpd < 0.8 ? 'status-propagation' : data.vpd < 1.6 ? 'status-vegetative' : 'status-stress');

    const descriptions = {
        'PROPAGATION': 'Optimal moisture for seedlings. High humidity, low stress.',
        'VEGETATIVE': 'Balanced growth phase. Ideal transpiration for leaf density.',
        'FLOWERING': 'High transpiration phase. Peak nutrient uptake efficiency.',
        'HIGH_STRESS': 'Critical stress detected. Plants may be closing stomata.'
    };
    desc.textContent = descriptions[data.vpd_status] || 'Monitoring environmental equilibrium.';
}

function updateChart(history) {
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    const reversed = [...history].reverse();

    const labels = reversed.map(l => new Date(l.timestamp).toLocaleTimeString([], { hour: '2d', minute: '2d' }));
    const temps = reversed.map(l => l.temp);
    const hums = reversed.map(l => l.humidity);

    if (telemetryChart) telemetryChart.destroy();

    telemetryChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                { label: 'Temp (°C)', data: temps, borderColor: '#0ea5e9', tension: 0.4, yAxisID: 'y' },
                { label: 'Hum (%)', data: hums, borderColor: '#10b981', tension: 0.4, yAxisID: 'y1' }
            ]
        },
        options: {
            scales: {
                y: { type: 'linear', position: 'left' },
                y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false } }
            }
        }
    });
}

function addNode() {
    Swal.fire({
        title: 'Provision IoT Node',
        html: `
            <input id="node-uid" class="swal2-input" placeholder="Device UID (e.g., ESP32-F4)">
            <select id="node-type" class="swal2-input">
                <option value="CLIMATE">Climate (T/H/CO2)</option>
                <option value="SOIL">Soil Telemetry</option>
            </select>
        `,
        confirmButtonText: 'Initialize Node',
        preConfirm: () => {
            return {
                uid: document.getElementById('node-uid').value,
                type: document.getElementById('node-type').value,
                zone_id: activeZoneId
            }
        }
    }).then((result) => {
        if (result.isConfirmed) {
            fetch('/api/v1/climate/nodes/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(result.value)
            }).then(() => Swal.fire('Provisioned', 'Node is now listening for telemetry bursts.', 'success'));
        }
    });
}
