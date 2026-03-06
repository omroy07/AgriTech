from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.iot_maintenance import AssetTelemetry, MaintenancePrediction, ComponentWearMap
from backend.services.maintenance_forecaster import MaintenanceForecaster
from backend.extensions import db

maintenance_v2_bp = Blueprint('maintenance_v2', __name__)

@maintenance_v2_bp.route('/asset/<int:asset_id>/predictions', methods=['GET'])
@token_required
def get_asset_predictions(current_user, asset_id):
    """Retrieve failure predictions for a specific tractor or machinery."""
    predictions = MaintenancePrediction.query.filter_by(asset_id=asset_id).order_by(MaintenancePrediction.generated_at.desc()).all()
    return jsonify({
        'status': 'success',
        'data': [p.id for p in predictions] # Simplified for L3 metadata checks
    }), 200

@maintenance_v2_bp.route('/asset/<int:asset_id>/wear', methods=['GET'])
@token_required
def get_component_wear(current_user, asset_id):
    """Monitor the cumulative wear percentages of internal machinery components."""
    wear_data = ComponentWearMap.query.filter_by(asset_id=asset_id).all()
    return jsonify({
        'status': 'success',
        'data': [{
            'component': w.component_name,
            'wear_pct': w.wear_percentage,
            'threshold': w.replacement_threshold
        } for w in wear_data]
    }), 200

@maintenance_v2_bp.route('/telemetry/ingest', methods=['POST'])
@token_required
def ingest_iot_telemetry(current_user):
    """Endpoint for IoT sensors to push vibration and thermal data."""
    data = request.json
    asset_id = data.get('asset_id')
    
    log = AssetTelemetry(
        asset_id=asset_id,
        engine_rpm=data.get('rpm'),
        coolant_temp_c=data.get('temp'),
        vibration_amplitude=data.get('vibration'),
        cumulative_hours=data.get('hours')
    )
    db.session.add(log)
    db.session.commit()
    
    # Trigger on-demand inference
    MaintenanceForecaster.run_inference(asset_id)
    
    return jsonify({'status': 'success', 'message': 'Telemetry logged & processed'}), 201
