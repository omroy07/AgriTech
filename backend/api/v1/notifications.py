from flask import Blueprint, jsonify, request
from backend.services.notification_service import NotificationService
from backend.models import Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    """Fetch notifications for a user."""
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'status': 'error', 'message': 'user_id is required'}), 400
    
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notifications = NotificationService.get_user_notifications(user_id, unread_only)
    
    return jsonify({
        'status': 'success',
        'notifications': [n.to_dict() for n in notifications]
    })

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
def mark_read(notification_id):
    """Mark a notification as read."""
    success = NotificationService.mark_as_read(notification_id)
    if success:
        return jsonify({'status': 'success', 'message': 'Notification marked as read'})
    return jsonify({'status': 'error', 'message': 'Notification not found'}), 404

@notifications_bp.route('/test', methods=['POST'])
def test_notification():
    """Endpoint for testing notifications."""
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title', 'Test Notification')
    message = data.get('message', 'This is a test notification from AgriTech')
    n_type = data.get('type', 'system')
    
    notification = NotificationService.create_notification(title, message, n_type, user_id)
    if notification:
        return jsonify({'status': 'success', 'notification': notification.to_dict()})
    return jsonify({'status': 'error', 'message': 'Failed to create notification'}), 500
