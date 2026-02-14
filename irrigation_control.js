let zones = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchZones();
    // Poll for telemetry every 5 seconds to simulate real-time
    setInterval(fetchZones, 5000);
});

async function fetchZones() {
    try {
        const response = await fetch('/api/v1/irrigation/zones');
        const data = await response.json();

        if (data.status === 'success') {
            zones = data.data;
            renderZones();
        }
    } catch (e) {
        console.error('Failed to sync with IoT gateway');
        // If API fails, we could use mock data but here we assume healthy connection
    }
}

function renderZones() {
    const container = document.getElementById('zones-container');
    const existingIds = Array.from(container.children).map(c => parseInt(c.dataset.id));

    zones.forEach(zone => {
        let card = container.querySelector(`[data-id="${zone.id}"]`);

        if (!card) {
            const template = document.getElementById('zone-template');
            card = template.content.cloneNode(true).querySelector('.zone-card');
            card.dataset.id = zone.id;
            container.appendChild(card);
        }

        // Update Dynamic content
        card.querySelector('.zone-name').textContent = zone.name;
        card.querySelector('.zone-desc').textContent = zone.description;

        const valveIcon = card.querySelector('#valve-status-icon');
        if (zone.status === 'open') {
            valveIcon.classList.add('active');
        } else {
            valveIcon.classList.remove('active');
        }

        // Fetch latest telemetry for this zone
        syncLatestTelemetry(zone.id, card);
    });
}

async function syncLatestTelemetry(zoneId, card) {
    try {
        const response = await fetch(`/api/v1/irrigation/analytics/${zoneId}`);
        const data = await response.json();

        if (data.status === 'success' && data.data.history.length > 0) {
            const latest = data.data.history[0];
            card.querySelector('#val-temp').textContent = `${latest.temperature}°C`;
            card.querySelector('#val-ph').textContent = latest.ph_level;

            const fill = card.querySelector('#moist-bar-fill');
            fill.style.width = `${latest.moisture}%`;
            card.querySelector('#val-moist-text').textContent = `Moisture: ${latest.moisture}%`;

            // Log entry if change detected (simple logic)
            if (latest.moisture < 30) {
                addGlobalLog(`Critical Low Moisture detected in ${card.querySelector('.zone-name').textContent}`);
            }
        }
    } catch (e) { }
}

async function toggleValve(btn, status) {
    const card = btn.closest('.zone-card');
    const zoneId = card.dataset.id;

    try {
        const response = await fetch(`/api/v1/irrigation/control/${zoneId}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: status })
        });

        if (response.ok) {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: `Valve ${status.toUpperCase()}`,
                showConfirmButton: false,
                timer: 1500
            });
            fetchZones();
        }
    } catch (e) {
        Swal.fire('Error', 'Communication with Field Controller failed', 'error');
    }
}

function addGlobalLog(msg) {
    const list = document.getElementById('global-logs');
    const item = document.createElement('div');
    item.className = 'log-item';
    item.innerHTML = `<span>${msg}</span><span>${new Date().toLocaleTimeString()}</span>`;
    list.prepend(item);

    // Keep only last 10
    if (list.children.length > 10) list.lastElementChild.remove();
}
