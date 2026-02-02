"""
Disease Incident Reporting & Outbreak Monitoring API
Endpoints for geo-tagged disease reporting and outbreak alerts.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import DiseaseIncident, OutbreakZone, OutbreakAlert, User
from backend.services.geospatial_service import GeospatialService
from backend.extensions import db
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

disease_bp = Blueprint('disease', __name__, url_prefix='/api/v1/disease')


@disease_bp.route('/incidents', methods=['POST'])
@jwt_required()
def report_disease_incident():
    """
    Report a geo-tagged disease incident from a farm location.
    
    Request JSON:
    {
        "disease_name": "Late Blight",
        "crop_affected": "Tomato",
        "severity_level": "high",
        "symptoms": "Brown spots on leaves...",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "affected_area": 2.5,  // in hectares
        "images": ["base64_image_data"]  // optional
    }
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['disease_name', 'crop_affected', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate coordinates
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({'error': 'Invalid coordinates'}), 400
        
        # Create incident record
        incident_id = f"INC-{uuid.uuid4().hex[:12].upper()}"
        
        incident = DiseaseIncident(
            incident_id=incident_id,
            user_id=current_user_id,
            disease_name=data['disease_name'],
            crop_affected=data['crop_affected'],
            severity_level=data.get('severity_level', 'medium'),
            symptoms=data.get('symptoms', ''),
            latitude=lat,
            longitude=lon,
            affected_area=data.get('affected_area', 0.0),
            detection_method=data.get('detection_method', 'manual'),
            verification_status='pending',
            reported_at=datetime.utcnow()
        )
        
        db.session.add(incident)
        db.session.commit()
        
        logger.info(f"Disease incident reported: {incident_id} by user {current_user_id}")
        
        # Trigger outbreak detection if needed (check immediate proximity)
        from backend.tasks import detect_disease_outbreaks_task
        detect_disease_outbreaks_task.delay()
        
        return jsonify({
            'success': True,
            'incident_id': incident_id,
            'message': 'Disease incident reported successfully',
            'incident': incident.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        logger.error(f"Failed to report disease incident: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to report incident'}), 500


@disease_bp.route('/incidents', methods=['GET'])
@jwt_required()
def get_disease_incidents():
    """
    Get disease incidents with optional filters.
    Query params: disease_name, crop, severity, radius_km, lat, lon, days
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Build query
        query = DiseaseIncident.query
        
        # Filter by disease name
        if request.args.get('disease_name'):
            query = query.filter(DiseaseIncident.disease_name.ilike(f"%{request.args.get('disease_name')}%"))
        
        # Filter by crop
        if request.args.get('crop'):
            query = query.filter(DiseaseIncident.crop_affected.ilike(f"%{request.args.get('crop')}%"))
        
        # Filter by severity
        if request.args.get('severity'):
            query = query.filter(DiseaseIncident.severity_level == request.args.get('severity'))
        
        # Filter by time range
        days = int(request.args.get('days', 30))
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(DiseaseIncident.reported_at >= cutoff_date)
        
        # Filter by proximity (if lat/lon provided)
        if request.args.get('lat') and request.args.get('lon'):
            lat = float(request.args.get('lat'))
            lon = float(request.args.get('lon'))
            radius_km = float(request.args.get('radius_km', 50))
            
            incidents = query.all()
            nearby_incidents = []
            
            for incident in incidents:
                distance = GeospatialService.calculate_distance(
                    lat, lon, incident.latitude, incident.longitude
                )
                if distance <= radius_km:
                    incident_dict = incident.to_dict()
                    incident_dict['distance_km'] = round(distance, 2)
                    nearby_incidents.append(incident_dict)
            
            # Sort by distance
            nearby_incidents.sort(key=lambda x: x['distance_km'])
            
            return jsonify({
                'success': True,
                'count': len(nearby_incidents),
                'incidents': nearby_incidents
            }), 200
        
        # Get all matching incidents
        incidents = query.order_by(DiseaseIncident.reported_at.desc()).all()
        
        return jsonify({
            'success': True,
            'count': len(incidents),
            'incidents': [inc.to_dict() for inc in incidents]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to fetch incidents: {str(e)}")
        return jsonify({'error': 'Failed to fetch incidents'}), 500


@disease_bp.route('/incidents/<incident_id>', methods=['GET'])
@jwt_required()
def get_disease_incident(incident_id):
    """Get detailed information about a specific incident."""
    try:
        incident = DiseaseIncident.query.filter_by(incident_id=incident_id).first()
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        return jsonify({
            'success': True,
            'incident': incident.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to fetch incident: {str(e)}")
        return jsonify({'error': 'Failed to fetch incident'}), 500


@disease_bp.route('/outbreaks', methods=['GET'])
@jwt_required()
def get_outbreak_zones():
    """
    Get active outbreak zones with optional filters.
    Query params: disease_name, crop, risk_level, lat, lon
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Build query for active outbreak zones
        query = OutbreakZone.query.filter_by(status='active')
        
        # Filter by disease
        if request.args.get('disease_name'):
            query = query.filter(OutbreakZone.disease_name.ilike(f"%{request.args.get('disease_name')}%"))
        
        # Filter by crop
        if request.args.get('crop'):
            query = query.filter(OutbreakZone.crop_affected.ilike(f"%{request.args.get('crop')}%"))
        
        # Filter by risk level
        if request.args.get('risk_level'):
            query = query.filter(OutbreakZone.risk_level == request.args.get('risk_level'))
        
        zones = query.order_by(OutbreakZone.created_at.desc()).all()
        
        # If user location provided, calculate distances
        if request.args.get('lat') and request.args.get('lon'):
            lat = float(request.args.get('lat'))
            lon = float(request.args.get('lon'))
            
            zones_with_distance = []
            for zone in zones:
                distance = GeospatialService.calculate_distance(
                    lat, lon, zone.center_latitude, zone.center_longitude
                )
                zone_dict = zone.to_dict()
                zone_dict['distance_km'] = round(distance, 2)
                zone_dict['is_at_risk'] = distance <= zone.radius_km * 1.5
                zones_with_distance.append(zone_dict)
            
            # Sort by distance
            zones_with_distance.sort(key=lambda x: x['distance_km'])
            
            return jsonify({
                'success': True,
                'count': len(zones_with_distance),
                'zones': zones_with_distance
            }), 200
        
        return jsonify({
            'success': True,
            'count': len(zones),
            'zones': [zone.to_dict() for zone in zones]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to fetch outbreak zones: {str(e)}")
        return jsonify({'error': 'Failed to fetch outbreak zones'}), 500


@disease_bp.route('/outbreaks/<zone_id>', methods=['GET'])
@jwt_required()
def get_outbreak_zone_details(zone_id):
    """Get detailed information about a specific outbreak zone."""
    try:
        zone = OutbreakZone.query.filter_by(zone_id=zone_id).first()
        
        if not zone:
            return jsonify({'error': 'Outbreak zone not found'}), 404
        
        # Get incidents in this zone
        incidents = GeospatialService.find_incidents_in_radius(
            zone.center_latitude,
            zone.center_longitude,
            zone.radius_km,
            disease_name=zone.disease_name,
            crop_affected=zone.crop_affected
        )
        
        return jsonify({
            'success': True,
            'zone': zone.to_dict(),
            'incidents': [inc.to_dict() for inc in incidents]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to fetch outbreak zone details: {str(e)}")
        return jsonify({'error': 'Failed to fetch zone details'}), 500


@disease_bp.route('/my-risk', methods=['GET'])
@jwt_required()
def check_my_risk():
    """
    Check if current user's farm is at risk due to nearby outbreaks.
    Uses user's saved farm location.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.farm_latitude or not user.farm_longitude:
            return jsonify({
                'error': 'Farm location not set. Please update your profile with farm coordinates.'
            }), 400
        
        # Check for nearby outbreaks
        at_risk_zones = GeospatialService.check_user_in_outbreak_zones(user)
        
        # Get user's outbreak alerts
        alerts = OutbreakAlert.query.filter_by(
            user_id=current_user_id
        ).order_by(OutbreakAlert.created_at.desc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'farm_location': {
                'latitude': user.farm_latitude,
                'longitude': user.farm_longitude,
                'address': user.farm_address
            },
            'is_at_risk': len(at_risk_zones) > 0,
            'nearby_outbreaks': [
                {
                    'zone_id': zone.zone_id,
                    'disease_name': zone.disease_name,
                    'crop_affected': zone.crop_affected,
                    'risk_level': zone.risk_level,
                    'distance_km': round(distance, 2)
                }
                for zone, distance in at_risk_zones
            ],
            'recent_alerts': [alert.to_dict() for alert in alerts]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to check risk status: {str(e)}")
        return jsonify({'error': 'Failed to check risk status'}), 500


@disease_bp.route('/incidents/geojson', methods=['GET'])
@jwt_required()
def get_incidents_geojson():
    """
    Get disease incidents as GeoJSON for mapping.
    Query params: disease_name, crop, severity, days
    """
    try:
        disease_name = request.args.get('disease_name')
        crop_affected = request.args.get('crop')
        severity = request.args.get('severity')
        days = int(request.args.get('days', 30))
        
        geojson = GeospatialService.get_incidents_geojson(
            disease_name=disease_name,
            crop_affected=crop_affected,
            severity_level=severity,
            days_back=days
        )
        
        return jsonify(geojson), 200
    
    except Exception as e:
        logger.error(f"Failed to generate GeoJSON: {str(e)}")
        return jsonify({'error': 'Failed to generate GeoJSON'}), 500


@disease_bp.route('/outbreaks/geojson', methods=['GET'])
@jwt_required()
def get_outbreaks_geojson():
    """
    Get outbreak zones as GeoJSON for mapping.
    Query params: disease_name, crop, risk_level
    """
    try:
        disease_name = request.args.get('disease_name')
        crop_affected = request.args.get('crop')
        risk_level = request.args.get('risk_level')
        
        geojson = GeospatialService.get_outbreak_zones_geojson(
            disease_name=disease_name,
            crop_affected=crop_affected,
            risk_level=risk_level
        )
        
        return jsonify(geojson), 200
    
    except Exception as e:
        logger.error(f"Failed to generate outbreak GeoJSON: {str(e)}")
        return jsonify({'error': 'Failed to generate GeoJSON'}), 500


@disease_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_my_alerts():
    """Get current user's outbreak alerts."""
    try:
        current_user_id = get_jwt_identity()
        
        # Filter parameters
        status = request.args.get('status', 'active')
        priority = request.args.get('priority')
        
        query = OutbreakAlert.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        
        alerts = query.order_by(OutbreakAlert.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'count': len(alerts),
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to fetch alerts: {str(e)}")
        return jsonify({'error': 'Failed to fetch alerts'}), 500


@disease_bp.route('/alerts/<alert_id>/acknowledge', methods=['POST'])
@jwt_required()
def acknowledge_alert(alert_id):
    """Mark an outbreak alert as acknowledged."""
    try:
        current_user_id = get_jwt_identity()
        
        alert = OutbreakAlert.query.filter_by(
            alert_id=alert_id,
            user_id=current_user_id
        ).first()
        
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        
        alert.status = 'acknowledged'
        alert.acknowledged_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Alert acknowledged',
            'alert': alert.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to acknowledge alert: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to acknowledge alert'}), 500


# Export blueprint
__all__ = ['disease_bp']
