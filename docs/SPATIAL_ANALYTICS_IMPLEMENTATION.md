# Spatial Analytics Implementation Plan

## Overview
This document outlines the implementation of the "Smart Field Analytics" module for the AgriTech platform. This module enables farmers to map their fields, view satellite imagery overlays (NDVI), and receive location-based insights.

## Architecture
- **Backend Framework**: Flask (Integrated with existing `app.py`).
- **Database**: PostgreSQL (Production) / SQLite (Dev) using SQLAlchemy.
- **Spatial Data Storage**: GeoJSON strings (compatible with SQLite) or PostGIS Geometry (if available).
- **Frontend**: Leaflet.js for maps (served via Flask templates), Chart.js for analytics.
- **Image Processing**: Python (Rasterio/NumPy) for NDVI calculation.

## Folder Structure
```
AgriTech/
├── spatial_analytics/          # New Module
│   ├── __init__.py             # Blueprint definition
│   ├── models.py               # FieldBoundary, AnalysisResult models
│   ├── routes.py               # API Endpoints
│   ├── utils.py                # NDVI logic (Sentinel/Landsat)
├── js/
│   └── spatial.js              # Frontend Map Logic
├── css/
│   └── spatial.css             # Dashboard Styling
├── spatial.html                # Main Dashboard Page (served by Flask)
├── docs/
│   └── SPATIAL_ANALYTICS_IMPLEMENTATION.md
└── app.py                      # Modified to register blueprint
```

## Step-by-Step Implementation

### Phase 1: dependencies
1. Add `rasterio`, `geopandas`, `shapely` to `requirements.txt`.
2. Ensure `numpy` and `opencv-python` are available.

### Phase 2: Backend Core (spatial_analytics)
1. **Models**: Create `Field` model to store user-drawn boundaries (GeoJSON).
2. **Routes**:
   - `POST /api/spatial/field`: Save field boundary.
   - `GET /api/spatial/field`: List user fields.
   - `POST /api/spatial/analyze`: Trigger NDVI analysis for a field.
3. **NDVI Processing**:
   - Implement `calculate_ndvi(red_band, nir_band)` using NumPy.
   - Implement logic to clip raster to field boundary.
   - Generate colored overlay image (PNG).

### Phase 3: Frontend Dashboard (Leaflet)
1. **Map Interface**:
   - Initialize Leaflet map.
   - Add drawing tools (`leaflet-draw`) for field creation.
   - Add toggle for "Satellite" vs "Street" view.
2. **Interaction**:
   - Fetch existing fields on load.
   - Handle "Save Field" event.
   - specific specific field to view details.
3. **Analytics Panel**:
   - Show calculated NDVI stats (Min, Max, Avg).
   - Display Heatmaps (Soil/Disease).

### Phase 4: Integration
1. Register `spatial_bp` in `app.py`.
2. Add navigation link to "Spatial Dashboard" in `navbar.html`.

## Key Components

### NDVI Formula
```python
ndvi = (nir - red) / (nir + red)
# normalize to -1 to 1
```

### Map Component
Uses Leaflet L.map, L.geoJSON for boundaries, and L.imageOverlay for NDVI results.
