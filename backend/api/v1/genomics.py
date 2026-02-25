from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.genomics import SeedGenomeProfile, LiveCropPhenotype, EpigeneticDriftLog
from backend.extensions import db

genomics_bp = Blueprint('genomics', __name__)

@genomics_bp.route('/seed-profiles', methods=['GET'])
@token_required
def get_seed_profiles(current_user):
    """Retrieve lab-minted genomic blueprints."""
    profiles = SeedGenomeProfile.query.all()
    return jsonify({
        'status': 'success',
        'data': [p.to_dict() for p in profiles]
    }), 200

@genomics_bp.route('/spawn-phenotype', methods=['POST'])
@token_required
def plant_phenotype(current_user):
    """Translate seed probabilities into real-world phenotypic instantiation."""
    from backend.services.genomic_simulator import QuantumGenomicSimulator
    data = request.json
    
    genome_id = data.get('genome_id')
    farm_id = data.get('farm_id')
    precision_idx = float(data.get('precision_agriculture_index', 1.0))
    
    phenotype = QuantumGenomicSimulator.spawn_live_phenotype(genome_id, farm_id, precision_idx)
    
    return jsonify({
        'status': 'success',
        'message': f'Wavefunction collapsed into phenotype ID {phenotype.id}',
        'data': phenotype.to_dict()
    }), 201

@genomics_bp.route('/epigenetic-drifts', methods=['GET'])
@token_required
def view_drift_logs(current_user):
    """Retrieve history of extreme weather events altering crop DNA."""
    phenotype_id = request.args.get('phenotype_id')
    query = EpigeneticDriftLog.query
    if phenotype_id:
        query = query.filter_by(phenotype_id=phenotype_id)
        
    logs = query.order_by(EpigeneticDriftLog.recorded_at.desc()).limit(100).all()
    
    data = []
    for l in logs:
        data.append({
            'log_id': l.id,
            'phenotype_id': l.phenotype_id,
            'trigger': l.triggering_event,
            'delta_health': l.delta_health_score,
            'delta_drought': l.delta_drought_tolerance,
            'timestamp': l.recorded_at.isoformat()
        })
        
    return jsonify({'status': 'success', 'data': data}), 200
