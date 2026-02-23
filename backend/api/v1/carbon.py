"""
Carbon & ESG Marketplace API — L3-1632
"""
from flask import Blueprint, request, jsonify
from auth_utils import token_required
from backend.extensions import db
from backend.services.carbon_sequestration_engine import (
    CarbonSequestrationEngine, CARBON_CREDIT_PRICE_USD
)
from backend.models.soil_health import RegenerativeFarmingLog, CarbonMintEvent
from backend.models.sustainability import ESGMarketListing, SustainabilityScore
from backend.models.farm import Farm
import logging

logger = logging.getLogger(__name__)
carbon_bp = Blueprint('carbon', __name__)


# ─── 1. Log a Regenerative Farming Practice ───────────────────────────────────
@carbon_bp.route('/practices', methods=['POST'])
@token_required
def log_practice(current_user):
    """
    Records a regenerative farming practice entry.
    Requires: farm_id, practice_type, area_hectares
    Optional: soil_organic_carbon_percent, bulk_density_gcm3, sampling_depth_cm
    """
    data = request.get_json()
    required = ['farm_id', 'practice_type', 'area_hectares']
    if not data or not all(k in data for k in required):
        return jsonify({'status': 'error', 'message': f'Missing required fields: {required}'}), 400

    farm = Farm.query.get(data['farm_id'])
    if not farm:
        return jsonify({'status': 'error', 'message': 'Farm not found.'}), 404

    valid_practices = ['NO_TILL', 'COVER_CROP', 'ORGANIC_FERTILIZER', 'AGROFORESTRY', 'BIOCHAR']
    if data['practice_type'] not in valid_practices:
        return jsonify({'status': 'error', 'message': f'Invalid practice_type. Must be one of: {valid_practices}'}), 400

    # Pre-calculate estimated CO2e for immediate feedback
    preview_log = RegenerativeFarmingLog(
        farm_id=data['farm_id'],
        practice_type=data['practice_type'],
        area_hectares=float(data['area_hectares']),
        soil_organic_carbon_percent=data.get('soil_organic_carbon_percent', 1.5),
        bulk_density_gcm3=data.get('bulk_density_gcm3', 1.3),
        sampling_depth_cm=data.get('sampling_depth_cm', 30.0),
        soil_test_id=data.get('soil_test_id')
    )
    estimated = CarbonSequestrationEngine.calculate_co2e(preview_log)
    preview_log.estimated_co2e_tonnes = estimated
    db.session.add(preview_log)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'data': {
            **preview_log.to_dict(),
            'estimated_co2e_tonnes': estimated,
            'estimated_credit_value_usd': round(estimated * CARBON_CREDIT_PRICE_USD, 2),
            'next_step': 'Submit for verification to unlock minting.'
        }
    }), 201


# ─── 2. Verify a Farming Log (Admin/Auditor action) ───────────────────────────
@carbon_bp.route('/practices/<int:log_id>/verify', methods=['PATCH'])
@token_required
def verify_practice(current_user, log_id):
    """Marks a farming log as verified, enabling credit minting."""
    log = RegenerativeFarmingLog.query.get(log_id)
    if not log:
        return jsonify({'status': 'error', 'message': 'Log not found'}), 404

    log.verified = True
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Log verified. Credits can now be minted.'}), 200


# ─── 3. Mint Credits for a Verified Log ───────────────────────────────────────
@carbon_bp.route('/practices/<int:log_id>/mint', methods=['POST'])
@token_required
def mint_credits(current_user, log_id):
    """
    Triggers the Carbon Sequestration Engine to mint credits for a verified log.
    Autonomously posts a double-entry ledger transaction.
    """
    price = request.get_json(silent=True) or {}
    price_per_tonne = price.get('price_per_tonne_usd', CARBON_CREDIT_PRICE_USD)

    event, err = CarbonSequestrationEngine.mint_credits(log_id, price_per_tonne)
    if err:
        return jsonify({'status': 'error', 'message': err}), 400

    return jsonify({
        'status': 'success',
        'data': {
            **event.to_dict(),
            'ledger_txn_posted': event.ledger_transaction_id is not None
        }
    }), 201


# ─── 4. List Credits on ESG Marketplace ──────────────────────────────────────
@carbon_bp.route('/market/list', methods=['POST'])
@token_required
def list_on_market(current_user):
    """
    Lists a minted carbon credit batch on the internal ESG marketplace.
    Requires: mint_event_id
    Optional: asking_price_usd, description
    """
    data = request.get_json()
    if not data or 'mint_event_id' not in data:
        return jsonify({'status': 'error', 'message': 'mint_event_id required.'}), 400

    listing, err = CarbonSequestrationEngine.list_on_esg_market(
        mint_event_id=data['mint_event_id'],
        asking_price_usd=data.get('asking_price_usd'),
        description=data.get('description')
    )
    if err:
        return jsonify({'status': 'error', 'message': err}), 400

    return jsonify({'status': 'success', 'data': listing.to_dict()}), 201


# ─── 5. Browse ESG Marketplace ────────────────────────────────────────────────
@carbon_bp.route('/market/listings', methods=['GET'])
@token_required
def browse_market(current_user):
    """
    Returns all active ESG marketplace listings with farm & credit metadata.
    Supports filter: ?min_credits=5&max_price=200
    """
    query = ESGMarketListing.query.filter_by(status='ACTIVE')

    min_credits = request.args.get('min_credits', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_credits:
        query = query.filter(ESGMarketListing.credits_offered >= min_credits)
    if max_price:
        query = query.filter(ESGMarketListing.asking_price_usd <= max_price)

    listings = query.order_by(ESGMarketListing.listed_at.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(listings),
        'data': [l.to_dict() for l in listings]
    }), 200


# ─── 6. Purchase Credits (Corporate Buyer) ───────────────────────────────────
@carbon_bp.route('/market/purchase/<int:listing_id>', methods=['POST'])
@token_required
def purchase_credits(current_user, listing_id):
    """
    Settles an ESG carbon credit purchase via double-entry ledger.
    """
    listing, err = CarbonSequestrationEngine.settle_esg_purchase(
        listing_id=listing_id,
        buyer_user_id=current_user.id
    )
    if err:
        return jsonify({'status': 'error', 'message': err}), 400

    return jsonify({
        'status': 'success',
        'message': 'Purchase settled. Credits transferred to your carbon portfolio.',
        'data': listing.to_dict()
    }), 200


# ─── 7. Farm Carbon Profile ───────────────────────────────────────────────────
@carbon_bp.route('/profile/<int:farm_id>', methods=['GET'])
@token_required
def get_carbon_profile(current_user, farm_id):
    """
    Returns a comprehensive carbon & ESG profile for a farm.
    Includes sequestration history, minted credits, sustainability score, and marketplace activity.
    """
    farm = Farm.query.get(farm_id)
    if not farm:
        return jsonify({'status': 'error', 'message': 'Farm not found.'}), 404

    logs = RegenerativeFarmingLog.query.filter_by(farm_id=farm_id).order_by(
        RegenerativeFarmingLog.logged_at.desc()).all()
    events = CarbonMintEvent.query.filter_by(farm_id=farm_id).all()
    score = SustainabilityScore.query.filter_by(farm_id=farm_id).first()
    active_listings = ESGMarketListing.query.filter_by(
        farm_id=farm_id, status='ACTIVE').count()
    sold_listings = ESGMarketListing.query.filter_by(
        farm_id=farm_id, status='SOLD').count()

    return jsonify({
        'status': 'success',
        'data': {
            'farm': {
                'id': farm.id,
                'name': farm.name,
                'is_no_till': farm.is_no_till,
                'cover_crop_active': farm.cover_crop_active,
                'organic_certified': farm.organic_certified,
                'sequestration_tier': farm.sequestration_tier,
                'total_credits_minted': farm.total_carbon_credits_minted
            },
            'sustainability_score': {
                'overall_rating': score.overall_rating if score else 0,
                'esg_carbon_score': score.esg_carbon_score if score else 0,
                'total_credits': score.total_credits_minted if score else 0
            },
            'practice_logs': [l.to_dict() for l in logs],
            'mint_events': [e.to_dict() for e in events],
            'marketplace': {
                'active_listings': active_listings,
                'completed_sales': sold_listings,
                'total_revenue_usd': sum(
                    e.sale_price_usd for e in events if e.sale_price_usd
                )
            }
        }
    }), 200
