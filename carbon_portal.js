document.addEventListener('DOMContentLoaded', () => {
    fetchImpact();
    fetchPractices();
});

async function fetchImpact() {
    try {
        const response = await fetch('/api/v1/sustainability/impact');
        const data = await response.json();
        if (data.status === 'success') {
            document.getElementById('total-offset').textContent = data.data.total_co2_offset;
            document.getElementById('active-count').textContent = data.data.practice_count;
            document.getElementById('active-credits').textContent = data.data.active_credits;
        }
    } catch (e) {
        console.error('Impact fetch failed');
    }
}

async function fetchPractices() {
    // In real app, we would have a GET /practices endpoint (here we simulate or use impact data)
    const list = document.getElementById('practice-list');
    list.innerHTML = '<tr><td colspan="5" style="text-align: center;">Syncing with ledger...</td></tr>';

    // Simulate fetching based on typical data structure
    setTimeout(() => {
        const mockData = [
            { type: 'No-Till', area: 45, offset: 12.4, status: 'Certified', id: 101 },
            { type: 'Cover Cropping', area: 20, offset: 3.2, status: 'Pending', id: 102 }
        ];

        list.innerHTML = mockData.map(p => `
            <tr>
                <td><strong>${p.type}</strong></td>
                <td>${p.area} Acres</td>
                <td style="color: var(--green); font-weight: 700;">${p.offset} T</td>
                <td><span class="status-badge status-${p.status.toLowerCase()}">${p.status}</span></td>
                <td>
                    ${p.status === 'Certified' ?
                `<button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.7rem; background: var(--slate); color: white;" onclick="issueCredits(${p.id})">Issue Credits</button>` :
                `<button class="btn" style="padding: 0.25rem 0.5rem; font-size: 0.7rem;" disabled>Verifying...</button>`
            }
                </td>
            </tr>
        `).join('');
    }, 800);
}

function openPracticeModal() {
    document.getElementById('practice-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('practice-modal').style.display = 'none';
}

async function submitPractice() {
    const type = document.getElementById('p-type').value;
    const area = document.getElementById('p-area').value;
    const date = document.getElementById('p-start').value;

    if (!area || !date) return Swal.fire('Error', 'Please fill all fields', 'error');

    try {
        const response = await fetch('/api/v1/sustainability/practices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                practice_type: type,
                area: parseFloat(area),
                start_date: date
            })
        });
        const data = await response.json();

        if (data.status === 'success') {
            closeModal();
            Swal.fire('Logged!', 'Sequestration monitoring started. Request an audit soon.', 'success');
            fetchImpact();
            fetchPractices();
        }
    } catch (e) {
        Swal.fire('Error', 'Ledger communication failed', 'error');
    }
}

async function issueCredits(practiceId) {
    const result = await Swal.fire({
        title: 'Issue Carbon Credits?',
        text: "This will convert your verified CO2 offsets into tradeable units on the marketplace.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#059669',
        confirmButtonText: 'Yes, Issue Credits'
    });

    if (result.isConfirmed) {
        try {
            const response = await fetch(`/api/v1/credits/issue/${practiceId}`, { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                Swal.fire('Success!', `Issued ${data.data.amount} credits. Serial: ${data.data.serial_number}`, 'success');
                fetchImpact();
            } else {
                Swal.fire('Error', data.message, 'error');
            }
        } catch (e) {
            Swal.fire('Error', 'Blockchain/Ledger timeout', 'error');
        }
    }
}
