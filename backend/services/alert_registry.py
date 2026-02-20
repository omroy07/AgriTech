import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from backend.extensions import db, mail, socketio
from backend.models import Alert, User, AlertPreference
from backend.utils.logger import logger

class AlertRegistry:
    """
    Centralized registry for managing cross-module alerts.
    Supports asynchronous delivery, priority-based queuing and multi-channel notification.
    """

    @staticmethod
    def register_alert(
        title: str,
        message: str,
        category: str,
        user_id: Optional[int] = None,
        priority: str = 'MEDIUM',
        group_key: Optional[str] = None,
        action_url: Optional[str] = None,
        metadata: Optional[Dict] = None,
        ttl_days: int = 30
    ) -> Optional[Alert]:
        """
        Registers a new alert and initiates the multi-channel delivery process.
        """
        try:
            # 1. Create the alert record
            alert = Alert(
                user_id=user_id,
                title=title,
                message=message,
                category=category,
                priority=priority,
                group_key=group_key,
                action_url=action_url,
                metadata_json=json.dumps(metadata) if metadata else None,
                expires_at=datetime.utcnow() + timedelta(days=ttl_days)
            )
            
            db.session.add(alert)
            db.session.commit()
            
            # 2. Process delivery based on user preferences or global rules
            AlertRegistry._dispatch_alert(alert)
            
            return alert
        except Exception as e:
            logger.error(f"Failed to register alert: {str(e)}", exc_info=True)
            db.session.rollback()
            return None

    @staticmethod
    def _dispatch_alert(alert: Alert):
        """
        Dispatches alert to various channels based on user preferences.
        """
        # If it's a global broadcast, we use default channels
        if not alert.user_id:
            AlertRegistry._deliver_websocket(alert)
            return

        user = User.query.get(alert.user_id)
        if not user:
            return

        # Fetch or create default preferences
        pref = AlertPreference.query.filter_by(
            user_id=user.id, 
            category=alert.category
        ).first()

        # Check if priority meets minimum requirement
        if pref and Alert.get_priority_weight(alert.priority) < Alert.get_priority_weight(pref.min_priority):
            logger.info(f"Alert {alert.id} skipped due to priority threshold for user {user.id}")
            return

        # WebSocket Delivery (Real-time)
        if not pref or pref.websocket_enabled:
            AlertRegistry._deliver_websocket(alert)

        # Email Delivery
        if (not pref or pref.email_enabled) and user.email:
            AlertRegistry._deliver_email(alert, user.email)

        # SMS Delivery
        if pref and pref.sms_enabled and hasattr(user, 'phone') and user.phone:
            AlertRegistry._deliver_sms(alert, user.phone)

    @staticmethod
    def _deliver_websocket(alert: Alert):
        """Delivers real-time alert via WebSockets."""
        try:
            payload = alert.to_dict()
            room = f"user_{alert.user_id}" if alert.user_id else "global_alerts"
            
            socketio.emit('new_alert', payload, room=room)
            
            alert.websocket_delivered = True
            db.session.commit()
            logger.info(f"WebSocket alert {alert.id} delivered to {room}")
        except Exception as e:
            logger.error(f"WebSocket delivery failed for alert {alert.id}: {str(e)}")

    @staticmethod
    def _deliver_email(alert: Alert, email: str):
        """Delivers alert via Email (asynchronous placeholder)."""
        try:
            # In a real app, this would be a Celery task
            # from backend.tasks.email_tasks import send_alert_email
            # send_alert_email.delay(alert.id, email)
            
            # For now, simulate/direct send
            logger.info(f"Email alert {alert.id} queued for {email}")
            alert.email_delivered = True
            db.session.commit()
        except Exception as e:
            logger.error(f"Email delivery failed for alert {alert.id}: {str(e)}")

    @staticmethod
    def _deliver_sms(alert: Alert, phone: str):
        """Delivers alert via SMS (integration placeholder)."""
        try:
            logger.info(f"SMS alert {alert.id} queued for {phone}")
            alert.sms_delivered = True
            db.session.commit()
        except Exception as e:
            logger.error(f"SMS delivery failed for alert {alert.id}: {str(e)}")

    @staticmethod
    def mark_as_read(alert_id: int, user_id: int) -> bool:
        """Marks an alert as read for a specific user."""
        alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
        if alert:
            alert.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_alerts(user_id: int, unread_only: bool = False, limit: int = 50) -> List[Alert]:
        """Retrieves alerts for a user with filtering."""
        query = Alert.query.filter(
            (Alert.user_id == user_id) | (Alert.user_id.is_(None))
        )
        
        if unread_only:
            query = query.filter(Alert.read_at.is_(None))
            
        return query.order_by(Alert.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_alert_summary(user_id: int) -> Dict[str, Any]:
        """
        Generates a statistical summary of alerts for a user.
        Useful for dashboard widgets and mobile push payload optimization.
        """
        total = Alert.query.filter((Alert.user_id == user_id) | (Alert.user_id.is_(None))).count()
        unread = Alert.query.filter(
            ((Alert.user_id == user_id) | (Alert.user_id.is_(None))),
            Alert.read_at.is_(None)
        ).count()
        
        # Priority breakdown
        critical = Alert.query.filter_by(user_id=user_id, priority='CRITICAL', read_at=None).count()
        high = Alert.query.filter_by(user_id=user_id, priority='HIGH', read_at=None).count()
        
        # Category distribution
        categories = db.session.query(
            Alert.category, db.func.count(Alert.id)
        ).filter_by(user_id=user_id).group_by(Alert.category).all()
        
        return {
            'total_alerts': total,
            'unread_count': unread,
            'critical_count': critical,
            'high_count': high,
            'category_distribution': {cat: count for cat, count in categories},
            'has_unread_critical': critical > 0
        }

    @staticmethod
    def aggregate_alerts_by_group(user_id: int, group_key: str) -> List[Alert]:
        """
        Retrieves all related alerts within a group to prevent notification fatigue.
        """
        return Alert.query.filter_by(user_id=user_id, group_key=group_key).all()

    @staticmethod
    def delete_alerts_by_group(user_id: int, group_key: str):
        """
        Bulk deletes alerts in a specific group (e.g. when an issue is resolved).
        """
        try:
            Alert.query.filter_by(user_id=user_id, group_key=group_key).delete()
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    @staticmethod
    def update_preferences(user_id: int, preferences: List[Dict[str, Any]]):
        """Updates user alert preferences across categories."""
        try:
            for p in preferences:
                category = p.get('category')
                if not category:
                    continue
                    
                pref = AlertPreference.query.filter_by(
                    user_id=user_id, 
                    category=category
                ).first()
                
                if not pref:
                    pref = AlertPreference(user_id=user_id, category=category)
                    db.session.add(pref)
                
                pref.email_enabled = p.get('email_enabled', pref.email_enabled)
                pref.sms_enabled = p.get('sms_enabled', pref.sms_enabled)
                pref.push_enabled = p.get('push_enabled', pref.push_enabled)
                pref.websocket_enabled = p.get('websocket_enabled', pref.websocket_enabled)
                pref.min_priority = p.get('min_priority', pref.min_priority)
            
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update preferences: {str(e)}")
            db.session.rollback()
            return False
