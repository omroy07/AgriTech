"""
Hyperlocal Precision Irrigation & Climate Early Warning API Endpoints.
Location: backend/api/v1/climate_control.py
"""

from datetime import datetime, timedelta
import json
from flask import Blueprint, request, jsonify
from backend.services.climate_service import ClimateService
from backend.services.precision_irrigation_engine import (
    PrecisionIrrigationEngine, CROP_KC_PROFILES, SOIL_TEXTURE_PROFILES
)
from backend.models.climate import SensorNode, ClimateZone, AutomationTrigger, TelemetryLog
from backend.extensions import db
from auth_utils import token_required

climate_bp = Blueprint('climate_control', __name__)

# Mock Default Farm Field Polygons with IoT / Satellite telemetry
DEFAULT_FIELD_POLYGONS = [
    {
        "id": 101,
        "name": "North Block - Tomato Greenhouse",
        "crop": "Tomato",
        "growth_stage": "mid_season",
        "soil_texture": "Clay Loam",
        "irrigation_method": "Drip Irrigation",
        "area_acres": 4.5,
        "coordinates": [
            [19.9982, 73.7885],
            [20.0015, 73.7892],
            [20.0008, 73.7935],
            [19.9975, 73.7925]
        ],
        "sensors": {
            "root_moisture_0_30cm": 22.4,
            "root_moisture_30_60cm": 25.8,
            "canopy_temp_c": 27.5,
            "relative_humidity_pct": 82.0,
            "solar_radiation_mj": 21.4,
            "wind_speed_ms": 2.1
        },
        "valve_status": "CLOSED"
    },
    {
        "id": 102,
        "name": "East Block - Durum Wheat Field",
        "crop": "Wheat",
        "growth_stage": "development",
        "soil_texture": "Black Cotton (Vertisol)",
        "irrigation_method": "Sprinkler",
        "area_acres": 12.0,
        "coordinates": [
            [19.9965, 73.7940],
            [19.9995, 73.7955],
            [19.9980, 73.8010],
            [19.9950, 73.7990]
        ],
        "sensors": {
            "root_moisture_0_30cm": 17.5,
            "root_moisture_30_60cm": 21.0,
            "canopy_temp_c": 29.0,
            "relative_humidity_pct": 54.0,
            "solar_radiation_mj": 23.8,
            "wind_speed_ms": 3.4
        },
        "valve_status": "SCHEDULED"
    },
    {
        "id": 103,
        "name": "South Sector - Citrus & Pomegranate Orchard",
        "crop": "Citrus",
        "growth_stage": "mid_season",
        "soil_texture": "Loam",
        "irrigation_method": "Micro-Drip",
        "area_acres": 8.0,
        "coordinates": [
            [19.9920, 73.7890],
            [19.9955, 73.7905],
            [19.9940, 73.7960],
            [19.9905, 73.7945]
        ],
        "sensors": {
            "root_moisture_0_30cm": 26.2,
            "root_moisture_30_60cm": 28.4,
            "canopy_temp_c": 25.0,
            "relative_humidity_pct": 68.0,
            "solar_radiation_mj": 19.5,
            "wind_speed_ms": 1.8
        },
        "valve_status": "STANDBY"
    }
]


# ------------------------------------------------------------------------------
# 1. FIELD POLYGON MAPPER & TELEMETRY
# ------------------------------------------------------------------------------
@climate_bp.route('/field-polygons/<int:farm_id>', methods=['GET'])
def get_field_polygons(farm_id):
    """
    Returns spatial GeoJSON/Polygon arrays for interactive field mapper on climate_dashboard.html.
    """
    enhanced_polygons = []
    for poly in DEFAULT_FIELD_POLYGONS:
        s = poly["sensors"]
        et0 = PrecisionIrrigationEngine.calculate_fao56_et0(
            temp_mean_c=s["canopy_temp_c"],
            temp_min_c=s["canopy_temp_c"] - 5.0,
            temp_max_c=s["canopy_temp_c"] + 5.0,
            humidity_pct=s["relative_humidity_pct"],
            wind_speed_2m_ms=s["wind_speed_ms"],
            solar_radiation_mj_m2=s["solar_radiation_mj"]
        )
        water_bal = PrecisionIrrigationEngine.calculate_water_balance(
            crop_name=poly["crop"],
            growth_stage=poly["growth_stage"],
            soil_texture=poly["soil_texture"],
            root_moisture_0_30_pct=s["root_moisture_0_30cm"],
            root_moisture_30_60_pct=s["root_moisture_30_60cm"],
            et0_mm_day=et0,
            irrigation_method=poly["irrigation_method"]
        )
        poly_copy = dict(poly)
        poly_copy["et0_mm"] = et0
        poly_copy["water_balance"] = water_bal
        enhanced_polygons.append(poly_copy)

    return jsonify({
        "status": "success",
        "farm_id": farm_id,
        "polygons": enhanced_polygons
    }), 200


# ------------------------------------------------------------------------------
# 2. AGRONOMIC WATER BALANCE & 3-DAY IRRIGATION SCHEDULER
# ------------------------------------------------------------------------------
@climate_bp.route('/irrigation/calculate', methods=['POST'])
def calculate_irrigation_schedule():
    """
    Calculates FAO-56 Penman-Monteith ET0, crop ETc, soil water balance,
    and 3-day optimal irrigation windows based on microclimate telemetry.
    """
    data = request.get_json(silent=True) or {}
    crop = data.get('crop', 'Tomato')
    stage = data.get('growth_stage', 'mid_season')
    soil = data.get('soil_texture', 'Clay Loam')
    method = data.get('irrigation_method', 'Drip Irrigation')
    root_0_30 = float(data.get('root_moisture_0_30cm', 22.0))
    root_30_60 = float(data.get('root_moisture_30_60cm', 24.5))

    temp_mean = float(data.get('temperature_c', 26.5))
    temp_min = float(data.get('temp_min_c', temp_mean - 6.0))
    temp_max = float(data.get('temp_max_c', temp_mean + 6.0))
    humidity = float(data.get('humidity_pct', 62.0))
    wind_speed = float(data.get('wind_speed_ms', 2.3))
    solar_rad = data.get('solar_radiation_mj')

    # 1. Calculate ET0
    et0 = PrecisionIrrigationEngine.calculate_fao56_et0(
        temp_mean_c=temp_mean,
        temp_min_c=temp_min,
        temp_max_c=temp_max,
        humidity_pct=humidity,
        wind_speed_2m_ms=wind_speed,
        solar_radiation_mj_m2=float(solar_rad) if solar_rad else None
    )

    # 2. Calculate Water Balance
    balance = PrecisionIrrigationEngine.calculate_water_balance(
        crop_name=crop,
        growth_stage=stage,
        soil_texture=soil,
        root_moisture_0_30_pct=root_0_30,
        root_moisture_30_60_pct=root_30_60,
        et0_mm_day=et0,
        rainfall_forecast_mm=float(data.get('rainfall_forecast_mm', 0.0)),
        irrigation_method=method
    )

    # 3. 3-Day Forecast Simulation
    weather_3d = data.get('weather_3day_forecast') or [
        {"temp": temp_mean, "temp_min": temp_min, "temp_max": temp_max, "humidity": humidity, "wind_speed": wind_speed, "rainfall": 0.0},
        {"temp": temp_mean + 1.2, "temp_min": temp_min + 1.0, "temp_max": temp_max + 1.5, "humidity": humidity - 4.0, "wind_speed": wind_speed + 0.3, "rainfall": 0.0},
        {"temp": temp_mean - 0.5, "temp_min": temp_min - 0.8, "temp_max": temp_max - 0.5, "humidity": humidity + 8.0, "wind_speed": wind_speed - 0.4, "rainfall": 2.5}
    ]

    schedule_3day = PrecisionIrrigationEngine.generate_3day_irrigation_schedule(
        crop_name=crop,
        growth_stage=stage,
        soil_texture=soil,
        root_moisture_pct=balance["soil_hydraulics"]["current_moisture_pct"],
        weather_3day_forecast=weather_3d,
        irrigation_method=method
    )

    return jsonify({
        "status": "success",
        "fao56_et0_mm_day": et0,
        "water_balance": balance,
        "schedule_3day": schedule_3day,
        "recommended_action": schedule_3day[0]["action_summary"]
    }), 200


# ------------------------------------------------------------------------------
# 3. CLIMATE RISK EARLY WARNING EVALUATOR
# ------------------------------------------------------------------------------
@climate_bp.route('/early-warnings/evaluate', methods=['POST', 'GET'])
def evaluate_early_warnings():
    """
    Evaluates microclimate thresholds for Frost, Blight/Fungal, Heat Stress, and Waterlogging.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
    else:
        data = request.args.to_dict()

    temp = float(data.get('temperature_c', 2.8))  # Demo default evaluates frost/fungal
    humidity = float(data.get('humidity_pct', 89.0))
    min_temp = float(data.get('forecast_min_temp_c', 2.2))
    rain_24h = float(data.get('rainfall_24h_mm', 0.0))
    hum_hist = [float(h) for h in data.get('humidity_history_48h', [86, 88, 91, 89, 87, 85, 90, 89])]

    risks = PrecisionIrrigationEngine.evaluate_microclimate_risks(
        temperature_c=temp,
        humidity_pct=humidity,
        forecast_min_temp_c=min_temp,
        humidity_history_48h=hum_hist,
        rainfall_24h_mm=rain_24h,
        crop_name=data.get('crop', 'Tomato')
    )

    return jsonify({
        "status": "success",
        "evaluated_at": datetime.utcnow().isoformat(),
        "risk_count": len(risks),
        "alerts": risks
    }), 200


# ------------------------------------------------------------------------------
# 4. SATELLITE SOIL MOISTURE INGESTION (COPERNICUS / SENTINEL-2)
# ------------------------------------------------------------------------------
@climate_bp.route('/satellite-soil-sync', methods=['POST', 'GET'])
def sync_satellite_soil():
    """
    Ingests or simulates Copernicus Sentinel-2 / NASA SMAP soil moisture layers.
    """
    return jsonify({
        "status": "success",
        "satellite_constellation": "Copernicus Sentinel-2 MSI & SMAP L4",
        "spatial_resolution": "10m Multispectral",
        "last_overpass": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
        "mean_surface_moisture_pct": 23.6,
        "confidence_index": "High (Cloud Cover < 5%)"
    }), 200


# ------------------------------------------------------------------------------
# 5. CORE CLIMATE SERVICES & TELEMETRY
# ------------------------------------------------------------------------------
@climate_bp.route('/telemetry/<string:node_uid>', methods=['POST'])
def post_telemetry(node_uid):
    data = request.get_json()
    log, error = ClimateService.process_telemetry(node_uid, data)
    if error:
        return jsonify({'status': 'error', 'message': error}), 404
    return jsonify({'status': 'success', 'timestamp': log.timestamp.isoformat()}), 201


@climate_bp.route('/zones/<int:farm_id>', methods=['GET'])
def get_farm_zones(farm_id):
    zones = ClimateZone.query.filter_by(farm_id=farm_id).all()
    if not zones:
        # Fallback to simulated zones
        return jsonify({
            'status': 'success',
            'data': [
                {"id": 1, "name": "Zone A (Greenhouse Tomato)", "farm_id": farm_id, "node_count": 3},
                {"id": 2, "name": "Zone B (Open Wheat Field)", "farm_id": farm_id, "node_count": 2},
                {"id": 3, "name": "Zone C (Citrus Orchard)", "farm_id": farm_id, "node_count": 4}
            ]
        }), 200
    return jsonify({'status': 'success', 'data': [z.to_dict() for z in zones]}), 200


@climate_bp.route('/analytics/<int:zone_id>', methods=['GET'])
def get_analytics(zone_id):
    analytics = ClimateService.get_zone_analytics(zone_id)
    if not analytics:
        # Fallback rich telemetry payload
        analytics = {
            "latest": {"temp": 26.4, "humidity": 64.0, "co2": 420},
            "vpd": 1.18,
            "vpd_status": "VEGETATIVE",
            "history": [
                {"timestamp": (datetime.utcnow() - timedelta(minutes=i*15)).isoformat(), "temp": 24 + (i%5)*0.8, "humidity": 60 + (i%4)*2.0}
                for i in range(12)
            ]
        }
    return jsonify({'status': 'success', 'data': analytics}), 200
