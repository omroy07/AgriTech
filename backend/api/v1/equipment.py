from flask import Blueprint, request, jsonify
from backend.services.rental_service import RentalService
from auth_utils import token_required
import json

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/', methods=['GET'])
def get_equipment():
    """List and filter available equipment"""
    category = request.args.get('category')
    location = request.args.get('location')
    max_rate = request.args.get('max_rate')
    
    equipment = RentalService.list_equipment(category, location, max_rate)
    return jsonify({
        'status': 'success',
        'data': [e.to_dict() for e in equipment]
    }), 200

@equipment_bp.route('/<int:equipment_id>', methods=['GET'])
def get_equipment_detail(equipment_id):
    """Get details for a specific equipment listing"""
    from backend.models.equipment import Equipment
    equipment = Equipment.query.get_or_404(equipment_id)
    return jsonify({
        'status': 'success',
        'data': equipment.to_dict()
    }), 200

@equipment_bp.route('/', methods=['POST'])
@token_required
def list_equipment(current_user):
    """Add a new equipment listing to the marketplace"""
    from backend.extensions import db
    from backend.models.equipment import Equipment
    
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
    try:
        equipment = Equipment(
            owner_id=current_user.id,
            name=data['name'],
            category=data['category'],
            description=data.get('description'),
            hourly_rate=data['hourly_rate'],
            daily_rate=data['daily_rate'],
            location=data['location'],
            specifications=json.dumps(data.get('specifications', {}))
        )
        db.session.add(equipment)
        db.session.commit()
        return jsonify({
            'status': 'success',
            'data': equipment.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
