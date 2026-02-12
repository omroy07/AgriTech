from flask import Blueprint, jsonify, request
from backend.services.audit_service import AuditService
from auth_utils import token_required, roles_required

audit_bp = Blueprint('audit_bp', __name__, url_prefix='/audit')

@audit_bp.route('/logs', methods=['GET'])
@token_required
@roles_required('admin')
def get_audit_logs():
    """Retrieves filtered audit logs (Admin only)."""
    filters = {
        'user_id': request.args.get('user_id', type=int),
        'action': request.args.get('action'),
        'risk_level': request.args.get('risk_level'),
        'threat_only': request.args.get('threat_only') == 'true',
        'start_date': request.args.get('start_date')
    }
    
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    logs = AuditService.get_logs(filters, limit, offset)
    return jsonify({
        'status': 'success',
        'count': len(logs),
        'logs': [log.to_dict() for log in logs]
    })

@audit_bp.route('/sessions', methods=['GET'])
@token_required
@roles_required('admin')
def get_active_sessions():
    """Retrieves active user sessions."""
    from backend.models import UserSession
    sessions = UserSession.query.filter_by(is_active=True).order_by(UserSession.last_activity.desc()).all()
    return jsonify({
        'status': 'success',
        'count': len(sessions),
        'sessions': [s.to_dict() for s in sessions]
    })

@audit_bp.route('/stats', methods=['GET'])
@token_required
@roles_required('admin')
def get_audit_stats():
    """Returns high-level security and activity statistics."""
    from backend.models import AuditLog, UserSession
    from backend.extensions import db
    from datetime import datetime, timedelta
    
    last_24h = datetime.utcnow() - timedelta(hours=24)
    
    total_actions = AuditLog.query.filter(AuditLog.timestamp >= last_24h).count()
    threats_detected = AuditLog.query.filter(AuditLog.timestamp >= last_24h, AuditLog.threat_flag == True).count()
    active_users = db.session.query(db.func.count(db.func.distinct(UserSession.user_id))).filter(UserSession.is_active == True).scalar()
    
    # Categorical breakdown
    categories = db.session.query(
        AuditLog.risk_level, db.func.count(AuditLog.id)
    ).filter(AuditLog.timestamp >= last_24h).group_by(AuditLog.risk_level).all()
    
    return jsonify({
        'status': 'success',
        'stats': {
            'total_actions_24h': total_actions,
            'threats_detected_24h': threats_detected,
            'active_users': active_users,
            'risk_distribution': {level: count for level, count in categories}
        }
    })
