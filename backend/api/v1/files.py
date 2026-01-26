"""
File management routes for upload and download.
"""
from flask import Blueprint, request, jsonify, send_file
from backend.services.file_service import FileService
from backend.models import File
import os

files_bp = Blueprint('files', __name__, url_prefix='/api/files')


@files_bp.route('/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """
    Download a file by ID.
    
    Args:
        file_id: File database ID
    
    Returns:
        File download or error
    """
    try:
        file_record = File.query.get(file_id)
        
        if not file_record:
            return jsonify({
                'status': 'error',
                'message': 'File not found'
            }), 404
        
        # Check if file exists on disk
        if not os.path.exists(file_record.file_path):
            return jsonify({
                'status': 'error',
                'message': 'File not found on storage'
            }), 404
        
        # Send file
        return send_file(
            file_record.file_path,
            as_attachment=True,
            download_name=file_record.original_name,
            mimetype=file_record.mime_type
        )
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Download failed: {str(e)}'
        }), 500


@files_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_files(user_id):
    """
    Get all files for a specific user.
    
    Args:
        user_id: User ID
    
    Returns:
        JSON list of files
    """
    try:
        files = File.query.filter_by(user_id=user_id).order_by(File.created_at.desc()).all()
        
        return jsonify({
            'status': 'success',
            'files': [{
                'id': f.id,
                'original_name': f.original_name,
                'file_type': f.file_type,
                'file_size': f.file_size,
                'created_at': f.created_at.isoformat() if f.created_at else None
            } for f in files]
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve files: {str(e)}'
        }), 500


@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file.
    
    Form Data:
        file: File to upload
        user_id: (optional) User ID
    
    Returns:
        JSON with file info
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id', type=int)
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        file_record, error = FileService.save_file(file, user_id=user_id)
        
        if error:
            return jsonify({
                'status': 'error',
                'message': error
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'file': {
                'id': file_record.id,
                'original_name': file_record.original_name,
                'file_type': file_record.file_type,
                'file_size': file_record.file_size
            }
        }), 201
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Upload failed: {str(e)}'
        }), 500
