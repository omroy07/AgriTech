// Configuration
const API_BASE_URL = window.location.port === '5000' ? '' : 'http://127.0.0.1:5000';

// Initialize Map
const map = L.map('map').setView([20.5937, 78.9629], 5); // Center on India

// Tile Layers
// 1. Satellite (Esri World Imagery)
const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri'
});

// 2. Street (OpenStreetMap)
const streetLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
});

satelliteLayer.addTo(map);

// Leaflet Draw Controls
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    },
    draw: {
        polygon: true,
        rectangle: true,
        circle: false,
        marker: false,
        polyline: false,
        circlemarker: false
    }
});
map.addControl(drawControl);

// Internal State
let userFields = [];
let lastDrawnLayer = null;

// Event: Created a shape
map.on(L.Draw.Event.CREATED, function (event) {
    const layer = event.layer;
    drawnItems.addLayer(layer);
    lastDrawnLayer = layer; // Store for the "Save Field" button

    // Zoom to it
    map.fitBounds(layer.getBounds());
});

// UI Handlers for Sidebar
document.getElementById('draw-btn').addEventListener('click', (e) => {
    e.preventDefault();
    new L.Draw.Polygon(map, drawControl.options.draw.polygon).enable();
});

document.getElementById('save-sidebar-btn').addEventListener('click', (e) => {
    e.preventDefault();
    window.saveCurrentField();
});

document.getElementById('analyze-btn').addEventListener('click', (e) => {
    e.preventDefault();
    if (userFields.length > 0) {
        analyzeField(userFields[0].id); // Analyze first field by default if none selected
    } else {
        alert("Please draw and save a field first!");
    }
});

window.saveCurrentField = function () {
    if (!lastDrawnLayer) {
        alert("Please draw a field on the map first using the polygon tool.");
        return;
    }
    const name = prompt("Enter Field Name:");
    if (name) {
        // Simple loading indicator
        const saveBtn = document.querySelector('.btn-primary');
        const originalText = saveBtn.innerText;
        saveBtn.innerText = "Saving...";
        saveBtn.disabled = true;

        saveFieldToBackend(name, lastDrawnLayer.toGeoJSON()).finally(() => {
            saveBtn.innerText = originalText;
            saveBtn.disabled = false;
        });
    }
};

// --- API Interactions ---

async function saveFieldToBackend(name, geoJson) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/spatial/fields`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                boundary: geoJson.geometry
            })
        });

        const result = await response.json();
        if (response.ok) {
            alert("Field saved successfully!");
            lastDrawnLayer = null; // Reset
            loadFields(); // Refresh list to show saved fields
        } else {
            console.error("Save failed:", result);
            alert("Error saving field: " + (result.error || "Unknown error"));
        }
    } catch (err) {
        console.error("Network Fetch Error:", err);
        alert("Network Error: Could not connect to server.");
    }
}

async function loadFields() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/spatial/fields`);
        const fields = await response.json();
        userFields = fields;

        // Clear current items (except currently drawn ones if any? Just clear all for sync)
        drawnItems.clearLayers();

        fields.forEach(field => {
            if (field.boundary_geojson) {
                try {
                    const geoJson = typeof field.boundary_geojson === 'string'
                        ? JSON.parse(field.boundary_geojson)
                        : field.boundary_geojson;

                    const layer = L.geoJSON(geoJson, {
                        style: { color: "#10b981", weight: 2 }
                    });

                    // Add popup
                    layer.bindPopup(`
                        <b>${field.name}</b><br>
                        <button onclick="analyzeField(${field.id})">Analyze Field</button>
                        <button onclick="zoomTo(${fields.indexOf(field)})">Zoom</button>
                    `);

                    drawnItems.addLayer(layer);
                } catch (e) {
                    console.error("Error parsing field GeoJSON:", e, field);
                }
            }
        });

    } catch (err) {
        console.error("Failed to load fields", err);
    }
}

// Global function (attached to window) for Popup functionality
// Global function (attached to window) for Popup functionality
window.analyzeField = async function (fieldId) {
    // Show loading state
    document.getElementById('ndvi-val').innerText = "Loading...";

    try {
        const response = await fetch(`${API_BASE_URL}/api/spatial/analyze/${fieldId}`, { method: 'POST' });
        const result = await response.json();

        if (response.ok) {
            // Update Stats with randomized but realistic logic for demo
            const stats = result.result_data;
            document.getElementById('ndvi-val').innerText = stats.mean.toFixed(2);

            // Derive other stats from health score
            const health = stats.health_score;

            // Update Health Text and Bar
            const healthText = document.getElementById('health-text');
            const healthBar = document.getElementById('health-bar');

            if (health > 75) {
                healthText.innerText = "Excellent";
                healthText.className = "value-large text-green";
            } else if (health > 50) {
                healthText.innerText = "Good";
                healthText.className = "value-large text-green"; // or yellow/orange css if exists
            } else {
                healthText.innerText = "Poor";
                healthText.className = "value-large text-red"; // Assume text-red exists or default
            }
            healthBar.style.width = `${health}%`;

            // Update other metrics
            document.getElementById('moisture-val').innerText = (30 + (health / 4)).toFixed(1) + "%";
            document.getElementById('temp-val').innerText = (25 + Math.random() * 5).toFixed(1) + "°C";

            // Update Recommendations
            const recList = document.getElementById('rec-list');
            recList.innerHTML = `
                <li><i class="fas fa-check-circle text-green"></i> Analysis Complete: ${health}/100 Health Score</li>
                <li><i class="fas fa-droplet text-blue"></i> Moisture levels are ${health > 60 ? 'optimal' : 'low'}.</li>
                <li><i class="fas fa-info-circle text-gray"></i> Recommended Action: ${health > 80 ? 'No action needed.' : 'Schedule irrigation soon.'}</li>
            `;

            // Add Overlay
            if (result.overlay_image_path) {
                const field = userFields.find(f => f.id === fieldId);
                if (!field) {
                    console.error("Field not found in local userFields array:", fieldId);
                    alert("Analysis complete, but could not locate field on map.");
                    return;
                }
                const geoJson = typeof field.boundary_geojson === 'string'
                    ? JSON.parse(field.boundary_geojson)
                    : field.boundary_geojson;

                const geoLayer = L.geoJSON(geoJson);
                const bounds = geoLayer.getBounds();

                // Ensure image path is absolute if using external backend
                // Note: Flask serves static files from root, so 'uploads/...' is relative to root URL.
                // We add a timestamp to force reload image if it changes
                const imageUrl = result.overlay_image_path.startsWith('http')
                    ? result.overlay_image_path
                    : `${API_BASE_URL}/${result.overlay_image_path}?t=${new Date().getTime()}`;

                console.log("Adding overlay:", imageUrl);

                // Clear previous overlays
                if (window.currentNDVIOverlay) {
                    map.removeLayer(window.currentNDVIOverlay);
                }

                const overlay = L.imageOverlay(imageUrl, bounds, {
                    opacity: 0.7,
                    interactive: true
                }).addTo(map);

                window.currentNDVIOverlay = overlay;
            }
        } else {
            alert("Analysis failed: " + result.error);
        }
    } catch (err) {
        console.error("Analysis Error Details:", err);
        alert(`Error executing analysis: ${err.message || "Network Error"}`);
    }
};

window.zoomTo = function (index) {
    const field = userFields[index];
    const geoJson = typeof field.boundary_geojson === 'string'
        ? JSON.parse(field.boundary_geojson)
        : field.boundary_geojson;
    const geoLayer = L.geoJSON(geoJson);
    map.fitBounds(geoLayer.getBounds());
};

// --- Initialization ---
loadFields();

// UI Toggles
document.getElementById('layer-select').addEventListener('change', (e) => {
    const value = e.target.value;

    // Reset view first
    map.removeLayer(streetLayer);
    satelliteLayer.addTo(map);

    if (value === 'satellite') {
        // Just satellite (already set)
        if (window.currentNDVIOverlay) {
            map.removeLayer(window.currentNDVIOverlay);
            window.currentNDVIOverlay = null; // Clear reference
        }
    } else if (value === 'ndvi') {
        // NDVI View
        if (window.currentNDVIOverlay) {
            window.currentNDVIOverlay.addTo(map);
        } else {
            alert("Please select a field and click 'Analyze' to generate NDVI data first.");
        }
    } else if (value === 'soil') {
        // Mock Soil View
        alert("Soil Moisture data layer is currently simulated based on vegetation health. Real-time sensor integration coming soon.");
        // We could reuse the NDVI overlay if available, as a proxy
        if (window.currentNDVIOverlay) {
            window.currentNDVIOverlay.addTo(map);
        }
    }
});
