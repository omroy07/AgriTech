from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.virulence import PathogenStrain, InfectionCombatSimulation
from backend.extensions import db

virulence_bp = Blueprint('virulence', __name__)

@virulence_bp.route('/strains/active', methods=['GET'])
@token_required
def active_pathogen_strains(current_user):
    """List genetically adapted pathogen strains currently infecting the world."""
    strains = PathogenStrain.query.filter_by(extinct_marker=False).order_by(PathogenStrain.mutation_generation.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [s.to_dict() for s in strains]
    }), 200

@virulence_bp.route('/combat-simulation/run', methods=['POST'])
@token_required
def execute_deterministic_combat_step(current_user):
    """Force an algorithmic sweep matching strains to random phenotypes."""
    from backend.services.virulence_engine import VirulenceEngine
    data = request.json
    
    num_engagements = int(data.get('engagements', 50))
    
    stats = VirulenceEngine.simulate_global_battles(num_engagements=num_engagements)
    
    return jsonify({
        'status': 'success',
        'message': f'Executed {stats.get("engagements_fired", 0)} engagements.',
        'data': stats
    }), 201

@virulence_bp.route('/combat-logs', methods=['GET'])
@token_required
def view_virulence_combat_logs(current_user):
    """Reads execution outcomes of pathogenic attack versus phenotypic defense."""
    logs = InfectionCombatSimulation.query.order_by(InfectionCombatSimulation.simulated_at.desc()).limit(200).all()
    
    data = []
    for l in logs:
        data.append({
            'simulation_id': l.id,
            'strain_id': l.strain_id,
            'phenotype_id': l.phenotype_id,
            'infection_success': l.infection_success,
            'attack_power': l.base_attack_power,
            'defense_power': l.crop_defense_power,
            'damage_inflicted': l.damage_inflicted_pct,
            'mutated': l.triggered_new_mutation,
            'timestamp': l.simulated_at.isoformat()
        })
        
    return jsonify({'status': 'success', 'count': len(data), 'data': data}), 200
