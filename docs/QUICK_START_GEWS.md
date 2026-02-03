# GEWS Feature - Quick Start Guide

## What is GEWS?

The **Geospatial Early Warning System (GEWS)** detects disease outbreaks on farms using GPS-tagged incident reports and spatial clustering. When an outbreak is detected, it automatically alerts farmers at risk.

## 5-Minute Quick Start

### Step 1: Install Dependencies
```bash
pip install geoalchemy2 shapely flask-jwt-extended
```

### Step 2: Run Database Migration
```bash
cd d:/AgriTech
python migrations/init_gews_db.py
python migrations/init_gews_db.py --sample
```

### Step 3: Set Environment Variables
```bash
# Optional: For AI-powered PDF reports
set GEMINI_API_KEY=your_gemini_api_key

# Optional: PostgreSQL with PostGIS
set DATABASE_URL=postgresql://user:pass@localhost/agritech
```

### Step 4: Start Services
```bash
# Terminal 1: Flask app
python app.py

# Terminal 2: Celery worker
celery -A backend.tasks worker --loglevel=info

# Terminal 3: Celery beat (required for hourly detection)
celery -A backend.tasks beat --loglevel=info
```

### Step 5: Test the API

#### Report a Disease Incident
```bash
curl -X POST http://localhost:5000/api/v1/disease/incidents ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"disease_name\": \"Late Blight\", \"crop_affected\": \"Tomato\", \"latitude\": 18.5204, \"longitude\": 73.8567, \"severity_level\": \"high\", \"affected_area\": 2.5}"
```

#### Check Your Farm's Risk
```bash
curl http://localhost:5000/api/v1/disease/my-risk ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### View Active Outbreaks
```bash
curl http://localhost:5000/api/v1/disease/outbreaks ^
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Key Concepts

### Disease Incident
A single report of disease from a farmer with GPS coordinates.

### Outbreak Zone
Automatically created when 3+ incidents are found within 50km radius for the same disease+crop combination.

### Outbreak Alert
Emergency notification sent to farmers within 75km (1.5x outbreak radius) of an active outbreak.

### Alert Priorities
- **Urgent**: Your farm is inside the outbreak zone (<50km)
- **High**: You're very close to the outbreak (50-60km)
- **Medium**: Take preventive action (60-75km)

## How It Works

1. **Farmers report diseases** via mobile app/web with GPS location
2. **Celery runs hourly** to analyze last 30 days of incidents
3. **Clustering algorithm** groups nearby incidents (50km radius)
4. **Outbreak zones created** when 3+ incidents found
5. **Alerts sent** to farmers within 75km via SocketIO
6. **PDF reports generated** with AI-powered preventative measures
7. **Real-time map updates** show outbreak zones

## Architecture Flow

```
Farmer Reports Incident (GPS tagged)
           ↓
    DiseaseIncident saved to DB
           ↓
    Hourly Celery Task runs
           ↓
   Spatial Clustering Analysis
           ↓
  OutbreakZone created (3+ incidents)
           ↓
    Find Farmers at Risk (75km)
           ↓
   Send SocketIO Alerts + Notifications
           ↓
  Generate AI PDF Report (Gemini)
           ↓
    OutbreakAlert saved with PDF link
```

## API Endpoints (Summary)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/disease/incidents` | POST | Report disease |
| `/api/v1/disease/incidents` | GET | Query incidents |
| `/api/v1/disease/outbreaks` | GET | List outbreak zones |
| `/api/v1/disease/my-risk` | GET | Check farm risk |
| `/api/v1/disease/alerts` | GET | User's alerts |
| `/api/v1/disease/incidents/geojson` | GET | Map data for incidents |
| `/api/v1/disease/outbreaks/geojson` | GET | Map data for outbreaks |

## Database Tables

### disease_incidents
- `incident_id`: INC-XXXXXXXXXXXX
- `disease_name`, `crop_affected`
- `latitude`, `longitude` (GPS)
- `severity_level`: low, medium, high, critical
- `verification_status`: pending, verified, rejected

### outbreak_zones
- `zone_id`: ZONE-XXXXXXXXXXXX
- `center_latitude`, `center_longitude`
- `radius_km`: Default 50km
- `risk_level`: low, medium, high, critical
- `status`: active, resolved, archived

### outbreak_alerts
- `alert_id`: ALERT-XXXXXXXXXXXX
- `user_id`: Farmer receiving alert
- `outbreak_zone_id`: Related outbreak
- `priority`: urgent, high, medium, low
- `distance_km`: From farmer's location
- `pdf_report_id`: AI-generated report

## Configuration

### Celery Beat Schedule
Add to your Celery configuration:

```python
# celeryconfig.py or app initialization
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'detect-disease-outbreaks-hourly': {
        'task': 'tasks.detect_disease_outbreaks',
        'schedule': crontab(minute=0),  # Every hour at :00
    },
}
```

### PostGIS Setup (Optional)
For PostgreSQL users:

```sql
-- Enable PostGIS extension
CREATE EXTENSION postgis;

-- Verify installation
SELECT PostGIS_Version();
```

**Note**: If PostGIS is not available, system automatically falls back to Python Haversine calculations.

## Frontend Integration Examples

### 1. Report Disease with GPS
```javascript
// Get user's current location
navigator.geolocation.getCurrentPosition(position => {
  const data = {
    disease_name: "Late Blight",
    crop_affected: "Tomato",
    latitude: position.coords.latitude,
    longitude: position.coords.longitude,
    severity_level: "high",
    symptoms: "Brown spots on leaves",
    affected_area: 2.5
  };
  
  fetch('/api/v1/disease/incidents', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
});
```

### 2. Real-Time Alerts
```javascript
// SocketIO connection
const socket = io('http://localhost:5000');

socket.on('outbreak_alert', (alert) => {
  showNotification({
    title: alert.title,
    message: alert.message,
    priority: alert.priority,
    pdfUrl: alert.pdf_report_id ? `/files/${alert.pdf_report_id}` : null
  });
  
  // Update map with new outbreak
  if (alert.zone_id) {
    updateOutbreakLayer(alert.zone_id);
  }
});
```

### 3. Interactive Map with Leaflet.js
```javascript
// Initialize map
const map = L.map('outbreak-map').setView([18.5204, 73.8567], 10);

// Add base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Load outbreak zones
fetch('/api/v1/disease/outbreaks/geojson')
  .then(r => r.json())
  .then(geojson => {
    L.geoJSON(geojson, {
      style: (feature) => ({
        color: getRiskColor(feature.properties.risk_level),
        fillOpacity: 0.3,
        weight: 2
      }),
      onEachFeature: (feature, layer) => {
        layer.bindPopup(`
          <strong>${feature.properties.disease_name}</strong><br>
          Crop: ${feature.properties.crop_affected}<br>
          Risk: ${feature.properties.risk_level}<br>
          Incidents: ${feature.properties.incident_count}
        `);
      }
    }).addTo(map);
  });

function getRiskColor(risk) {
  switch(risk) {
    case 'critical': return '#dc2626';
    case 'high': return '#f59e0b';
    case 'medium': return '#eab308';
    default: return '#22c55e';
  }
}
```

## Troubleshooting

### Issue: No outbreaks detected
**Solution**: Make sure you have at least 3 incidents within 50km for the same disease+crop combination.

```bash
# Check incident count
python migrations/init_gews_db.py --stats

# Add sample data
python migrations/init_gews_db.py --sample
```

### Issue: Alerts not sending
**Solution**: Verify Celery worker and beat are running.

```bash
# Check Celery worker
celery -A backend.tasks inspect active

# Check Celery beat schedule
celery -A backend.tasks inspect scheduled
```

### Issue: Slow proximity queries
**Solution**: Enable PostGIS for 10x faster spatial queries.

```sql
-- PostgreSQL only
CREATE EXTENSION postgis;

-- Verify indexes
\d+ disease_incidents
-- Should show GIST index on location column
```

### Issue: PDF generation fails
**Solution**: Set Gemini API key or disable PDF generation.

```bash
# Option 1: Set API key
set GEMINI_API_KEY=your_key_here

# Option 2: Skip PDF generation (alerts still work)
# PDFs will be generated when API key is available
```

## Common Commands

```bash
# View database statistics
python migrations/init_gews_db.py --stats

# Add sample test data
python migrations/init_gews_db.py --sample

# Reset GEWS tables (WARNING: Deletes data)
python migrations/init_gews_db.py --drop

# Trigger outbreak detection manually
curl -X POST http://localhost:5000/api/v1/tasks/trigger/detect_disease_outbreaks

# Check Celery task status
celery -A backend.tasks inspect active
celery -A backend.tasks inspect scheduled
```

## Performance Tips

1. **Enable PostGIS** for PostgreSQL (10x faster proximity queries)
2. **Verify GIST indexes** exist on geometry columns
3. **Limit time windows** in queries (default 30 days)
4. **Cache GeoJSON** responses with ETags
5. **Monitor Celery** task execution time

## Security Notes

- All endpoints require JWT authentication
- Coordinate validation (-90 to 90, -180 to 180)
- Input sanitization on user content
- SQL injection protection via SQLAlchemy ORM
- Rate limiting recommended (TODO)

## Next Steps

1. ✅ Backend implementation complete
2. ⏳ **Frontend integration** (disease reporting form, alert UI, interactive map)
3. ⏳ **Automated tests** (pytest suite)
4. ⏳ **Load testing** (simulate 1000+ incidents)
5. ⏳ **Security audit** (penetration testing)
6. ⏳ **SMS fallback** (for farmers without smartphones)
7. ⏳ **ML prediction** (forecast outbreak spread)

## Support

- **Documentation**: [docs/GEWS_FEATURE.md](GEWS_FEATURE.md)
- **PR Summary**: [docs/PR_SUMMARY_GEWS.md](PR_SUMMARY_GEWS.md)
- **GitHub Issue**: #1192
- **Feature Branch**: `feature/disease-outbreak-gews-1192`

---

**Status**: ✅ Backend implementation complete and pushed  
**Last Updated**: 2024  
**Estimated Learning Time**: 30 minutes
