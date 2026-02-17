let activeBatchId = null;
let batches = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchBatches();
});

async function fetchBatches() {
    try {
        const response = await fetch('/api/v1/processing/batches');
        const data = await response.json();
        if (data.status === 'success') {
            batches = data.data;
            renderBatchList();
        }
    } catch (e) {
        console.error('Failed to sync with processing server');
    }
}

function renderBatchList() {
    const list = document.getElementById('batch-list');
    list.innerHTML = batches.map(b => `
        <div class="batch-card ${activeBatchId === b.id ? 'active' : ''}" onclick="selectBatch(${b.id})">
            <div style="font-weight: 700;">${b.batch_number}</div>
            <div style="font-size: 0.8rem; opacity: 0.7;">${b.product_type} | ${b.current_stage.toUpperCase()}</div>
        </div>
    `).join('');
}

async function selectBatch(id) {
    activeBatchId = id;
    const batch = batches.find(b => b.id === id);
    if (!batch) return;

    document.getElementById('active-batch-num').textContent = `Batch ${batch.batch_number}`;
    document.getElementById('active-batch-prod').textContent = `Product: ${batch.product_type} | Starting Weight: ${batch.total_weight} kg`;

    renderBatchList(); // Update highlight
    updateVisualization(batch.current_stage);
    fetchGenealogy(id);
}

function updateVisualization(currentStage) {
    const order = ['collection', 'cleaning', 'processing', 'grading', 'packaging', 'completed'];
    const currentIdx = order.indexOf(currentStage);

    document.querySelectorAll('.stage-node').forEach((node, idx) => {
        const nodeStage = node.dataset.stage;
        const nodeIdx = order.indexOf(nodeStage);

        node.classList.remove('active', 'completed');
        if (nodeIdx < currentIdx) {
            node.classList.add('completed');
        } else if (nodeIdx === currentIdx) {
            node.classList.add('active');
        }
    });

    // Check if we can enable advance btn
    // (Logic: only enable if last audit for current stage was PASS)
}

async function fetchGenealogy(id) {
    try {
        const response = await fetch(`/api/v1/processing/batches/${id}/genealogy`);
        const data = await response.json();
        if (data.status === 'success') {
            const audits = data.data.audits;
            const logPanel = document.getElementById('audit-log');

            if (audits.length === 0) {
                logPanel.innerHTML = '<p style="text-align:center;">No audits performed.</p>';
            } else {
                logPanel.innerHTML = audits.map(a => `
                    <div class="audit-item">
                        <div>
                            <strong>${a.stage_name.toUpperCase()}</strong><br>
                            <small>${new Date(a.timestamp).toLocaleTimeString()}</small>
                        </div>
                        <div class="${a.is_passed ? 'pass-badge' : 'fail-badge'}">
                            ${a.is_passed ? 'PASSED' : 'FAILED'}
                        </div>
                    </div>
                `).join('');
            }

            // Enable advance button if latest audit for current stage passed
            const batch = data.data.batch;
            const latestForStage = audits.filter(a => a.stage_name === batch.current_stage).pop();
            document.getElementById('advance-btn').disabled = !latestForStage || !latestForStage.is_passed;
        }
    } catch (e) { }
}

async function submitAudit() {
    if (!activeBatchId) return;

    const moisture = document.getElementById('qa-moisture').value;
    const purity = document.getElementById('qa-purity').value;
    const weight = document.getElementById('qa-weight').value;

    if (!moisture || !purity || !weight) return Swal.fire('Error', 'Full quality telemetry required', 'error');

    try {
        const response = await fetch(`/api/v1/processing/batches/${activeBatchId}/audit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ moisture, purity, weight })
        });
        const data = await response.json();
        if (data.status === 'success') {
            Swal.fire('Audit Complete', data.data.is_passed ? 'Batch is ready for next stage.' : 'Quality threshold not met.', 'success');
            fetchGenealogy(activeBatchId);
        }
    } catch (e) { }
}

async function advanceStage() {
    if (!activeBatchId) return;
    const batch = batches.find(b => b.id === activeBatchId);

    const order = ['collection', 'cleaning', 'processing', 'grading', 'packaging', 'completed'];
    const nextStage = order[order.indexOf(batch.current_stage) + 1];

    try {
        const response = await fetch(`/api/v1/processing/batches/${activeBatchId}/advance`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ next_stage: nextStage })
        });
        const data = await response.json();
        if (data.status === 'success') {
            Swal.fire('Advanced!', `Batch moved to ${nextStage} stage.`, 'success');
            await fetchBatches();
            selectBatch(activeBatchId);
        }
    } catch (e) { }
}

async function createNewBatch() {
    const { value: formValues } = await Swal.fire({
        title: 'Initialize Manufacturing Batch',
        html:
            '<input id="swal-prod" class="swal2-input" placeholder="Crop Type (e.g. Wheat)">' +
            '<input id="swal-weight" type="number" class="swal2-input" placeholder="Weight (kg)">',
        focusConfirm: false,
        preConfirm: () => {
            return [
                document.getElementById('swal-prod').value,
                document.getElementById('swal-weight').value
            ]
        }
    });

    if (formValues) {
        const [product, weight] = formValues;
        try {
            const response = await fetch('/api/v1/processing/batches', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_type: product, weight: parseFloat(weight) })
            });
            if (response.ok) {
                fetchBatches();
            }
        } catch (e) { }
    }
}
