from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.ai_diagnostics import CropDiagnosticReport, PathogenKnowledgeBase
from backend.services.diagnostic_engine import DiagnosticEngine
from backend.extensions import db

diagnostics_v2_bp = Blueprint('diagnostics_v2', __name__)

@diagnostics_v2_bp.route('/reports/history', methods=['GET'])
@token_required
def get_diagnostic_history(current_user):
    """Retrieve historical AI diagnostic results for a user's farm."""
    farm_id = request.args.get('farm_id')
    reports = CropDiagnosticReport.query.filter_by(farm_id=farm_id).order_by(CropDiagnosticReport.created_at.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [r.id for r in reports]
    }), 200

@diagnostics_v2_bp.route('/knowledge-base/pathogen', methods=['GET'])
@token_required
def get_pathogen_info(current_user):
    """Retrieve detailed mitigation strategies from the AI knowledge base."""
    name = request.args.get('name')
    pathogen = PathogenKnowledgeBase.query.filter_by(pathogen_name=name).first()
    if not pathogen:
        return jsonify({'error': 'Pathogen unknown'}), 404
        
    return jsonify({
        'status': 'success',
        'data': {
            'symptoms': pathogen.typical_symptoms,
            'treatment': pathogen.suggested_chemical_treatment,
            'organic': pathogen.organic_alternative
        }
    }), 200

@diagnostics_v2_bp.route('/verify-report/<int:report_id>', methods=['POST'])
@token_required
def verify_ai_report(current_user, report_id):
    """Expert verification of computer vision results to improve ML accuracy."""
    data = request.json
    # In a real app, verify user role is 'EXPERT'
    report = CropDiagnosticReport.query.get(report_id)
    if report:
        report.status = 'VERIFIED'
        db.session.commit()
        return jsonify({'status': 'success'}), 200
    return jsonify({'error': 'Report not found'}), 404
