let myPolicies = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchPolicies();
});

async function fetchPolicies() {
    try {
        const response = await fetch('/api/v1/insurance-v2/my-policies');
        const data = await response.json();

        if (data.status === 'success') {
            myPolicies = data.data;
            renderPolicies();
            updateStats();
        }
    } catch (e) {
        console.error('Failed to sync with Underwriting server');
    }
}

function renderPolicies() {
    const container = document.getElementById('policy-container');
    const claimSelect = document.getElementById('claim-policy-id');

    if (myPolicies.length === 0) {
        container.innerHTML = '<p style="text-align:center; padding: 2rem; opacity: 0.5;">No active policies found.</p>';
        return;
    }

    container.innerHTML = myPolicies.map(p => `
        <div class="policy-item">
            <span class="status-pill status-${p.status.toLowerCase()}">${p.status}</span>
            <div style="font-weight:700; font-size:1.1rem;">${p.crop_type} Coverage</div>
            <div style="font-size:0.85rem; opacity:0.7; margin: 0.25rem 0;">ID: POL-${p.id.toString().padStart(6, '0')}</div>
            <div style="display:flex; justify-content:space-between; margin-top:1rem;">
                <div>
                    <div style="font-size:0.7rem; text-transform:uppercase; opacity:0.6;">Insured Value</div>
                    <div style="font-weight:700;">₹${p.coverage.toLocaleString()}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem; text-transform:uppercase; opacity:0.6;">Risk Score</div>
                    <div style="font-weight:700; color: ${p.risk_score > 50 ? '#ef4444' : '#10b981'};">${p.risk_score}%</div>
                </div>
            </div>
        </div>
    `).join('');

    claimSelect.innerHTML = myPolicies.map(p => `
        <option value="${p.id}">${p.crop_type} (POL-${p.id})</option>
    `).join('');
}

function updateStats() {
    const total = myPolicies.reduce((sum, p) => sum + p.coverage, 0);
    document.getElementById('total-coverage').textContent = `₹${total.toLocaleString()}`;
}

async function openPolicyModal() {
    const { value: formValues } = await Swal.fire({
        title: 'New Policy Underwriting',
        html:
            '<select id="swal-crop" class="swal2-input">' +
            '<option value="Wheat">Wheat</option><option value="Rice">Rice</option>' +
            '<option value="Coffee">Coffee</option><option value="Corn">Corn</option>' +
            '</select>' +
            '<input id="swal-coverage" type="number" class="swal2-input" placeholder="Coverage Amount (₹)">' +
            '<label style="font-size:0.7rem;">Start Date</label><input id="swal-start" type="date" class="swal2-input">' +
            '<label style="font-size:0.7rem;">End Date</label><input id="swal-end" type="date" class="swal2-input">',
        focusConfirm: false,
        preConfirm: () => {
            return {
                crop_type: document.getElementById('swal-crop').value,
                coverage: document.getElementById('swal-coverage').value,
                start_date: document.getElementById('swal-start').value,
                end_date: document.getElementById('swal-end').value,
                farm_id: 1 // Default for demo
            }
        }
    });

    if (formValues) {
        try {
            const response = await fetch('/api/v1/insurance-v2/policies', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formValues)
            });
            const data = await response.json();
            if (data.status === 'success') {
                Swal.fire('Policy Issued!', `Premium: ₹${data.data.premium}. Policy is now Active.`, 'success');
                fetchPolicies();
            }
        } catch (e) {
            Swal.fire('Error', 'Underwriting engine rejected the application.', 'error');
        }
    }
}

async function submitClaim() {
    const policyId = document.getElementById('claim-policy-id').value;
    const loss = document.getElementById('claim-loss').value;
    const reason = document.getElementById('claim-reason').value;

    if (!loss || !reason) return Swal.fire('Incomplete Data', 'Loss details are mandatory for assessment.', 'warning');

    try {
        const response = await fetch('/api/v1/insurance-v2/claims', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ policy_id: policyId, loss_kg: loss, reason: reason })
        });
        const data = await response.json();
        if (data.status === 'success') {
            Swal.fire('Claim Filed', `Our adjusters will review the loss. Suggested payout: ₹${data.data.suggested_payout}`, 'success');
            document.getElementById('pending-claims').textContent = parseInt(document.getElementById('pending-claims').textContent) + 1;
        }
    } catch (e) { }
}
