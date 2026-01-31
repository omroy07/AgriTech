# Pest & Disease Geospatial Early Warning System (GEWS) 🌾🗺️

**Issue**: #1192  
**Feature Branch**: `feature/disease-outbreak-gews-1192`

## Overview

The Geospatial Early Warning System (GEWS) is an advanced disease outbreak detection and alert system that uses spatial clustering algorithms to identify disease hotspots and proactively warn farmers at risk.

## Key Features

### 1. Geo-Tagged Disease Reporting 📍
- Farmers can report disease incidents with GPS coordinates
- Captures disease name, crop affected, severity, symptoms, and affected area
- Automatic verification workflow for reported incidents

### 2. Spatial Outbreak Detection 🔍
- **Automated hourly analysis** using DBSCAN-like clustering
- Groups incidents within 50km radius
- Minimum 3 incidents required to declare outbreak
- AI-powered risk assessment (low, medium, high, critical)

### 3. Real-Time Emergency Alerts ⚠️
- **SocketIO push notifications** for immediate farmer alerts
- Three alert levels:
  - **Urgent**: Within outbreak zone (<50km)
  - **High**: Proximity warning (<60km)
  - **Medium**: Preventive action advised (<75km)
- Multi-language support (English, Hindi, Marathi)

### 4. AI-Generated Action Reports 📄
- Gemini AI generates preventative measures PDFs
- Includes:
  - Immediate actions (24-48 hours)
  - Preventative measures
  - Treatment recommendations
  - Monitoring guidelines
  - Community coordination steps

### 5. Interactive Mapping 🗺️
- GeoJSON endpoints for disease incidents and outbreak zones
- Visualize outbreaks on interactive maps
- Color-coded risk levels
- Distance calculations from user's farm

## Architecture

### Database Models

#### `DiseaseIncident`
```python
- incident_id: Unique identifier (INC-XXXX)
- disease_name: Name of disease
- crop_affected: Affected crop type
- latitude, longitude: GPS coordinates
- severity_level: low, medium, high, critical
- affected_area: Hectares affected
- verification_status: pending, verified, rejected
```

#### `OutbreakZone`
```python
- zone_id: Unique identifier (ZONE-XXXX)
- center_latitude, center_longitude: Cluster center
- radius_km: Outbreak radius
- incident_count: Number of incidents
- risk_level: low, medium, high, critical
- status: active, resolved, archived
```

#### `OutbreakAlert`
```python
- alert_id: Unique identifier (ALERT-XXXX)
- user_id: Farmer receiving alert
- outbreak_zone_id: Related outbreak
- alert_type: outbreak_detected, proximity_warning, preventive_action
- priority: urgent, high, medium, low
- distance_km: Distance from farm
- pdf_report_id: Link to preventative PDF
```

### Geospatial Service

#### Core Algorithms

**Distance Calculation**: Haversine formula
```python
d = 2 * R * arcsin(sqrt(sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2)))
```

**Clustering**: DBSCAN-like spatial clustering
- Groups incidents by disease + crop
- 50km epsilon (radius)
- Min 3 points per cluster
- Calculates centroid, average severity, total area

**Risk Assessment**:
- `critical`: >10 incidents OR avg severity > 2.5
- `high`: 6-10 incidents OR avg severity > 2.0
- `medium`: 3-5 incidents OR avg severity > 1.5
- `low`: <3 incidents

### Celery Tasks

#### `detect_disease_outbreaks_task` (Hourly)
```python
# Runs every hour via Celery Beat
1. Analyze last 30 days of incidents
2. Detect spatial clusters (50km, min 3 incidents)
3. Create/update OutbreakZone records
4. Trigger emergency alerts for new outbreaks
```

#### `send_outbreak_emergency_alerts_task`
```python
# Triggered for each new outbreak zone
1. Find farmers within 75km (1.5x radius)
2. Calculate distances
3. Determine alert priority
4. Send SocketIO real-time notifications
5. Create OutbreakAlert records
6. Trigger PDF report generation
```

#### `generate_outbreak_pdf_report_task`
```python
# AI-powered preventative action report
1. Query Gemini AI for recommendations
2. Generate professional PDF report
3. Include disease info, actions, treatments
4. Link PDF to alert record
```

## API Endpoints

### Disease Reporting

#### `POST /api/v1/disease/incidents`
Report a geo-tagged disease incident.

**Request**:
```json
{
  "disease_name": "Late Blight",
  "crop_affected": "Tomato",
  "severity_level": "high",
  "symptoms": "Brown spots on leaves...",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "affected_area": 2.5
}
```

**Response**:
```json
{
  "success": true,
  "incident_id": "INC-A1B2C3D4E5F6",
  "incident": { /* full incident data */ }
}
```

#### `GET /api/v1/disease/incidents`
Query disease incidents with filters.

**Query Params**:
- `disease_name`: Filter by disease
- `crop`: Filter by crop type
- `severity`: Filter by severity level
- `lat`, `lon`, `radius_km`: Proximity search
- `days`: Time window (default: 30)

#### `GET /api/v1/disease/incidents/geojson`
Get incidents as GeoJSON for mapping.

### Outbreak Monitoring

#### `GET /api/v1/disease/outbreaks`
List active outbreak zones.

**Query Params**:
- `disease_name`, `crop`, `risk_level`: Filters
- `lat`, `lon`: Calculate distances from location

#### `GET /api/v1/disease/outbreaks/<zone_id>`
Get detailed outbreak zone information with all incidents.

#### `GET /api/v1/disease/outbreaks/geojson`
Get outbreak zones as GeoJSON polygons.

### Risk Assessment

#### `GET /api/v1/disease/my-risk`
Check if logged-in user's farm is at risk.

**Response**:
```json
{
  "is_at_risk": true,
  "farm_location": {
    "latitude": 18.5204,
    "longitude": 73.8567,
    "address": "Pune District"
  },
  "nearby_outbreaks": [
    {
      "zone_id": "ZONE-ABC123",
      "disease_name": "Late Blight",
      "crop_affected": "Tomato",
      "risk_level": "high",
      "distance_km": 12.3
    }
  ],
  "recent_alerts": [ /* alert history */ ]
}
```

### Alert Management

#### `GET /api/v1/disease/alerts`
Get user's outbreak alerts.

**Query Params**: `status`, `priority`

#### `POST /api/v1/disease/alerts/<alert_id>/acknowledge`
Mark an alert as acknowledged.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install geoalchemy2 shapely
```

### 2. Database Migration

```bash
# Create GEWS tables
python migrations/init_gews_db.py

# Add sample data for testing
python migrations/init_gews_db.py --sample

# View statistics
python migrations/init_gews_db.py --stats
```

### 3. Configure PostGIS (Optional, PostgreSQL only)

```sql
-- Enable PostGIS extension
CREATE EXTENSION postgis;

-- Verify installation
SELECT PostGIS_Version();
```

**Note**: System falls back to Python Haversine calculations if PostGIS unavailable.

### 4. Configure Celery Beat Schedule

Add to `celeryconfig.py` or Celery initialization:

```python
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'detect-disease-outbreaks': {
        'task': 'tasks.detect_disease_outbreaks',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

### 5. Environment Variables

```bash
# Required for AI-powered PDF reports
export GEMINI_API_KEY=your_gemini_api_key_here

# Database URL (if using PostgreSQL with PostGIS)
export DATABASE_URL=postgresql://user:pass@localhost/agritech
```

### 6. Start Services

```bash
# Start Flask app
python app.py

# Start Celery worker
celery -A backend.tasks worker --loglevel=info

# Start Celery beat scheduler
celery -A backend.tasks beat --loglevel=info
```

## Usage Examples

### 1. Report Disease Incident

```javascript
// From mobile app or web
const incident = await reportDisease({
  disease_name: "Bacterial Blight",
  crop_affected: "Rice",
  severity_level: "medium",
  latitude: 18.5204,
  longitude: 73.8567,
  affected_area: 3.2,
  symptoms: "Water-soaked lesions on leaves"
});
```

### 2. Check Farm Risk Status

```javascript
// When farmer logs in
const riskStatus = await checkMyRisk();

if (riskStatus.is_at_risk) {
  showWarningModal(riskStatus.nearby_outbreaks);
}
```

### 3. Real-Time Alert Handling

```javascript
// SocketIO client
socket.on('outbreak_alert', (alert) => {
  showNotification({
    title: alert.title,
    message: alert.message,
    priority: alert.priority,
    pdfUrl: `/files/${alert.pdf_report_id}`
  });
});
```

### 4. Visualize Outbreaks on Map

```javascript
// Fetch GeoJSON data
const incidents = await fetch('/api/v1/disease/incidents/geojson').then(r => r.json());
const zones = await fetch('/api/v1/disease/outbreaks/geojson').then(r => r.json());

// Render with Leaflet/Mapbox
map.addSource('incidents', { type: 'geojson', data: incidents });
map.addSource('zones', { type: 'geojson', data: zones });
```

## Testing

### Manual Testing

```bash
# 1. Create test incidents
curl -X POST http://localhost:5000/api/v1/disease/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "disease_name": "Late Blight",
    "crop_affected": "Tomato",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "severity_level": "high",
    "affected_area": 2.5
  }'

# 2. Trigger outbreak detection manually
curl -X POST http://localhost:5000/api/v1/tasks/trigger/detect_disease_outbreaks

# 3. Check outbreak zones
curl http://localhost:5000/api/v1/disease/outbreaks \
  -H "Authorization: Bearer $TOKEN"

# 4. Check personal risk
curl http://localhost:5000/api/v1/disease/my-risk \
  -H "Authorization: Bearer $TOKEN"
```

### Automated Tests

```python
# tests/test_geospatial_service.py
def test_distance_calculation():
    d = GeospatialService.calculate_distance(18.5204, 73.8567, 18.5304, 73.8667)
    assert 1.0 < d < 2.0  # ~1.5 km

def test_outbreak_clustering():
    clusters = GeospatialService.detect_outbreak_clusters(radius_km=50, min_incidents=3)
    assert len(clusters) >= 0
```

## Performance Considerations

### Database Indexes
- **GIST spatial indexes** on all geometry columns
- B-tree indexes on `disease_name`, `crop_affected`, `status`
- Composite index on `(disease_name, crop_affected, status)`

### Query Optimization
- Use PostGIS `ST_DWithin` for proximity queries (10x faster than Haversine)
- Limit time windows (default 30 days) to reduce scan size
- Paginate large result sets

### Scalability
- Celery tasks run asynchronously (non-blocking)
- SocketIO scales horizontally with Redis pub/sub
- PDF generation offloaded to background workers
- GeoJSON endpoints support caching with ETags

## Monitoring & Alerts

### Metrics to Track
- Number of incidents reported per day
- Active outbreak zones
- Alert delivery success rate
- PDF generation time
- Celery task execution time

### Logging
```python
logger.info(f"Outbreak detected: {zone_id} - {disease} in {crop}")
logger.warning(f"Failed to send alert to user {user_id}")
logger.error(f"PDF generation failed: {error}")
```

## Security Considerations

- **JWT authentication** required for all endpoints
- **Rate limiting** on incident reporting (max 10/hour per user)
- **Input validation** for coordinates, disease names, severity
- **SQL injection protection** via SQLAlchemy ORM
- **XSS protection** on user-generated content (symptoms field)

## Future Enhancements

1. **Machine Learning**: Predict outbreak spread patterns
2. **Image Recognition**: Auto-detect disease from crop photos
3. **Weather Integration**: Correlate outbreaks with weather data
4. **Community Validation**: Crowd-source incident verification
5. **SMS Alerts**: Fallback for farmers without smartphones
6. **Predictive Analytics**: Forecast risk based on historical patterns
7. **Drone Integration**: Aerial surveillance for large farms

## Troubleshooting

### Issue: No alerts sent
- Check Celery worker is running
- Verify users have farm locations set
- Check SocketIO connection status
- Review Celery logs for task failures

### Issue: Slow proximity queries
- Enable PostGIS extension
- Verify GIST indexes exist: `\d+ disease_incidents`
- Reduce search radius or time window

### Issue: PDF generation fails
- Verify `GEMINI_API_KEY` is set
- Check ReportLab installation
- Review disk space for temp files

### Issue: Incorrect distances
- Verify coordinate order (latitude, longitude)
- Check coordinate range (-90 to 90, -180 to 180)
- Ensure coordinates are in decimal degrees (not DMS)

## References

- [PostGIS Documentation](https://postgis.net/docs/)
- [GeoAlchemy2 Guide](https://geoalchemy-2.readthedocs.io/)
- [DBSCAN Clustering Algorithm](https://en.wikipedia.org/wiki/DBSCAN)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Gemini API Documentation](https://ai.google.dev/docs)

## License

Part of AgriTech platform - See main LICENSE file.

## Contributors

- AI-Powered Development Team
- Agricultural Domain Experts
- GIS Specialists

---

**Status**: ✅ Implementation Complete  
**Last Updated**: 2024  
**Tested**: ⚠️ Pending QA
