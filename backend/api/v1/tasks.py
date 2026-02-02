from flask import Blueprint, jsonify
from auth_utils import token_required

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@token_required
def get_task_status(task_id):
    """Check the status of an async task."""
    try:
        from backend.celery_app import celery_app
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Task is waiting to be processed'
            }
        elif task.state == 'STARTED':
            response = {
                'status': 'processing',
                'message': 'Task is currently being processed'
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'status': 'failed',
                'message': str(task.info)
            }
        else:
            response = {
                'status': task.state,
                'message': 'Unknown state'
            }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
