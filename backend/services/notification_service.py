import os
from datetime import datetime
from flask_mail import Message
from backend.extensions import db, mail, socketio
from backend.models import Notification, User
from backend.utils.logger import logger

class NotificationService:
    @staticmethod
    def create_notification(title, message, notification_type, user_id=None):
        """
        Creates a notification in the database and triggers real-time delivery.
        """
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type
            )
            db.session.add(notification)
            db.session.commit()
            
            # 1. Deliver via WebSocket
            NotificationService.send_websocket_notification(notification)
            
            # 2. Check user preferences for Email/SMS
            if user_id:
                user = User.query.get(user_id)
                if user:
                    if user.email_enabled:
                        NotificationService.send_email_notification(notification, user.email)
                    if user.sms_enabled:
                        NotificationService.send_sms_notification(notification, user.phone)
            
            return notification
        except Exception as e:
            logger.error("Failed to create notification: %s", str(e), exc_info=True)
            db.session.rollback()
            return None

    @staticmethod
    def send_websocket_notification(notification):
        """
        Sends notification via SocketIO.
        """
        try:
            payload = notification.to_dict()
            if notification.user_id:
                # Send to specific user room
                socketio.emit('new_notification', payload, room=f"user_{notification.user_id}")
            else:
                # Broadcast global notification
                socketio.emit('new_notification', payload)
            
            notification.websocket_sent = True
            db.session.commit()
        except Exception as e:
            logger.error("WebSocket notification failed: %s", str(e))

    @staticmethod
    def send_email_notification(notification, email):
        """
        Sends notification via Email.
        """
        try:
            msg = Message(
                subject=f"AgriTech: {notification.title}",
                recipients=[email],
                body=notification.message
            )
            # Use background task for real production
            mail.send(msg)
            
            notification.email_sent = True
            db.session.commit()
        except Exception as e:
            logger.error("Email notification failed: %s", str(e))

    @staticmethod
    def send_sms_notification(notification, phone):
        """
        Skeleton for SMS notification (e.g. using Twilio).
        """
        if not phone:
            return
            
        try:
            # Twilio implementation would go here
            # account_sid = os.environ.get('TWILIO_SID')
            # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            # client = Client(account_sid, auth_token)
            # client.messages.create(body=notification.message, from_='+12345678', to=phone)
            
            logger.info("SMS notification would be sent to %s", phone)
            # notification.sms_sent = True
            # db.session.commit()
        except Exception as e:
            logger.error("SMS notification failed: %s", str(e))

    @staticmethod
    def mark_as_read(notification_id):
        """
        Marks a notification as read.
        """
        notification = Notification.query.get(notification_id)
        if notification:
            notification.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_notifications(user_id, unread_only=False):
        """
        Retrieves notifications for a specific user.
        """
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter(Notification.read_at.is_(None))
        return query.order_by(Notification.sent_at.desc()).all()
