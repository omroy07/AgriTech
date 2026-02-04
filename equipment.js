let selectedEquipment = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchEquipment();

    // Listen for price calculation
    document.getElementById('start-date').addEventListener('change', updateEstimate);
    document.getElementById('end-date').addEventListener('change', updateEstimate);
});

async function fetchEquipment() {
    try {
        const response = await fetch('/api/v1/equipment/');
        const data = await response.json();

        if (data.status === 'success') {
            renderEquipment(data.data);
            document.getElementById('count').textContent = data.data.length;
        }
    } catch (error) {
        console.error('Failed to load equipment:', error);
    }
}

function renderEquipment(items) {
    const grid = document.getElementById('marketplace-grid');
    grid.innerHTML = '';

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'equipment-card';
        card.innerHTML = `
            <div class="image-container">
                ${item.image_url ? `<img src="${item.image_url}" style="width:100%; height:100%; object-fit:cover;">` : ''}
                <span class="category-badge">${item.category.toUpperCase()}</span>
            </div>
            <div class="card-content">
                <h3 class="card-title">${item.name}</h3>
                <div class="card-location"><i class="fas fa-map-marker-alt"></i> ${item.location}</div>
                <div class="price-tag">
                    <span class="price-val">₹${item.daily_rate}</span>
                    <span class="price-unit">/ day</span>
                </div>
                <button class="btn-rent" onclick="openBookingModal(${JSON.stringify(item).replace(/"/g, '&quot;')})">Check Availability</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function openBookingModal(item) {
    selectedEquipment = item;
    document.getElementById('modal-title').textContent = `Rent ${item.name}`;
    document.getElementById('estimate').textContent = '₹0';
    document.getElementById('booking-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('booking-modal').style.display = 'none';
}

function updateEstimate() {
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;

    if (start && end && selectedEquipment) {
        const d1 = new Date(start);
        const d2 = new Date(end);
        const diffTime = Math.abs(d2 - d1);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) || 1;

        const rent = diffDays * selectedEquipment.daily_rate;
        const deposit = rent * 0.2;
        document.getElementById('estimate').textContent = `₹${(rent + deposit).toLocaleString()}`;
    }
}

document.getElementById('confirm-booking-btn').onclick = async () => {
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;

    if (!start || !end) return Swal.fire('Error', 'Please select dates', 'error');

    try {
        const response = await fetch('/api/v1/bookings/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                equipment_id: selectedEquipment.id,
                start_time: start,
                end_time: end
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            closeModal();
            Swal.fire({
                title: 'Booking Confirmed!',
                text: 'Your funds are now held in escrow. Please coordinate pick-up with the owner.',
                icon: 'success',
                confirmButtonColor: '#16a34a'
            });
        } else {
            Swal.fire('Conflict', data.message, 'warning');
        }
    } catch (error) {
        console.error('Booking failed:', error);
        Swal.fire('Error', 'Communication with server failed', 'error');
    }
}
