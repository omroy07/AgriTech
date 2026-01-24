from flask import Blueprint, request, jsonify, send_file
from backend.services.file_service import FileService
from backend.models import File
from backend.extensions import db

files_bp = Blueprint('files', __name__)

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file."""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id', type=int)
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400
    
    file_record, error = FileService.save_file(file, user_id=user_id)
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 400
    
    return jsonify({
        'status': 'success',
        'message': 'File uploaded successfully',
        'file': file_record.to_dict(),
        'download_url': FileService.get_file_url(file_record)
    }), 201

@files_bp.route('/<int:file_id>', methods=['GET'])
def get_file_info(file_id):
    """Get metadata and download URL for a file."""
    file_record = File.query.get_or_404(file_id)
    return jsonify({
        'status': 'success',
        'file': file_record.to_dict(),
        'download_url': FileService.get_file_url(file_record)
    })

@files_bp.route('/download/<int:file_id>', methods=['GET'])
def download_local_file(file_id):
    """Download a locally stored file."""
    file_record = File.query.get_or_404(file_id)
    if file_record.storage_type != 'local':
        return jsonify({'status': 'error', 'message': 'File is not stored locally'}), 400
    
    return send_file(
        file_record.file_path,
        mimetype=file_record.file_type,
        as_attachment=True,
        download_name=file_record.original_name
    )

@files_bp.route('/user/<int:user_id>', methods=['GET'])
def list_user_files(user_id):
    """List all files uploaded by a user."""
    files = File.query.filter_by(user_id=user_id).all()
    return jsonify({
        'status': 'success',
        'files': [f.to_dict() for f in files]
    })
