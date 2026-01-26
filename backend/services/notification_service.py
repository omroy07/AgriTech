from datetime import datetime
from backend.extensions import db, socketio
from backend.models import Notification

class NotificationService:
    @staticmethod
    def create_notification(title, message, notification_type, user_id=None):
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type
            )
            db.session.add(notification)
            db.session.commit()
            
            # Emit via SocketIO if needed
            if user_id:
                socketio.emit('new_notification', notification.to_dict(), room=f"user_{user_id}")
            else:
                socketio.emit('new_notification', notification.to_dict())
                
            return notification
        except Exception as e:
            db.session.rollback()
            return None
