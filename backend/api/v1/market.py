from flask import Blueprint, request, jsonify
from backend.services.market_service import MarketIntelligenceService
from backend.models import PriceWatchlist
from backend.extensions import db
from backend.services.audit_service import AuditService

market_bp = Blueprint('market', __name__)

@market_bp.route('/market/prices', methods=['GET'])
def get_prices():
    district = request.args.get('district')
    crop = request.args.get('crop')
    prices = MarketIntelligenceService.get_market_prices(district, crop)
    return jsonify({
        "status": "success",
        "data": [p.to_dict() for p in prices]
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

@market_bp.route('/market/watchlist', methods=['POST'])
def add_to_watchlist():
    data = request.get_json()
    user_id = data.get('user_id')
    crop = data.get('crop')
    target_price = data.get('target_price')
    
    if not all([user_id, crop, target_price]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    watchlist_item = PriceWatchlist(
        user_id=user_id,
        crop_name=crop,
        target_price=target_price
    )
    db.session.add(watchlist_item)
    db.session.commit()
    
    AuditService.log_action(
        action="MARKET_WATCHLIST_ADD",
        user_id=user_id,
        resource_type="MARKET_WATCHLIST",
        resource_id=str(watchlist_item.id),
        meta_data={"crop": crop, "target": target_price}
    )
    
    return jsonify({
        "status": "success",
        "message": f"Added {crop} to your watchlist."
    })

@market_bp.route('/market/refresh', methods=['POST'])
def force_refresh_prices():
    """Manual trigger for price updates (Admin/Internal use)"""
    updated = MarketIntelligenceService.fetch_live_prices()
    
    AuditService.log_action(
        action="MARKET_PRICE_REFRESH_MANUAL",
        risk_level="MEDIUM",
        meta_data={"updated_count": len(updated)}
    )
    
    return jsonify({
        "status": "success",
        "updated_count": len(updated)
    })
