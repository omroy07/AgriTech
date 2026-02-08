from flask import Blueprint, request, jsonify
from backend.services.farm_service import FarmService
from backend.models.farm import FarmMember, FarmRole
from auth_utils import token_required

farm_members_bp = Blueprint('farm_members', __name__)

@farm_members_bp.route('/<int:farm_id>/members', methods=['GET'])
@token_required
def list_members(current_user, farm_id):
    """Retrieve all team members associated with a farm"""
    members = FarmMember.query.filter_by(farm_id=farm_id).all()
    return jsonify({
        'status': 'success',
        'data': [m.to_dict() for m in members]
    }), 200

@farm_members_bp.route('/<int:farm_id>/invite', methods=['POST'])
@token_required
def invite_member(current_user, farm_id):
    """Invite/Add a new member to the farm team"""
    # Authorization: Only OWNERS or MANAGERS can invite
    inviter = FarmMember.query.filter_by(farm_id=farm_id, user_id=current_user.id).first()
    if not inviter or inviter.role not in [FarmRole.OWNER.value, FarmRole.MANAGER.value]:
        return jsonify({'status': 'error', 'message': 'Insufficient permissions to invite members'}), 403
        
    data = request.get_json()
    user_id = data.get('user_id')
    role = data.get('role', FarmRole.WORKER.value)
    
    member, error = FarmService.add_member(
        farm_id=farm_id,
        user_id=user_id,
        role=role,
        invited_by_id=current_user.id
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({
        'status': 'success',
        'data': member.to_dict()
    }), 201

@farm_members_bp.route('/<int:member_id>', methods=['DELETE'])
@token_required
def remove_member(current_user, member_id):
    """Remove a member from the farm (offboarding)"""
    from backend.extensions import db
    member = FarmMember.query.get_or_404(member_id)
    
    # Check if inviter has permission
    inviter = FarmMember.query.filter_by(farm_id=member.farm_id, user_id=current_user.id).first()
    if not inviter or inviter.role not in [FarmRole.OWNER.value, FarmRole.MANAGER.value]:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
        
    if member.role == FarmRole.OWNER.value:
        return jsonify({'status': 'error', 'message': 'Cannot remove farm owner'}), 400
        
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Member offboarded'}), 200
