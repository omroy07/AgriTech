let activeFarmId = null;
let nutrientChart = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchFarms();
});

async function fetchFarms() {
    // In real app, fetch from /api/v1/farms
    // For demo, we'll try to find active farms or provide a dummy
    const farmList = document.getElementById('farm-list');
    const dummyFarms = [{ id: 1, name: "Sunset Valley" }, { id: 2, name: "River Oaks" }];

    farmList.innerHTML = dummyFarms.map(f => `
        <div class="farm-card" onclick="selectFarm(${f.id}, '${f.name}')" id="farm-${f.id}">
            <div style="font-weight: 700;">${f.name}</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">Farm ID: #${f.id}</div>
        </div>
    `).join('');
}

async function selectFarm(id, name) {
    activeFarmId = id;
    document.querySelectorAll('.farm-card').forEach(c => c.classList.remove('active'));
    document.getElementById(`farm-${id}`).classList.add('active');
    document.getElementById('active-farm-name').textContent = name;

    await fetchHistory(id);
}

async function fetchHistory(id) {
    try {
        const response = await fetch(`/api/v1/soil/history/${id}`);
        const data = await response.json();
        if (data.status === 'success' && data.data.length > 0) {
            const latest = data.data[0];
            updateStats(latest);
            updateChart(data.data);
            fetchRecommendations(latest.id);
        }
    } catch (e) {
        console.error("Failed to sync soil history");
    }
}

function updateStats(test) {
    document.getElementById('val-ph').textContent = test.ph_level;
    document.getElementById('val-oc').textContent = test.organic_matter || 'N/A';
    document.getElementById('val-ec').textContent = test.ec || 'N/A';

    // Animate bars
    document.getElementById('fill-ph').style.width = `${(test.ph_level / 14) * 100}%`;
    document.getElementById('fill-oc').style.width = `${(test.organic_matter || 0) * 10}%`;
    document.getElementById('fill-ec').style.width = `${(test.ec || 0) * 20}%`;

    document.getElementById('last-test-date').textContent = `Last synchronized: ${test.test_date}`;
}

function updateChart(history) {
    const ctx = document.getElementById('nutrientChart').getContext('2d');
    const reversedHistory = [...history].reverse();

    const labels = reversedHistory.map(h => h.test_date);
    const nitrogen = reversedHistory.map(h => h.nitrogen);
    const phosphorus = reversedHistory.map(h => h.phosphorus);
    const potassium = reversedHistory.map(h => h.potassium);

    if (nutrientChart) nutrientChart.destroy();

    nutrientChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'Nitrogen', data: nitrogen, borderColor: '#10b981', tension: 0.3 },
                { label: 'Phosphorus', data: phosphorus, borderColor: '#f59e0b', tension: 0.3 },
                { label: 'Potassium', data: potassium, borderColor: '#3b82f6', tension: 0.3 }
            ]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
}

async function fetchRecommendations(testId) {
    try {
        const response = await fetch(`/api/v1/soil/recommendations/${testId}`);
        const data = await response.json();
        if (data.status === 'success') {
            const container = document.getElementById('rec-container');
            container.innerHTML = data.data.map(r => `
                <div class="rec-item">
                    <h4>${r.crop_type} Strategy</h4>
                    <p style="font-size: 0.85rem; margin: 0.5rem 0;">Need: N: ${r.nitrogen} | P: ${r.phosphorus} | K: ${r.potassium}</p>
                    <div style="font-size: 0.8rem; opacity: 0.8;">
                        <strong>Suggestions:</strong> ${r.suggestions.map(s => `${s.amount}kg/ha ${s.name}`).join(', ')}
                    </div>
                </div>
            `).join('');
        }
    } catch (e) { }
}

async function openTestModal() {
    if (!activeFarmId) return Swal.fire('Error', 'Please select a farm first', 'error');

    const { value: formValues } = await Swal.fire({
        title: 'New Soil Lab Analysis',
        html:
            '<div style="display:grid; grid-template-columns: 1fr 1fr; gap: 10px;">' +
            '<input id="swal-n" class="swal2-input" placeholder="Nitrogen (ppm)">' +
            '<input id="swal-p" class="swal2-input" placeholder="Phosphorus (ppm)">' +
            '<input id="swal-k" class="swal2-input" placeholder="Potassium (ppm)">' +
            '<input id="swal-ph" class="swal2-input" placeholder="pH Level">' +
            '<input id="swal-oc" class="swal2-input" placeholder="Organic Matter (%)">' +
            '<input id="swal-ec" class="swal2-input" placeholder="EC (dS/m)">' +
            '</div>',
        focusConfirm: false,
        preConfirm: () => {
            return {
                farm_id: activeFarmId,
                nitrogen: parseFloat(document.getElementById('swal-n').value),
                phosphorus: parseFloat(document.getElementById('swal-p').value),
                potassium: parseFloat(document.getElementById('swal-k').value),
                ph_level: parseFloat(document.getElementById('swal-ph').value),
                organic_matter: parseFloat(document.getElementById('swal-oc').value),
                ec: parseFloat(document.getElementById('swal-ec').value)
            }
        }
    });

    if (formValues) {
        try {
            const response = await fetch('/api/v1/soil/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formValues)
            });
            if (response.ok) {
                Swal.fire('Test Logged', 'Scientific recommendations have been generated.', 'success');
                fetchHistory(activeFarmId);
            }
        } catch (e) {
            Swal.fire('Error', 'Failed to communicate with analytical engine', 'error');
        }
    }
}
