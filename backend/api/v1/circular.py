from flask import Blueprint, jsonify, request
from backend.models.circular import WasteInventory, BioEnergyOutput, CircularCredit
from backend.models.sustainability import SustainabilityScore
from backend.auth_utils import token_required
from backend.extensions import db

circular_bp = Blueprint('circular', __name__)

@circular_bp.route('/dashboard/<int:farm_id>', methods=['GET'])
@token_required
def get_circular_dashboard(current_user, farm_id):
    """
    Returns metrics for the Zero-Waste farm certification.
    """
    # 1. Aggregated Credits
    credits = CircularCredit.query.filter_by(farm_id=farm_id).all()
    total_credits = sum(c.credit_amount for c in credits)
    
    # 2. Energy Output
    energy = BioEnergyOutput.query.filter_by(farm_id=farm_id).all()
    total_energy = sum(e.amount_kwh for e in energy)
    carbon_saved = sum(e.carbon_offset_kg for e in energy)
    
    # 3. Waste Metrics
    waste_stats = db.session.query(
        WasteInventory.status, 
        db.func.sum(WasteInventory.quantity_kg)
    ).filter_by(farm_id=farm_id).group_by(WasteInventory.status).all()
    
    # Check for Zero-Waste Certification Qualification
    # Qualification: > 90% of waste must be TRANSFORMED or UTILIZED_ON_FARM
    total_waste = sum(q for s, q in waste_stats)
    recovered_waste = sum(q for s, q in waste_stats if s in ['TRANSFORMED', 'UTILIZED_ON_FARM'])
    is_certified = (recovered_waste / total_waste > 0.9) if total_waste > 0 else False

    return jsonify({
        'status': 'success',
        'data': {
            'credits_available': total_credits,
            'energy_generated_kwh': total_energy,
            'carbon_offset_kg': carbon_saved,
            'waste_distribution': {s: q for s, q in waste_stats},
            'zero_waste_qualified': is_certified,
            'recovery_rate': (recovered_waste / total_waste * 100) if total_waste > 0 else 0
        }
    })

@circular_bp.route('/waste/report', methods=['POST'])
@token_required
def report_waste(current_user):
    """
    Manually report a new waste batch from farm operations.
    """
    data = request.get_json()
    new_waste = WasteInventory(
        farm_id=data.get('farm_id'),
        waste_type=data.get('type', 'Organic Bio-Mass'),
        quantity_kg=data.get('quantity', 0.0),
        status='PENDING_TRANSFORMATION'
    )
    db.session.add(new_waste)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'waste_id': new_waste.id,
        'message': 'Waste batch logged and queued for transformation.'
    })
