"""
Predictive Mandi Price Intelligence & Net-Profit Optimizer API Endpoints.
Location: backend/api/v1/market.py
"""

from datetime import datetime
from flask import Blueprint, request, jsonify
from backend.services.market_service import MarketIntelligenceService
from backend.services.mandi_profit_optimizer import MandiProfitOptimizer, VEHICLE_PROFILES
from backend.ml_models.price_forecast import PriceForecastEngine, COMMODITY_BASELINES, MANDI_REGISTRY
from backend.models.market import PriceWatchlist, MarketPrice
from backend.extensions import db
from backend.services.audit_service import AuditService

market_bp = Blueprint('market', __name__)


# ------------------------------------------------------------------------------
# 1. COMMODITY & MANDI METADATA
# ------------------------------------------------------------------------------
@market_bp.route('/market/commodities', methods=['GET'])
def get_commodities():
    """Returns list of supported agricultural commodities and baseline statistics."""
    return jsonify({
        "status": "success",
        "commodities": PriceForecastEngine.get_supported_commodities(),
        "baselines": COMMODITY_BASELINES,
        "mandis": MANDI_REGISTRY,
        "vehicle_profiles": VEHICLE_PROFILES
    })


@market_bp.route('/market/prices', methods=['GET'])
def get_prices():
    """Query current mandi prices filtered by district or crop."""
    district = request.args.get('district')
    crop = request.args.get('crop')
    prices = MarketIntelligenceService.get_market_prices(district, crop)
    return jsonify({
        "status": "success",
        "data": [p.to_dict() for p in prices]
    })


# ------------------------------------------------------------------------------
# 2. 7- TO 14-DAY TIME-SERIES PRICE FORECASTING
# ------------------------------------------------------------------------------
@market_bp.route('/market/forecast', methods=['POST', 'GET'])
def forecast_prices():
    """
    Predict 7- to 14-day price trends with 95% confidence intervals (yhat, yhat_lower, yhat_upper),
    seasonality cycles, and optimal harvest/selling day recommendations.
    """
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        crop = data.get('crop') or data.get('commodity', 'Tomato')
        mandi = data.get('mandi') or data.get('mandi_name', 'Lasalgaon Mandi')
        horizon = int(data.get('horizon_days', 14))
    else:
        crop = request.args.get('crop', 'Tomato')
        mandi = request.args.get('mandi', 'Lasalgaon Mandi')
        horizon = int(request.args.get('horizon_days', 14))

    forecast_res = PriceForecastEngine.forecast_prices(
        commodity=crop,
        mandi_name=mandi,
        horizon_days=min(30, max(3, horizon))
    )

    return jsonify(forecast_res)


# ------------------------------------------------------------------------------
# 3. LOGISTICS & NET-PROFIT CALCULATOR
# ------------------------------------------------------------------------------
@market_bp.route('/market/optimize-profit', methods=['POST'])
def optimize_net_profit():
    """
    Given farmer location, crop volume, and vehicle type, calculates road distances,
    deducts transport fuel/freight, loading labor, toll, and APMC cess to rank mandis by net profit.
    """
    data = request.get_json(silent=True) or {}
    crop = data.get('crop') or data.get('crop_name', 'Tomato')
    volume = float(data.get('volume_quintals') or data.get('volume', 50.0))
    lat = float(data.get('lat') or data.get('latitude', 19.9975))
    lng = float(data.get('lng') or data.get('longitude', 73.7898))
    vehicle = data.get('vehicle_type', 'tractor_trolley')
    harvest_date = data.get('harvest_date')

    optimization_res = MandiProfitOptimizer.optimize_mandi_sales(
        crop_name=crop,
        volume_quintals=volume,
        farmer_lat=lat,
        farmer_lng=lng,
        vehicle_type=vehicle,
        harvest_date=harvest_date
    )

    return jsonify(optimization_res)


# ------------------------------------------------------------------------------
# 4. LEAFLET.JS GEOJSON PRICE HEATMAP
# ------------------------------------------------------------------------------
@market_bp.route('/market/heatmap', methods=['GET'])
def get_price_heatmap():
    """
    Returns GeoJSON FeatureCollection with price heat intensity for Leaflet.js rendering.
    """
    crop = request.args.get('crop', 'Tomato')
    lat = float(request.args.get('lat', 19.9975))
    lng = float(request.args.get('lng', 73.7898))

    geojson = MandiProfitOptimizer.generate_mandi_heatmap_geojson(
        crop_name=crop,
        farmer_lat=lat,
        farmer_lng=lng
    )
    return jsonify(geojson)


# ------------------------------------------------------------------------------
# 5. TARGET PRICE ALERTS & WATCHLIST
# ------------------------------------------------------------------------------
@market_bp.route('/market/watchlist', methods=['POST'])
@market_bp.route('/market/alerts/subscribe', methods=['POST'])
def add_to_watchlist():
    """
    Subscribe to automated SMS or Web Push alerts when a target price threshold is reached.
    """
    data = request.get_json(silent=True) or {}
    user_id = data.get('user_id', 'anonymous_farmer')
    crop = data.get('crop') or data.get('crop_name')
    target_price = float(data.get('target_price', 0))
    mandi = data.get('mandi_name')
    phone = data.get('phone_number') or data.get('phone')
    channel = data.get('alert_channel', 'SMS')

    if not crop or target_price <= 0:
        return jsonify({"status": "error", "message": "Crop and positive target_price are required"}), 400

    watchlist_item = PriceWatchlist(
        user_id=str(user_id),
        crop_name=crop,
        target_price=target_price,
        mandi_name=mandi,
        phone_number=phone,
        alert_channel=channel,
        alert_enabled=True
    )
    db.session.add(watchlist_item)
    db.session.commit()

    AuditService.log_action(
        action="MARKET_ALERT_SUBSCRIBE",
        user_id=str(user_id),
        resource_type="PRICE_WATCHLIST",
        resource_id=str(watchlist_item.id),
        meta_data={"crop": crop, "target": target_price, "channel": channel}
    )

    return jsonify({
        "status": "success",
        "message": f"Alert registered for {crop} at target ₹{target_price}/Q. You will receive {channel} notification upon trigger.",
        "alert": watchlist_item.to_dict()
    })


@market_bp.route('/market/alerts/check', methods=['POST', 'GET'])
def check_price_alerts():
    """Evaluate active price watchlists and trigger simulated or real notifications."""
    watchlists = PriceWatchlist.query.filter_by(alert_enabled=True).all()
    triggered = []

    for item in watchlists:
        base_cfg = COMMODITY_BASELINES.get(item.crop_name, COMMODITY_BASELINES["Tomato"])
        current_mkt_price = base_cfg["base_price"]

        if current_mkt_price >= item.target_price and not item.is_triggered:
            item.is_triggered = True
            item.triggered_at = datetime.utcnow()
            triggered.append({
                "user_id": item.user_id,
                "crop": item.crop_name,
                "target_price": item.target_price,
                "current_price": current_mkt_price,
                "channel": item.alert_channel,
                "phone": item.phone_number,
                "message": f"🚨 Mandi Alert: {item.crop_name} crossed your target of ₹{item.target_price}/Q! Current price: ₹{current_mkt_price}/Q."
            })

    db.session.commit()
    return jsonify({
        "status": "success",
        "checked_count": len(watchlists),
        "triggered_count": len(triggered),
        "triggered_alerts": triggered
    })


@market_bp.route('/market/analyze', methods=['GET'])
def analyze_market():
    crop = request.args.get('crop')
    district = request.args.get('district')
    if not crop or not district:
        return jsonify({"status": "error", "message": "Crop and District are required"}), 400

    analysis = MarketIntelligenceService.analyze_price_trends(crop, district)
    return jsonify({
        "status": "success" if "error" not in analysis else "error",
        "data": analysis
    })


@market_bp.route('/market/refresh', methods=['POST'])
def force_refresh_prices():
    updated = MarketIntelligenceService.fetch_live_prices()
    return jsonify({
        "status": "success",
        "updated_count": len(updated)
    })
