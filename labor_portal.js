let activeFarmId = 1;
let workerData = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchWorkers();
});

async function fetchWorkers() {
    try {
        const response = await fetch(`/api/v1/labor/workers?farm_id=${activeFarmId}`);
        const data = await response.json();

        if (data.status === 'success') {
            workerData = data.data;
            renderWorkers();
        }
    } catch (e) {
        console.error("Labor registry offline");
    }
}

function renderWorkers() {
    const tbody = document.getElementById('worker-body');
    tbody.innerHTML = workerData.map(w => `
        <tr onclick="viewPayroll(${w.id})">
            <td><strong>${w.name}</strong></td>
            <td>${w.worker_type}</td>
            <td>
                <span style="font-size: 0.8rem;">Hourly: ₹${w.hourly_rate}</span><br>
                <span style="font-size: 0.8rem;">Piece: ₹${w.piece_rate}/kg</span>
            </td>
            <td><span class="status-pill ${w.active ? 'status-active' : 'status-inactive'}">${w.active ? 'ACTIVE' : 'INACTIVE'}</span></td>
        </tr>
    `).join('');
}

async function viewPayroll(workerId) {
    try {
        const response = await fetch(`/api/v1/labor/payroll/history/${workerId}`);
        const data = await response.json();

        if (data.status === 'success') {
            renderPayrollHistory(data.data);
        }
    } catch (e) { }
}

function renderPayrollHistory(history) {
    const container = document.getElementById('payroll-ledger');
    if (history.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 2rem; opacity: 0.5;">No payroll records found.</p>';
        return;
    }

    container.innerHTML = history.map(p => `
        <div style="padding: 1rem; border-bottom: 1px solid #f1f5f9; cursor: pointer;" onclick="showSlip(${JSON.stringify(p).replace(/"/g, '&quot;')})">
            <div style="display: flex; justify-content: space-between;">
                <strong>${p.period}</strong>
                <span style="font-weight: 700; color: var(--success);">₹${p.net.toLocaleString()}</span>
            </div>
            <div style="font-size: 0.8rem; opacity: 0.6;">Status: ${p.status}</div>
        </div>
    `).join('');
}

function showSlip(payroll) {
    const placeholder = document.getElementById('payslip-placeholder');
    const content = document.getElementById('payslip-content');
    placeholder.style.display = 'block';

    content.innerHTML = `
        <div style="text-align: center; border-bottom: 2px solid #333; padding-bottom: 1rem; margin-bottom: 1rem;">
            <h2 style="margin: 0;">OFFICIAL PAYSLIP</h2>
            <p style="margin: 0; font-size: 0.8rem;">AgriTech Precision Payroll System</p>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.9rem;">
            <div><strong>Worker:</strong> ${payroll.worker_name}</div>
            <div><strong>Period:</strong> ${payroll.period}</div>
            <div style="grid-column: span 2; border-top: 1px solid #ddd; padding-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>Gross Earnings:</span>
                    <span>₹${payroll.gross.toLocaleString()}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; color: var(--danger);">
                    <span>Total Deductions:</span>
                    <span>- ₹${payroll.deductions.toLocaleString()}</span>
                </div>
                <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 1.2rem; border-top: 2px solid #333; padding-top: 0.5rem; margin-top: 0.5rem;">
                    <span>NET PAYABLE:</span>
                    <span>₹${payroll.net.toLocaleString()}</span>
                </div>
            </div>
        </div>
        <div style="margin-top: 1.5rem; font-size: 0.75rem; text-align: center; opacity: 0.5;">
            Digitally generated on ${new Date().toLocaleDateString()}
        </div>
    `;
}

async function openClockModal() {
    const { value: workerId } = await Swal.fire({
        title: 'Attendance Terminal',
        input: 'select',
        inputOptions: Object.fromEntries(workerData.map(w => [w.id, w.name])),
        showCancelButton: true,
        confirmButtonText: 'Clock-In',
        showDenyButton: true,
        denyButtonText: 'Clock-Out',
        denyButtonColor: 'var(--danger)'
    });

    if (workerId) {
        // Simple logic for brevity in demo
        fetch('/api/v1/labor/clock-in', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ worker_id: workerId })
        }).then(() => Swal.fire('Clocked In', 'Shift timer started.', 'success'));
    }
}

async function openLogHarvestModal() {
    const { value: formValues } = await Swal.fire({
        title: 'Log Daily Harvest',
        html:
            `<select id="swal-w" class="swal2-input">${workerData.map(w => `<option value="${w.id}">${w.name}</option>`).join('')}</select>` +
            '<input id="swal-crop" class="swal2-input" placeholder="Crop (e.g., Mangoes)">' +
            '<input id="swal-qty" class="swal2-input" placeholder="Quantity (kg)" type="number">',
        preConfirm: () => ({
            worker_id: document.getElementById('swal-w').value,
            crop: document.getElementById('swal-crop').value,
            quantity: document.getElementById('swal-qty').value
        })
    });

    if (formValues) {
        fetch('/api/v1/labor/harvest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formValues)
        }).then(() => Swal.fire('Logged', 'Harvest piece-rate added to ledger.', 'success'));
    }
}
