let activeLoanId = 1; // Demo loan ID
let scheduleData = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchSchedule();
    fetchRiskScore();
});

async function fetchSchedule() {
    try {
        const response = await fetch(`/api/v1/loans/schedule/${activeLoanId}`);
        const data = await response.json();

        if (data.status === 'success') {
            scheduleData = data.data;
            renderSchedule();
            updateMetrics();
        }
    } catch (e) {
        console.error('Failed to sync repayment schedule');
    }
}

function renderSchedule() {
    const tbody = document.getElementById('schedule-body');
    const today = new Date().toISOString().split('T')[0];

    tbody.innerHTML = scheduleData.map(s => {
        let statusClass = 'badge-pending';
        let statusText = 'Pending';

        if (s.paid) {
            statusClass = 'badge-paid';
            statusText = 'Paid';
        } else if (s.due_date < today) {
            statusClass = 'badge-overdue';
            statusText = 'Overdue';
        }

        return `
            <tr>
                <td>${s.installment}</td>
                <td>${s.due_date}</td>
                <td>₹${s.principal.toLocaleString()}</td>
                <td>₹${s.interest.toLocaleString()}</td>
                <td><strong>₹${s.emi.toLocaleString()}</strong></td>
                <td>₹${s.balance.toLocaleString()}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            </tr>
        `;
    }).join('');
}

function updateMetrics() {
    const paid = scheduleData.filter(s => s.paid).length;
    const today = new Date().toISOString().split('T')[0];
    const overdue = scheduleData.filter(s => !s.paid && s.due_date < today).length;
    const pending = scheduleData.length - paid - overdue;

    document.getElementById('total-emi').textContent = scheduleData.length > 0 ? `₹${scheduleData[0].emi.toLocaleString()}` : '₹0';
    document.getElementById('paid-count').textContent = paid;
    document.getElementById('pending-count').textContent = pending;
    document.getElementById('overdue-count').textContent = overdue;
}

async function fetchRiskScore() {
    try {
        const response = await fetch(`/api/v1/loans/risk/${activeLoanId}`);
        const data = await response.json();

        if (data.status === 'success') {
            const risk = data.data;
            document.getElementById('risk-score').textContent = risk.risk_score;
            document.getElementById('days-overdue').textContent = risk.days_overdue;
            document.getElementById('consistency').textContent = `${(risk.consistency * 100).toFixed(0)}%`;

            // Animate risk meter
            document.getElementById('risk-fill').style.width = `${risk.risk_score}%`;

            // Color code
            const scoreEl = document.getElementById('risk-score');
            if (risk.risk_score < 30) {
                scoreEl.style.color = 'var(--success)';
            } else if (risk.risk_score < 60) {
                scoreEl.style.color = 'var(--warning)';
            } else {
                scoreEl.style.color = 'var(--danger)';
            }
        }
    } catch (e) {
        console.error('Risk assessment unavailable');
    }
}

async function makePayment() {
    // Find first unpaid installment
    const unpaid = scheduleData.find(s => !s.paid);
    if (!unpaid) {
        return Swal.fire('All Paid', 'All installments have been cleared!', 'success');
    }

    const { value: confirm } = await Swal.fire({
        title: `Pay Installment #${unpaid.installment}`,
        html: `
            <div style="text-align: left; padding: 1rem;">
                <p><strong>Due Date:</strong> ${unpaid.due_date}</p>
                <p><strong>Amount:</strong> ₹${unpaid.emi.toLocaleString()}</p>
                <p style="font-size: 0.85rem; opacity: 0.7;">This will be processed via UPI</p>
            </div>
        `,
        icon: 'info',
        showCancelButton: true,
        confirmButtonText: 'Confirm Payment'
    });

    if (confirm) {
        try {
            const response = await fetch('/api/v1/loans/pay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    loan_id: activeLoanId,
                    schedule_id: unpaid.id,
                    amount: unpaid.emi,
                    method: 'UPI'
                })
            });

            const data = await response.json();
            if (data.status === 'success') {
                Swal.fire('Payment Successful', `Transaction Ref: ${data.data.ref}`, 'success');
                fetchSchedule();
                fetchRiskScore();
            }
        } catch (e) {
            Swal.fire('Error', 'Payment processing failed', 'error');
        }
    }
}
