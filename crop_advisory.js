const API_BASE = '/api/v1/crop-advisory';

async function getRecommendations() {
    const location = document.getElementById('location').value;
    const soilType = document.getElementById('soilType').value;
    
    if (!location) {
        alert('Please enter a location');
        return;
    }
    
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login first');
        return;
    }
    
    try {
        document.getElementById('recommendationsCard').classList.add('hidden');
        document.getElementById('alertsCard').classList.add('hidden');
        document.getElementById('climateCard').classList.add('hidden');
        document.getElementById('weatherStats').classList.add('hidden');
        
        const response = await fetch(`${API_BASE}/recommendations?location=${encodeURIComponent(location)}&soil_type=${soilType || ''}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderRecommendations(data.data);
            
            document.getElementById('statTemp').textContent = `${data.data.current_weather.temperature}C`;
            document.getElementById('statHumidity').textContent = `${data.data.current_weather.humidity}%`;
            document.getElementById('statCondition').textContent = data.data.current_weather.condition;
            document.getElementById('weatherStats').classList.remove('hidden');
            
            loadAlerts();
            loadClimateAnalysis(location);
        } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.message}`);
        }
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        alert('Error fetching recommendations. Please try again.');
    }
}

function renderRecommendations(data) {
    const container = document.getElementById('recommendationsContainer');
    
    if (!data.recommendations || data.recommendations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b;">No recommendations available for this location.</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="current-weather">
            <div class="weather-item">
                <div class="label">Current Month</div>
                <div class="value">${data.current_month}</div>
            </div>
            <div class="weather-item">
                <div class="label">Temperature</div>
                <div class="value">${data.current_weather.temperature}C</div>
            </div>
            <div class="weather-item">
                <div class="label">Humidity</div>
                <div class="value">${data.current_weather.humidity}%</div>
            </div>
        </div>
        <div class="recommendations-grid">
            ${data.recommendations.map(rec => `
                <div class="recommendation-item">
                    <div class="recommendation-header">
                        <div class="recommendation-title">${rec.crop}</div>
                        <div class="score-badge">${rec.score}% Match</div>
                    </div>
                    <ul class="reasons-list">
                        ${rec.reasons.map(reason => `<li>${reason}</li>`).join('')}
                    </ul>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Planting Time</label>
                            <span>${rec.planting_time.join(', ')}</span>
                        </div>
                        <div class="info-item">
                            <label>Harvesting Time</label>
                            <span>${rec.harvesting_time.join(', ')}</span>
                        </div>
                        <div class="info-item">
                            <label>Water Requirement</label>
                            <span>${rec.water_requirement}</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    
    document.getElementById('recommendationsCard').classList.remove('hidden');
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
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #64748b;">No active alerts. Great!</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="alert-item alert-${alert.priority.toLowerCase()}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: var(--primary);">${alert.type}</strong>
                    <p style="margin: 0.5rem 0;">${alert.message}</p>
                    <small style="color: #64748b;">
                        <i class="fas fa-map-marker-alt"></i> ${alert.location} | 
                        <i class="fas fa-calendar"></i> ${alert.crop}
                    </small>
                </div>
                <div style="text-align: right;">
                    <div style="color: var(--accent); font-weight: 600; margin-bottom: 0.5rem;">${alert.priority}</div>
                    <div style="font-size: 0.875rem;">${alert.action}</div>
                </div>
            </div>
        </div>
    `).join('');
    
    document.getElementById('alertsCard').classList.remove('hidden');
}

async function loadClimateAnalysis(location) {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch(`${API_BASE}/climate-analysis?location=${encodeURIComponent(location)}&days=30`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            renderClimateAnalysis(data.data);
        }
    } catch (error) {
        console.error('Error loading climate analysis:', error);
    }
}

function renderClimateAnalysis(data) {
    const container = document.getElementById('climateContainer');
    
    if (data.error) {
        container.innerHTML = `<p style="text-align: center; color: #64748b;">${data.error}</p>`;
        return;
    }
    
    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
            <div class="info-item">
                <label>Average Temperature</label>
                <span>${data.average_temperature}C</span>
            </div>
            <div class="info-item">
                <label>Average Humidity</label>
                <span>${data.average_humidity}%</span>
            </div>
            <div class="info-item">
                <label>Total Rainfall</label>
                <span>${data.total_rainfall}mm</span>
            </div>
            <div class="info-item">
                <label>Rainy Days</label>
                <span>${data.rainy_days}</span>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
            <div class="info-item">
                <label>Temperature Trend</label>
                <span>${data.temperature_trend} (${data.temperature_change > 0 ? '+' : ''}${data.temperature_change}C)</span>
            </div>
            <div class="info-item">
                <label>Analysis Period</label>
                <span>${data.period_days} days</span>
            </div>
        </div>
        ${data.advisory ? `
            <div style="margin-top: 1rem; padding: 1rem; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                <strong style="color: #92400e;"><i class="fas fa-exclamation-triangle"></i> Advisory:</strong>
                <p style="margin: 0.5rem 0 0 0; color: #92400e;">${data.advisory}</p>
            </div>
        ` : ''}
        ${data.rainfall_advisory ? `
            <div style="margin-top: 1rem; padding: 1rem; background: #dbeafe; border-radius: 8px; border-left: 4px solid #3b82f6;">
                <strong style="color: #1e40af;"><i class="fas fa-cloud-rain"></i> Rainfall Advisory:</strong>
                <p style="margin: 0.5rem 0 0 0; color: #1e40af;">${data.rainfall_advisory}</p>
            </div>
        ` : ''}
    `;
    
    document.getElementById('climateCard').classList.remove('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('location').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            getRecommendations();
        }
    });
});
