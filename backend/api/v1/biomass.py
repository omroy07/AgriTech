from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.biomass import BiomassStockpile, BiogasDigesterLog
from backend.extensions import db

biomass_bp = Blueprint('biomass', __name__)

@biomass_bp.route('/stockpile/declare', methods=['POST'])
@token_required
def declare_stockpile(current_user):
    """Register crop waste available for digestion."""
    data = request.json
    farm_id = data.get('farm_id')
    
    # Needs owner check (skipped for brevity)
    stockpile = BiomassStockpile(
        farm_id=farm_id,
        stockpile_type=data.get('type', 'RICE_STRAW'),
        total_mass_kg=float(data.get('mass_kg', 0)),
        moisture_content_pct=float(data.get('moisture_pct', 15.0)),
        calorific_value_mj_per_kg=float(data.get('calorific_mj_kg', 16.0))
    )
    db.session.add(stockpile)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'data': stockpile.to_dict()
    }), 201

@biomass_bp.route('/digester/burn', methods=['POST'])
@token_required
def trigger_combustion(current_user):
    """Manually initiate digestion/combustion of a stockpile."""
    from backend.services.energy_token_service import DecentralizedEnergyLedger
    data = request.json
    
    farm_id = data.get('farm_id')
    stockpile_id = data.get('stockpile_id')
    kg_to_burn = float(data.get('mass_kg'))
    
    try:
        log = DecentralizedEnergyLedger.log_biomass_combustion_cycle(farm_id, stockpile_id, kg_to_burn)
        return jsonify({    
            'status': 'success',
            'message': 'Combined heat & power digestion finished',
            'data': log.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@biomass_bp.route('/farm/<int:farm_id>/logs', methods=['GET'])
@token_required
def get_digest_logs(current_user, farm_id):
    """Retrieve historical digestion records."""
    logs = BiogasDigesterLog.query.filter_by(farm_id=farm_id).order_by(BiogasDigesterLog.end_time.desc()).limit(50).all()
    return jsonify({
        'status': 'success', 
        'data': [l.to_dict() for l in logs]
    }), 200
