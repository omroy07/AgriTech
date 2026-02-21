from flask import Blueprint, jsonify, request
from backend.models.disease import MigrationVector, ContainmentZone
from backend.models.gews import OutbreakZone, DiseaseIncident
from backend.models.traceability import SupplyBatch
from backend.services.neutralization_engine import NeutralizationEngine
from backend.auth_utils import token_required
from backend.extensions import db

biosecurity_bp = Blueprint('biosecurity', __name__)

@biosecurity_bp.route('/heatmap', methods=['GET'])
@token_required
def get_outbreak_heatmap(current_user):
    """
    Returns a real-time heatmap of outbreaks and containment zones.
    """
    outbreaks = OutbreakZone.query.filter_by(status='active').all()
    containment = ContainmentZone.query.filter_by(enforcement_level='LOCKED').all()
    vectors = MigrationVector.query.order_by(MigrationVector.created_at.desc()).limit(20).all()
    
    return jsonify({
        'status': 'success',
        'data': {
            'outbreaks': [o.to_dict() for o in outbreaks],
            'containment_zones': [c.to_dict() for c in containment],
            'migration_vectors': [{
                'origin': [v.origin_lat, v.origin_lng],
                'target': [v.target_lat, v.target_lng],
                'eta': v.predicted_arrival_time.isoformat(),
                'speed': v.speed_km_per_day
            } for v in vectors]
        }
    })

@biosecurity_bp.route('/containment/trigger', methods=['POST'])
@token_required
def trigger_blockade(current_user):
    """
    Manually trigger an autonomous blockade.
    """
    data = request.get_json()
    zone_id = data.get('zone_id')
    
    success = NeutralizationEngine.trigger_autonomous_blockade(zone_id)
    
    return jsonify({
        'status': 'success' if success else 'failed',
        'message': 'Autonomous blockade enforced and irrigation shutdown triggered.' if success else 'Failed to trigger blockade.'
    })

@biosecurity_bp.route('/clearance/generate/<int:batch_id>', methods=['POST'])
@token_required
def generate_clearance(current_user, batch_id):
    """
    Requests a bio-clearance hash for a batch.
    """
    clearance_hash = NeutralizationEngine.generate_bio_clearance_hash(batch_id)
    
    if not clearance_hash:
        return jsonify({
            'status': 'error',
            'message': 'Batch failed bio-security check. Quarantine enforcement active.'
        }), 403
        
    return jsonify({
        'status': 'success',
        'bio_clearance_hash': clearance_hash
    })
