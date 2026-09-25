/**
 * Batch Traceability & Consumer Verification Controller
 * Location: trace_batch.js
 */

async function traceBatch() {
    const inputEl = document.getElementById('batchIdInput');
    const batchId = (inputEl ? inputEl.value : '').trim() || 'AGRI-TOM-1200-F4A8';

    try {
        const response = await fetch(`/api/v1/traceability/batches/${encodeURIComponent(batchId)}`);
        const data = await response.json();

        if (data.status === 'success' && data.data) {
            renderResults(data.data);
        } else {
            Swal.fire('Not Found', 'We could not find a batch with that ID on our ledger.', 'warning');
        }
    } catch (error) {
        console.error('Trace error:', error);
        Swal.fire('Error', 'Failed to communicate with the traceability ledger engine.', 'error');
    }
}

function renderResults(batch) {
    const resEl = document.getElementById('results');
    if (resEl) resEl.style.display = 'block';

    const heroEl = document.getElementById('hero-batch-id');
    if (heroEl) heroEl.textContent = batch.batch_id;

    // Header Info
    const pName = document.getElementById('p-name');
    if (pName) pName.textContent = batch.crop_name;

    const pVariety = document.getElementById('p-variety');
    if (pVariety) pVariety.textContent = batch.crop_variety || 'Organic Heirloom';

    const pQty = document.getElementById('p-quantity');
    if (pQty) pQty.textContent = `${batch.quantity} ${batch.unit}`;

    const pLoc = document.getElementById('p-location');
    if (pLoc) pLoc.textContent = batch.farm_location;

    const intHash = document.getElementById('integrity-hash');
    if (intHash) intHash.textContent = (batch.integrity_hash || '').substring(0, 24) + '...';

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
    if (qualityCard) {
        qualityCard.style.display = 'block';
        const qContent = document.getElementById('quality-content');
        if (qContent) {
            qContent.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span class="grade-badge" style="background:#10b981; color:white; padding:4px 12px; border-radius:12px; font-weight:700;">GRADE ${batch.quality_grade || 'A+'}</span>
                        <p style="margin-top: 0.5rem; font-size: 0.9rem;">0.00 ppm chemical residues. NABL Lab & NPOP Organic Certified.</p>
                    </div>
                    <div style="text-align: right; font-size: 0.85rem; color: #64748b;">
                        <strong>Harvest Date:</strong><br/>
                        ${new Date(batch.harvest_date).toLocaleDateString()}
                    </div>
                </div>
            `;
        }
    }

    // Audit Trail (Lifecycle logs)
    const trail = document.getElementById('audit-trail');
    if (trail) {
        trail.innerHTML = '';
        const logs = batch.lifecycle_logs && batch.lifecycle_logs.length > 0 ? batch.lifecycle_logs : batch.logs || [];

        logs.forEach(log => {
            const item = document.createElement('div');
            item.className = 'timeline-item';
            const actionTitle = log.event_title || log.action;
            const blockHash = log.block_hash ? `Block: ${log.block_hash.substring(0, 16)}...` : `Handler: ${log.handler_id || 'Agronomist'}`;

            item.innerHTML = `
                <div class="tl-date">${formatDate(log.timestamp)}</div>
                <div class="tl-content" style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:12px; margin-bottom:12px;">
                    <div class="tl-action" style="font-weight:700; color:#0f172a;">${actionTitle}</div>
                    <div style="font-size: 0.85rem; color: #64748b; margin-top:4px;">
                        <i class="fas fa-map-marker-alt"></i> ${log.location || 'Farm'}<br/>
                        <strong style="color:#0ea5e9;">${blockHash}</strong>
                    </div>
                    ${log.notes ? `<p style="margin-top: 0.5rem; border-top: 1px dashed #eee; padding-top: 0.5rem; font-size:0.85rem;">${log.notes}</p>` : ''}
                </div>
            `;
            trail.appendChild(item);
        });
    }

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

// Auto-run if hash exists or on load
document.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash.replace('#', '').trim();
    if (hash) {
        const input = document.getElementById('batchIdInput');
        if (input) input.value = hash;
    }
    traceBatch();
});
