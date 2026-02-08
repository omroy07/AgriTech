let selectedItemId = null;

document.addEventListener('DOMContentLoaded', () => {
    fetchCatalog();
    fetchMyOrders();
});

async function fetchCatalog() {
    const list = document.getElementById('catalog-list');
    try {
        const response = await fetch('/api/v1/procurement/items');
        const data = await response.json();

        if (data.status === 'success') {
            list.innerHTML = data.data.map(item => `
                <div class="item-card">
                    <div style="font-weight: 700;">${item.name}</div>
                    <div style="font-size: 0.8rem; color: #64748b;">Vendor: ${item.vendor_name}</div>
                    <div style="margin: 1rem 0;">
                        <span class="price-badge">₹${item.base_price}/unit</span>
                    </div>
                    <button class="btn" style="width: 100%; font-size: 0.8rem;" onclick="openOrderModal(${item.id}, '${item.name}')">Initiate Order</button>
                </div>
            `).join('');
        }
    } catch (e) {
        list.innerHTML = '<p>Offline Mode: Failed to load catalog.</p>';
        // Mock data for demo
        const mock = [{ id: 1, name: 'DAP Fertilizer', vendor_name: 'Iffco Ltd', base_price: 1200 }];
        list.innerHTML = renderMockItems(mock);
    }
}

function renderMockItems(items) {
    return items.map(item => `
        <div class="item-card">
            <div style="font-weight: 700;">${item.name}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Vendor: ${item.vendor_name}</div>
            <div style="margin: 1rem 0;">
                <span class="price-badge">₹${item.base_price}/unit</span>
            </div>
            <button class="btn" style="width: 100%; font-size: 0.8rem;" onclick="openOrderModal(${item.id}, '${item.name}')">Initiate Order</button>
        </div>
    `).join('');
}

async function fetchMyOrders() {
    const list = document.getElementById('active-orders');
    try {
        const response = await fetch('/api/v1/procurement/orders');
        const data = await response.json();

        if (data.status === 'success' && data.data.length > 0) {
            list.innerHTML = data.data.map(o => `
                <div class="order-item">
                    <div style="display: flex; justify-content: space-between;">
                        <strong>Order #${o.id}</strong>
                        <span class="status-pill status-${o.status.toLowerCase()}">${o.status}</span>
                    </div>
                    <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                        Amount: ₹${o.total_amount.toLocaleString()}
                    </div>
                </div>
            `).join('');
        }
    } catch (e) { }
}

function openOrderModal(id, name) {
    selectedItemId = id;
    document.getElementById('modal-item-name').textContent = `Product: ${name}`;
    document.getElementById('order-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('order-modal').style.display = 'none';
}

async function submitOrder() {
    const qty = document.getElementById('order-qty').value;

    try {
        const response = await fetch('/api/v1/procurement/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                item_id: selectedItemId,
                quantity: parseFloat(qty)
            })
        });

        const data = await response.json();
        if (data.status === 'success') {
            closeModal();
            Swal.fire('Order Proposed', `Order ID: ${data.data.order_id}. Waiting for vendor vetting.`, 'success');
            fetchMyOrders();
        }
    } catch (e) {
        Swal.fire('System Error', 'Could not transmit order to blockchain node.', 'error');
    }
}
