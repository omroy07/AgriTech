const API_BASE = '/api/v1/iot';

let currentUser = null;

async function init() {
    await loadUserData();
    await loadSensors();
    await loadAlerts();
    await loadStats();
    setInterval(loadSensors, 30000);
}

async function loadUserData() {
    const token = localStorage.getItem('token');
    if (token) {
        try {
            const response = await fetch('/api/v1/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                currentUser = data.data;
                loadFarms();
            }
        } catch (error) {
            console.error('Error loading user:', error);
        }
    }
}

async function loadFarms() {
    if (!currentUser) return;
    
    const farmSelect = document.getElementById('farmId');
    farmSelect.innerHTML = '<option value="">Select Farm</option>';
    
    const token = localStorage.getItem('token');
    try {
        const response = await fetch('/api/v1/farms', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            data.data.forEach(farm => {
                const option = document.createElement('option');
                option.value = farm.id;
                option.textContent = farm.name;
                farmSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading farms:', error);
    }
}

async function loadSensors() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE}/sensors`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            renderSensors(data.data);
        }
    } catch (error) {
        console.error('Error loading sensors:', error);
    }
}

function renderSensors(sensors) {
    const container = document.getElementById('sensorsContainer');
    
    if (sensors.length === 0) {
        container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #64748b;">No sensors registered yet. Add your first sensor to get started!</p>';
        return;
    }
    
    container.innerHTML = sensors.map(sensor => `
        <div class="sensor-card">
            <div class="sensor-header">
                <div>
                    <h4 style="margin: 0;">${sensor.sensor_type.replace('_', ' ').toUpperCase()}</h4>
                    <small style="color: #64748b;">${sensor.location}</small>
                </div>
                <span class="sensor-status ${sensor.is_active ? 'status-active' : 'status-inactive'}">
                    ${sensor.is_active ? 'Active' : 'Inactive'}
                </span>
            </div>
            <div class="reading-grid" id="readings-${sensor.id}">
                <div class="reading-item">
                    <div class="label">Last Update</div>
                    <div class="value" style="font-size: 1rem;">${sensor.last_seen ? new Date(sensor.last_seen).toLocaleString() : 'Never'}</div>
                </div>
                <div class="reading-item">
                    <div class="label">Status</div>
                    <div class="value" style="font-size: 1rem;">${sensor.is_active ? 'Online' : 'Offline'}</div>
                </div>
            </div>
            <button class="btn btn-primary" style="margin-top: 1rem; width: 100%;" onclick="viewSensorDetails(${sensor.id})">
                View Details
            </button>
        </div>
    `).join('');
    
    sensors.forEach(sensor => {
        loadSensorReadings(sensor.id);
    });
}

async function loadSensorReadings(sensorId) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE}/sensors/${sensorId}/readings?hours=24`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            if (data.data && data.data.length > 0) {
                const latestReading = data.data[0];
                updateSensorCard(sensorId, latestReading);
            }
        }
    } catch (error) {
        console.error('Error loading readings:', error);
    }
}

function updateSensorCard(sensorId, reading) {
    const container = document.getElementById(`readings-${sensorId}`);
    if (!container || !reading) return;
    
    let readingsHtml = '';
    
    if (reading.soil_moisture !== null) {
        readingsHtml += `
            <div class="reading-item">
                <div class="label">Soil Moisture</div>
                <div class="value">${reading.soil_moisture.toFixed(1)}%</div>
            </div>
        `;
    }
    
    if (reading.temperature !== null) {
        readingsHtml += `
            <div class="reading-item">
                <div class="label">Temperature</div>
                <div class="value">${reading.temperature.toFixed(1)}C</div>
            </div>
        `;
    }
    
    if (reading.humidity !== null) {
        readingsHtml += `
            <div class="reading-item">
                <div class="label">Humidity</div>
                <div class="value">${reading.humidity.toFixed(1)}%</div>
            </div>
        `;
    }
    
    if (reading.ph_level !== null) {
        readingsHtml += `
            <div class="reading-item">
                <div class="label">pH Level</div>
                <div class="value">${reading.ph_level.toFixed(1)}</div>
            </div>
        `;
    }
    
    if (reading.battery_level !== null) {
        readingsHtml += `
            <div class="reading-item">
                <div class="label">Battery</div>
                <div class="value">${reading.battery_level.toFixed(0)}%</div>
            </div>
        `;
    }
    
    if (reading.signal_strength !== null) {
        readingsHtml += `
            <div class="reading-item">
                <div class="label">Signal</div>
                <div class="value">${reading.signal_strength.toFixed(0)}%</div>
            </div>
        `;
    }
    
    container.innerHTML = readingsHtml || '<div style="grid-column: 1/-1; text-align: center; color: #64748b;">No readings available</div>';
}

async function loadAlerts() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE}/alerts`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            renderAlerts(data.data);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

function renderAlerts(alerts) {
    const container = document.getElementById('alertsContainer');
    
    if (alerts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b;">No active alerts. Great job!</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item alert-${alert.severity.toLowerCase()}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>${alert.alert_type.replace('_', ' ').toUpperCase()}</strong>
                    <p style="margin: 0.25rem 0 0 0;">${alert.message}</p>
                    <small style="color: #64748b;">${new Date(alert.created_at).toLocaleString()}</small>
                </div>
                <button class="btn btn-primary" style="padding: 0.5rem 1rem; font-size: 0.875rem;" onclick="resolveAlert(${alert.id})">
                    Resolve
                </button>
            </div>
        </div>
    `).join('');
}

async function resolveAlert(alertId) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/resolve`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (response.ok) {
            await loadAlerts();
        }
    } catch (error) {
        console.error('Error resolving alert:', error);
    }
}

async function loadStats() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const sensorsResponse = await fetch(`${API_BASE}/sensors`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (sensorsResponse.ok) {
            const sensorsData = await sensorsResponse.json();
            const activeSensors = sensorsData.data.filter(s => s.is_active);
            document.getElementById('activeSensors').textContent = activeSensors.length;
            
            let totalReadings = 0;
            let totalMoisture = 0;
            let moistureCount = 0;
            
            for (const sensor of activeSensors) {
                const readingsResponse = await fetch(`${API_BASE}/sensors/${sensor.id}/readings?hours=24`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (readingsResponse.ok) {
                    const readingsData = await readingsResponse.json();
                    totalReadings += readingsData.data.length;
                    
                    readingsData.data.forEach(reading => {
                        if (reading.soil_moisture !== null) {
                            totalMoisture += reading.soil_moisture;
                            moistureCount++;
                        }
                    });
                }
            }
            
            document.getElementById('totalReadings').textContent = totalReadings;
            
            if (moistureCount > 0) {
                document.getElementById('avgMoisture').textContent = `${(totalMoisture / moistureCount).toFixed(1)}%`;
            }
        }
        
        const alertsResponse = await fetch(`${API_BASE}/alerts`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        if (alertsResponse.ok) {
            const alertsData = await alertsResponse.json();
            document.getElementById('activeAlerts').textContent = alertsData.data.length;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function openAddSensorModal() {
    document.getElementById('addSensorModal').classList.add('active');
}

function closeAddSensorModal() {
    document.getElementById('addSensorModal').classList.remove('active');
    document.getElementById('sensorId').value = '';
    document.getElementById('farmId').value = '';
    document.getElementById('sensorLocation').value = '';
}

async function addSensor(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login first');
        return;
    }
    
    const sensorData = {
        sensor_id: document.getElementById('sensorId').value,
        farm_id: parseInt(document.getElementById('farmId').value),
        sensor_type: document.getElementById('sensorType').value,
        location: document.getElementById('sensorLocation').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/sensors`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(sensorData)
        });
        
        if (response.ok) {
            closeAddSensorModal();
            loadSensors();
            loadStats();
            alert('Sensor added successfully!');
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.message}`);
        }
    } catch (error) {
        console.error('Error adding sensor:', error);
        alert('Error adding sensor. Please try again.');
    }
}

async function viewSensorDetails(sensorId) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const historyResponse = await fetch(`${API_BASE}/sensors/${sensorId}/history?days=7`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            const history = historyData.data;
            
            const stats = history.stats || {};
            let statsHtml = 'Historical Data (Last 7 Days):\n\n';
            
            if (stats.soil_moisture_avg) {
                statsHtml += `Average Soil Moisture: ${stats.soil_moisture_avg.toFixed(1)}%\n`;
            }
            if (stats.temperature_avg) {
                statsHtml += `Average Temperature: ${stats.temperature_avg.toFixed(1)}C\n`;
            }
            if (stats.humidity_avg) {
                statsHtml += `Average Humidity: ${stats.humidity_avg.toFixed(1)}%\n`;
            }
            
            alert(statsHtml);
        }
    } catch (error) {
        console.error('Error loading sensor details:', error);
        alert('Error loading sensor details');
    }
}

document.addEventListener('DOMContentLoaded', init);
