from flask import Blueprint, request, jsonify, current_app
from backend.extensions import db
from .models import Field, FieldAnalysis
from backend.models import User
from .utils import SpatialUtils
import json
import os
import uuid
import cv2

spatial_bp = Blueprint('spatial', __name__, url_prefix='/api/spatial')

@spatial_bp.route('/fields', methods=['POST'])
def create_field():
    try:
        data = request.get_json()
        print(f"DEBUG: Received field save request: {data}")
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        if not data.get('name') or not data.get('boundary'):
            return jsonify({'error': 'Name and boundary are required'}), 400
            
            
        # For demo: use the first available user if no integrated auth yet
        # For demo: use the first available user if no integrated auth yet
        user = User.query.first()
        if not user:
            # Create a dummy user for demo purposes if table is empty
            user = User(username="DemoUser", email="demo@agritech.com")
            user.set_password("demo123")
            db.session.add(user)
            db.session.commit()
            
        target_user_id = user.id
        
        new_field = Field(
            user_id=target_user_id,
            name=data['name'],
            boundary_geojson=json.dumps(data['boundary']),
            area_hectares=data.get('area', 0.0),
            crop_type=data.get('crop', 'Unknown')
        )
        
        db.session.add(new_field)
        db.session.commit()
        
        return jsonify(new_field.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@spatial_bp.route('/fields', methods=['GET'])
def get_fields():
    try:
        # TODO: Filter by user_id
        fields = Field.query.all()
        return jsonify([f.to_dict() for f in fields]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@spatial_bp.route('/analyze/<int:field_id>', methods=['POST'])
def analyze_field(field_id):
    """
    Trigger NDVI analysis for a field.
    In production, this would dispatch a Celery task.
    """
    try:
        field = Field.query.get_or_404(field_id)
        
        # Mock Analysis
        # 1. Fetch satellite data for field location (Mocked in Utils)
        heatmap_img, stats = SpatialUtils.process_satellite_imagery(None, field.boundary_geojson)
        
        # 2. Save Heatmap Image
        filename = f"ndvi_{field_id}_{uuid.uuid4().hex[:8]}.png"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'spatial_outputs')
        os.makedirs(save_path, exist_ok=True)
        
        full_path = os.path.join(save_path, filename)
        cv2.imwrite(full_path, heatmap_img)
        
        # 3. Create Analysis Record
        analysis = FieldAnalysis(
            field_id=field.id,
            analysis_type='NDVI',
            result_data=stats,
            overlay_image_path=f"uploads/spatial_outputs/{filename}" # Relative path for client
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify(analysis.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
