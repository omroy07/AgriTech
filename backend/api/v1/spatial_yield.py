from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.spatial_yield import SpatialYieldGrid, TemporalYieldForex
from backend.extensions import db

spatial_yield_bp = Blueprint('spatial_yield', __name__)

@spatial_yield_bp.route('/grids', methods=['GET'])
@token_required
def get_spatial_grids(current_user):
    """
    Returns high-resolution yield mapping data used by the engine.
    """
    grids = SpatialYieldGrid.query.limit(200).all()
    results = []
    
    for g in grids:
        forex_data = [f.to_dict() for f in TemporalYieldForex.query.filter_by(grid_id=g.id).all()]
        data = g.to_dict()
        data['forex_predictions'] = forex_data
        results.append(data)
        
    return jsonify({
        'status': 'success',
        'count': len(results),
        'data': results
    })

@spatial_yield_bp.route('/grids/<string:region_id>/simulate-telemetry', methods=['POST'])
@token_required
def simulate_telemetry(current_user, region_id):
    """
    Dev tool: Manually push extreme satellite conditions to trigger price crashes.
    """
    from backend.services.prophet_engine import YieldProphetEngine
    payload = request.get_json()
    
    ndvi = payload.get('ndvi', 0.5)
    ct = payload.get('canopy_temperature_c', 25.0)
    moisture = payload.get('soil_moisture_pct', 40.0)
    
    grid = YieldProphetEngine.ingest_spatial_satellite_data(region_id, ndvi, ct, moisture)
    
    return jsonify({
        'status': 'success',
        'message': f'Extrapolated grid parameters for {region_id}',
        'data': grid.to_dict()
    }), 201
