let warehouseId = 1; // Demo warehouse
let inventoryData = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchInventory();
    fetchExpiryAlerts();
});

async function fetchInventory() {
    try {
        const response = await fetch(`/api/v1/warehouse/stock?warehouse_id=${warehouseId}`);
        const data = await response.json();

        if (data.status === 'success') {
            inventoryData = data.data;
            renderInventory();
            updateStats();
        }
    } catch (e) {
        console.error('Failed to sync inventory');
    }
}

function renderInventory() {
    const tbody = document.getElementById('inventory-body');

    tbody.innerHTML = inventoryData.map(item => {
        let statusClass = 'badge-healthy';
        let statusText = 'Healthy';

        if (item.reorder_point && item.quantity <= item.reorder_point) {
            statusClass = 'badge-critical';
            statusText = 'Reorder';
        } else if (item.reorder_point && item.quantity <= item.reorder_point * 1.5) {
            statusClass = 'badge-low';
            statusText = 'Low';
        }

        return `
            <tr>
                <td><strong>${item.sku}</strong></td>
                <td>${item.name}</td>
                <td>${item.category}</td>
                <td>${item.quantity} ${item.unit}</td>
                <td>${item.reorder_point || 'N/A'}</td>
                <td><span class="stock-badge ${statusClass}">${statusText}</span></td>
                <td>${item.expiry || 'N/A'}</td>
            </tr>
        `;
    }).join('');
}

function updateStats() {
    const total = inventoryData.length;
    const low = inventoryData.filter(i => i.reorder_point && i.quantity <= i.reorder_point * 1.5).length;
    const critical = inventoryData.filter(i => i.reorder_point && i.quantity <= i.reorder_point).length;
    const healthy = total - low;

    document.getElementById('total-items').textContent = total;
    document.getElementById('healthy-stock').textContent = healthy;
    document.getElementById('low-stock').textContent = low;
}

async function fetchExpiryAlerts() {
    try {
        const response = await fetch(`/api/v1/warehouse/expiring?warehouse_id=${warehouseId}&days=30`);
        const data = await response.json();

        if (data.status === 'success') {
            const container = document.getElementById('alerts-container');
            document.getElementById('expiring-soon').textContent = data.data.length;

            if (data.data.length === 0) {
                container.innerHTML = '<p style="text-align: center; opacity: 0.5;">No expiry alerts</p>';
            } else {
                container.innerHTML = data.data.map(alert => `
                    <div class="alert-item">
                        <strong>${alert.item.name}</strong>
                        <div style="font-size: 0.85rem; margin-top: 0.5rem;">
                            SKU: ${alert.item.sku} | Expires in ${alert.days_left} days
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (e) { }
}

async function openStockInModal() {
    const { value: formValues } = await Swal.fire({
        title: 'Record Stock Receipt',
        html:
            '<select id="swal-item" class="swal2-input">' +
            inventoryData.map(i => `<option value="${i.id}">${i.name} (${i.sku})</option>`).join('') +
            '</select>' +
            '<input id="swal-qty" class="swal2-input" placeholder="Quantity" type="number">' +
            '<input id="swal-ref" class="swal2-input" placeholder="PO/Reference">',
        focusConfirm: false,
        preConfirm: () => ({
            stock_item_id: document.getElementById('swal-item').value,
            quantity: parseFloat(document.getElementById('swal-qty').value),
            reference: document.getElementById('swal-ref').value
        })
    });

    if (formValues) {
        try {
            const response = await fetch('/api/v1/warehouse/stock/in', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formValues)
            });

            if (response.ok) {
                Swal.fire('Stock Received', 'Inventory updated successfully', 'success');
                fetchInventory();
            }
        } catch (e) {
            Swal.fire('Error', 'Failed to record stock', 'error');
        }
    }
}

async function openStockOutModal() {
    const { value: formValues } = await Swal.fire({
        title: 'Issue Stock',
        html:
            '<select id="swal-item" class="swal2-input">' +
            inventoryData.map(i => `<option value="${i.id}">${i.name} (${i.sku})</option>`).join('') +
            '</select>' +
            '<input id="swal-qty" class="swal2-input" placeholder="Quantity" type="number">' +
            '<input id="swal-ref" class="swal2-input" placeholder="Invoice/Reference">',
        focusConfirm: false,
        preConfirm: () => ({
            stock_item_id: document.getElementById('swal-item').value,
            quantity: parseFloat(document.getElementById('swal-qty').value),
            reference: document.getElementById('swal-ref').value
        })
    });

    if (formValues) {
        try {
            const response = await fetch('/api/v1/warehouse/stock/out', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formValues)
            });

            if (response.ok) {
                Swal.fire('Stock Issued', 'Inventory updated successfully', 'success');
                fetchInventory();
            } else {
                const error = await response.json();
                Swal.fire('Error', error.message, 'error');
            }
        } catch (e) {
            Swal.fire('Error', 'Failed to issue stock', 'error');
        }
    }
}

async function performReconciliation() {
    Swal.fire({
        title: 'Stock Reconciliation',
        text: 'This will compare physical counts with book inventory',
        icon: 'info',
        timer: 2000
    });
}
