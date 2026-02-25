from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.energy_grid import DecentralizedEnergyGrid, EnergyTokenMint
from backend.extensions import db

energy_grid_bp = Blueprint('energy_grid', __name__)

@energy_grid_bp.route('/', methods=['GET'])
@token_required
def get_grid_status(current_user):
    """View the live spot prices and load states of virtual power plants."""
    grids = DecentralizedEnergyGrid.query.all()
    
    data = []
    for g in grids:
        data.append({
            'grid_id': g.id,
            'grid_name': g.grid_name,
            'region': g.region_code,
            'status': g.status,
            'current_tariff_spot_price': g.dynamic_feed_in_tariff_usd,
            'load_mwh': g.current_active_load_mwh,
            'supply_mwh': g.current_supply_mwh,
            'capacity_mwh': g.target_capacity_mwh,
            'last_rebalanced': g.last_rebalancing.isoformat()
        })
        
    return jsonify({'status': 'success', 'data': data}), 200

@energy_grid_bp.route('/farm/<int:farm_id>/tokens', methods=['GET'])
@token_required
def get_farm_energy_tokens(current_user, farm_id):
    """Retrieve all tokens minted by this farm from biomass digestion."""
    tokens = EnergyTokenMint.query.filter_by(farm_id=farm_id).order_by(EnergyTokenMint.minted_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'count': len(tokens),
        'data': [t.to_dict() for t in tokens]
    }), 200
