"""
Smart Freight & Digital Corridor API — L3-1631
"""
from flask import Blueprint, request, jsonify
from auth_utils import token_required
from backend.extensions import db
from backend.services.logistics_orchestrator import LogisticsOrchestrator
from backend.models.logistics_v2 import (
    TransportRoute, PhytoSanitaryCertificate, FreightEscrow,
    CustomsCheckpoint, GPSTelemetry
)
from backend.models.traceability import SupplyBatch
import logging

logger = logging.getLogger(__name__)
smart_freight_bp = Blueprint('smart_freight', __name__)


# ─── 1. Issue Phyto-Sanitary Certificate ──────────────────────────────────────
@smart_freight_bp.route('/phyto-cert/issue', methods=['POST'])
@token_required
def issue_phyto_cert(current_user):
    """
    Autonomously generates and signs a Phyto-Sanitary Certificate for a shipment.
    Required: route_id, batch_id, origin_country, destination_country
    """
    data = request.get_json()
    required = ['route_id', 'batch_id', 'origin_country', 'destination_country']
    if not data or not all(k in data for k in required):
        return jsonify({'status': 'error', 'message': f'Missing required fields: {required}'}), 400

    cert, err = LogisticsOrchestrator.generate_phyto_cert(
        route_id=data['route_id'],
        batch_id=data['batch_id'],
        origin_country=data['origin_country'],
        destination_country=data['destination_country']
    )
    if err:
        return jsonify({'status': 'error', 'message': err}), 400

    return jsonify({'status': 'success', 'data': cert.to_dict()}), 201


# ─── 2. Verify Phyto Certificate ──────────────────────────────────────────────
@smart_freight_bp.route('/phyto-cert/verify/<cert_number>', methods=['GET'])
def verify_phyto_cert(cert_number):
    """Public-facing endpoint for border agents to verify certificate authenticity."""
    cert = PhytoSanitaryCertificate.query.filter_by(certificate_number=cert_number).first()
    if not cert:
        return jsonify({'status': 'error', 'message': 'Certificate not found.'}), 404

    import hashlib, json
    recalc = hashlib.sha256(cert.certificate_payload_json.encode()).hexdigest()
    is_valid = recalc == cert.signature_hash

    return jsonify({
        'status': 'success',
        'valid': is_valid,
        'cert_status': cert.status,
        'data': cert.to_dict()
    }), 200


# ─── 3. Lock Freight Escrow ────────────────────────────────────────────────────
@smart_freight_bp.route('/escrow/lock', methods=['POST'])
@token_required
def lock_escrow(current_user):
    """
    Creates a smart-contract freight escrow. Funds locked until GPS delivery confirmed.
    Required: route_id, driver_id, dest_lat, dest_lng, estimated_distance_km
    Optional: current_fuel_price (USD/L)
    """
    data = request.get_json()
    required = ['route_id', 'driver_id', 'dest_lat', 'dest_lng', 'estimated_distance_km']
    if not data or not all(k in data for k in required):
        return jsonify({'status': 'error', 'message': f'Missing fields: {required}'}), 400

    escrow, err = LogisticsOrchestrator.lock_freight_escrow(
        route_id=data['route_id'],
        driver_id=data['driver_id'],
        dest_lat=float(data['dest_lat']),
        dest_lng=float(data['dest_lng']),
        estimated_distance_km=float(data['estimated_distance_km']),
        current_fuel_price=float(data.get('current_fuel_price', 1.10))
    )
    if err:
        return jsonify({'status': 'error', 'message': err}), 400

    return jsonify({
        'status': 'success',
        'message': 'Freight escrow locked. Release pending GPS geo-fence confirmation.',
        'data': escrow.to_dict()
    }), 201


# ─── 4. Ingest GPS Telemetry Ping ─────────────────────────────────────────────
@smart_freight_bp.route('/gps/ping', methods=['POST'])
def ingest_gps():
    """
    IoT gateway endpoint for real-time GPS pings.
    Evaluates geo-fence and triggers escrow release autonomously.
    Required: route_id, vehicle_id, lat, lng
    Optional: speed, fuel_price
    """
    data = request.get_json()
    if not data or not all(k in data for k in ['route_id', 'vehicle_id', 'lat', 'lng']):
        return jsonify({'status': 'error', 'message': 'route_id, vehicle_id, lat, lng required.'}), 400

    result = LogisticsOrchestrator.ingest_gps_ping(
        route_id=data['route_id'],
        vehicle_id=data['vehicle_id'],
        lat=float(data['lat']),
        lng=float(data['lng']),
        speed=float(data.get('speed', 0.0)),
        fuel_price=float(data.get('fuel_price', 1.10))
    )

    return jsonify({'status': 'success', 'data': result}), 200


# ─── 5. Log Customs Arrival ───────────────────────────────────────────────────
@smart_freight_bp.route('/customs/arrive', methods=['POST'])
@token_required
def customs_arrive(current_user):
    """Logs vehicle arrival at a customs checkpoint."""
    data = request.get_json()
    if not data or 'route_id' not in data or 'checkpoint_name' not in data:
        return jsonify({'status': 'error', 'message': 'route_id and checkpoint_name required.'}), 400

    cp = LogisticsOrchestrator.log_customs_arrival(
        route_id=data['route_id'],
        checkpoint_name=data['checkpoint_name'],
        country=data.get('country', 'Unknown'),
        phyto_cert_id=data.get('phyto_cert_id')
    )
    return jsonify({'status': 'success', 'data': cp.to_dict()}), 201


# ─── 6. Clear Customs Checkpoint ─────────────────────────────────────────────
@smart_freight_bp.route('/customs/<int:checkpoint_id>/clear', methods=['PATCH'])
@token_required
def clear_customs(current_user, checkpoint_id):
    """
    Clears a customs checkpoint, calculates wait time, and applies
    dynamic delay surcharge to the freight escrow.
    """
    data = request.get_json(silent=True) or {}
    cp, err = LogisticsOrchestrator.clear_customs(checkpoint_id, notes=data.get('notes'))
    if err:
        return jsonify({'status': 'error', 'message': err}), 400

    return jsonify({
        'status': 'success',
        'data': {
            **cp.to_dict(),
            'delay_surcharge_applied': cp.wait_hours > 4.0
        }
    }), 200


# ─── 7. Escrow Status & Freight Dashboard ────────────────────────────────────
@smart_freight_bp.route('/escrow/<int:route_id>', methods=['GET'])
@token_required
def get_escrow_status(current_user, route_id):
    """Returns live freight escrow status, pricing breakdown, and geo-fence config."""
    escrow = FreightEscrow.query.filter_by(route_id=route_id).first()
    if not escrow:
        return jsonify({'status': 'error', 'message': 'No escrow found for this route.'}), 404

    checkpoints = CustomsCheckpoint.query.filter_by(route_id=route_id).all()
    latest_ping = GPSTelemetry.query.filter_by(route_id=route_id).order_by(
        GPSTelemetry.recorded_at.desc()
    ).first()

    return jsonify({
        'status': 'success',
        'data': {
            'escrow': escrow.to_dict(),
            'geo_fence': {
                'destination_lat': escrow.destination_lat,
                'destination_lng': escrow.destination_lng,
                'radius_meters': escrow.geo_fence_radius_meters,
                'passed': escrow.geo_fence_passed
            },
            'customs_checkpoints': [c.to_dict() for c in checkpoints],
            'latest_gps': {
                'lat': latest_ping.latitude if latest_ping else None,
                'lng': latest_ping.longitude if latest_ping else None,
                'speed': latest_ping.speed_kmh if latest_ping else None,
                'recorded_at': latest_ping.recorded_at.isoformat() if latest_ping else None
            }
        }
    }), 200
