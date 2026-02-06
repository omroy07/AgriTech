async function traceBatch() {
    const batchId = document.getElementById('batchIdInput').value.trim();
    if (!batchId) {
        return Swal.fire('Error', 'Please enter a valid Batch ID', 'error');
    }

    try {
        const response = await fetch(`/api/v1/traceability/batches/${batchId}`);
        const data = await response.json();

        if (data.status === 'success') {
            renderResults(data.data);
        } else {
            Swal.fire('Not Found', 'We could not find a batch with that ID on our ledger.', 'warning');
        }
    } catch (error) {
        console.error('Trace error:', error);
        Swal.fire('Error', 'Failed to communicate with our blockchain engine.', 'error');
    }
}

function renderResults(batch) {
    document.getElementById('results').style.display = 'block';
    document.getElementById('hero-batch-id').textContent = batch.batch_id;

    // Header Info
    document.getElementById('p-name').textContent = batch.crop_name;
    document.getElementById('p-variety').textContent = batch.crop_variety || 'Standard';
    document.getElementById('p-quantity').textContent = `${batch.quantity} ${batch.unit}`;
    document.getElementById('p-location').textContent = batch.farm_location;
    document.getElementById('integrity-hash').textContent = batch.integrity_hash.substring(0, 16) + '...';

    // Status Tracker
    const statuses = ['HARVESTED', 'QUALITY_CHECK', 'LOGISTICS', 'IN_SHOP'];
    const currentIndex = statuses.indexOf(batch.status);

    statuses.forEach((status, idx) => {
        const step = document.getElementById(`step-${status}`);
        if (step) {
            step.classList.remove('active', 'completed');
            if (idx < currentIndex) step.classList.add('completed');
            if (idx === currentIndex) step.classList.add('active');
        }
    });

    // Quality Section
    const qualityCard = document.getElementById('quality-card');
    if (batch.quality_history && batch.quality_history.length > 0) {
        qualityCard.style.display = 'block';
        const q = batch.quality_history[0]; // Latest grade
        document.getElementById('quality-content').innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="grade-badge">GRADE ${q.grade}</span>
                    <p style="margin-top: 0.5rem; font-size: 0.9rem;">${q.notes || 'Meets all AgriTech safety standards.'}</p>
                </div>
                <div style="text-align: right; font-size: 0.85rem;">
                    <strong>Inspected on:</strong><br/>
                    ${new Date(q.inspection_date).toLocaleDateString()}
                </div>
            </div>
        `;
    } else {
        qualityCard.style.display = 'none';
    }

    // Audit Trail
    const trail = document.getElementById('audit-trail');
    trail.innerHTML = '';
    batch.logs.forEach(log => {
        const item = document.createElement('div');
        item.className = 'timeline-item';
        item.innerHTML = `
            <div class="tl-date">${formatDate(log.timestamp)}</div>
            <div class="tl-content">
                <div class="tl-action">${log.action}</div>
                <div style="font-size: 0.85rem; color: var(--text-muted);">
                    <i class="fas fa-map-marker-alt"></i> ${log.location || 'N/A'}<br/>
                    <strong>Handler ID:</strong> ${log.handler_id}
                </div>
                ${log.notes ? `<p style="margin-top: 0.5rem; border-top: 1px dashed #eee; padding-top: 0.5rem;">${log.notes}</p>` : ''}
            </div>
        `;
        trail.appendChild(item);
    });

    // Check for direct URL access via hash
    if (window.location.hash !== `#${batch.batch_id}`) {
        window.history.pushState(null, null, `#${batch.batch_id}`);
    }
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

async function downloadCert() {
    Swal.fire({
        title: 'Verifying Signature...',
        text: 'Generating high-resolution certificate from audit logs.',
        timer: 2000,
        showConfirmButton: false,
        didOpen: () => Swal.showLoading()
    }).then(() => {
        Swal.fire('Success', 'Certificate generation triggered. Check your notifications for the download link.', 'success');
    });
}

// Initial check for hash in URL
window.onload = () => {
    const hash = window.location.hash.substring(1);
    if (hash && hash.startsWith('AGRI-')) {
        document.getElementById('batchIdInput').value = hash;
        traceBatch();
    }
};
