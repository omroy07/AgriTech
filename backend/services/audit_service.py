import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from flask import request, g
from backend.extensions import db
from backend.models import AuditLog, UserSession, User
from backend.utils.logger import logger

class AuditService:
    """
    Centralized service for recording and analyzing user activity logs.
    Includes threat detection and session management logic.
    """

    @staticmethod
    def log_action(
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        meta_data: Optional[Dict] = None,
        risk_level: str = 'LOW'
    ) -> AuditLog:
        """
        Extracts request context and persists an audit entry.
        """
        try:
            # Capture request context if available
            ip_address = request.remote_addr if request else None
            user_agent = request.user_agent.string if request and request.user_agent else None
            method = request.method if request else None
            url = request.url if request else None
            
            # Use g.user if user_id is not provided
            if not user_id and hasattr(g, 'user') and g.user:
                user_id = g.user.id

            # Threat detection logic
            is_threat, threat_reason = AuditService._detect_threat(action, user_id, ip_address, url)
            if is_threat:
                risk_level = 'CRITICAL'
                if not meta_data: meta_data = {}
                meta_data['threat_reason'] = threat_reason

            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                ip_address=ip_address,
                user_agent=user_agent,
                method=method,
                url=url,
                risk_level=risk_level,
                threat_flag=is_threat,
                meta_data=json.dumps(meta_data) if meta_data else None
            )

            db.session.add(log)
            db.session.commit()
            
            if is_threat:
                logger.warning(f"SECURITY THREAT DETECTED: {threat_reason} | Action: {action} | User: {user_id}")
                # Potentially trigger an alert via CUNAR here
                from backend.services.alert_registry import AlertRegistry
                AlertRegistry.register_alert(
                    title="Security Threat Detected",
                    message=f"Suspicious activity: {threat_reason} for action '{action}'",
                    category="SECURITY",
                    priority="CRITICAL",
                    user_id=None # Admin broadcast
                )

            return log
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}", exc_info=True)
            db.session.rollback()
            return None

    @staticmethod
    def _detect_threat(action: str, user_id: Optional[int], ip: str, url: str) -> (bool, str):
        """
        Internal heuristic for detecting suspicious patterns.
        """
        # 1. Check for rapid sequence of sensitive actions
        if action in ['DELETE_USER', 'EXPORT_DATA', 'CHANGE_PERMISSIONS']:
            recent_count = AuditLog.query.filter(
                AuditLog.user_id == user_id,
                AuditLog.action == action,
                AuditLog.timestamp >= datetime.utcnow() - timedelta(minutes=5)
            ).count()
            if recent_count > 5:
                return True, "Potential automated bulk sensitive operation"

        # 2. Check for SQL Injection patterns in URL (basic)
        if url and any(pattern in url.lower() for pattern in ["select%20", "union%20all", "drop%20table"]):
            return True, "SQL Injection pattern detected in URL"

        # 3. Check for multiple failed logins from same IP
        if action == 'LOGIN_FAILED':
            recent_fails = AuditLog.query.filter(
                AuditLog.ip_address == ip,
                AuditLog.action == 'LOGIN_FAILED',
                AuditLog.timestamp >= datetime.utcnow() - timedelta(minutes=15)
            ).count()
            if recent_fails > 10:
                return True, "Brute force login attempt suspected"

        return False, ""

    @staticmethod
    def start_session(user_id: int, token: str) -> UserSession:
        """Records the start of a new user session."""
        try:
            # Inactive previous sessions
            UserSession.query.filter_by(user_id=user_id, is_active=True).update({'is_active': False, 'logout_time': datetime.utcnow()})
            
            session = UserSession(
                user_id=user_id,
                session_token=token,
                ip_address=request.remote_addr if request else None,
                user_agent=request.user_agent.string if request and request.user_agent else None
            )
            db.session.add(session)
            db.session.commit()
            return session
        except Exception as e:
            logger.error(f"Failed to start session: {str(e)}")
            return None

    @staticmethod
    def update_session_activity(token: str):
        """Updates the last activity timestamp for a session."""
        session = UserSession.query.filter_by(session_token=token).first()
        if session:
            session.last_activity = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def end_session(token: str):
        """Marks a session as terminated."""
        session = UserSession.query.filter_by(session_token=token).first()
        if session:
            session.is_active = False
            session.logout_time = datetime.utcnow()
            db.session.commit()

    @staticmethod
    def get_logs(filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """Query audit logs with various filters."""
        query = AuditLog.query
        
        if filters.get('user_id'):
            query = query.filter_by(user_id=filters['user_id'])
        if filters.get('action'):
            query = query.filter(AuditLog.action.ilike(f"%{filters['action']}%"))
        if filters.get('risk_level'):
            query = query.filter_by(risk_level=filters['risk_level'])
        if filters.get('threat_only'):
            query = query.filter_by(threat_flag=True)
        if filters.get('start_date'):
            query = query.filter(AuditLog.timestamp >= datetime.fromisoformat(filters['start_date']))
            
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset).all()

    @staticmethod
    def analyze_user_behavior(user_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Performs behavioral analysis to identify anomalies.
        Compare current activity against historical norms.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        logs = AuditLog.query.filter(AuditLog.user_id == user_id, AuditLog.timestamp >= cutoff).all()
        
        if not logs:
            return {"status": "insufficient_data"}

        # 1. Action frequencies
        action_counts = {}
        for log in logs:
            action_counts[log.action] = action_counts.get(log.action, 0) + 1
            
        # 2. Temporal analysis (active hours)
        active_hours = [log.timestamp.hour for log in logs]
        avg_hour = sum(active_hours) / len(active_hours)
        
        # 3. IP diversity
        unique_ips = set(log.ip_address for log in logs if log.ip_address)
        
        # 4. Security score calculation
        threat_count = sum(1 for log in logs if log.threat_flag)
        high_risk_count = sum(1 for log in logs if log.risk_level in ['HIGH', 'CRITICAL'])
        
        security_score = 100 - (threat_count * 10) - (high_risk_count * 5) - (len(unique_ips) * 2)
        
        return {
            "user_id": user_id,
            "analysis_period_days": days,
            "total_actions": len(logs),
            "top_actions": sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "ip_count": len(unique_ips),
            "security_score": max(0, security_score),
            "avg_active_hour": round(avg_hour, 1),
            "anomaly_detected": security_score < 40 or len(unique_ips) > 5
        }

    @staticmethod
    def generate_security_report(hours: int = 24) -> Dict[str, Any]:
        """
        Generates a comprehensive system-wide security forensic report.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        total_logs = AuditLog.query.filter(AuditLog.timestamp >= cutoff).count()
        threats = AuditLog.query.filter(AuditLog.timestamp >= cutoff, AuditLog.threat_flag == True).all()
        
        # Identity threats grouped by IP
        ip_threats = {}
        for t in threats:
            if t.ip_address:
                if t.ip_address not in ip_threats: ip_threats[t.ip_address] = []
                ip_threats[t.ip_address].append(t.action)

        # Flagged sensitive resources
        sensitive_ops = AuditLog.query.filter(
            AuditLog.timestamp >= cutoff,
            AuditLog.action.in_(['DELETE_USER', 'DATABASE_WIPE', 'CONFIG_CHANGE', 'PERMISSION_GRANT'])
        ).all()

        return {
            "report_timestamp": datetime.utcnow().isoformat(),
            "period_hours": hours,
            "total_interactions": total_logs,
            "threat_count": len(threats),
            "high_risk_source_ips": {ip: len(actions) for ip, actions in ip_threats.items() if len(actions) > 2},
            "sensitive_operations_performed": [s.to_dict() for s in sensitive_ops],
            "system_health_status": "CRITICAL" if len(threats) > 50 else "WARNING" if len(threats) > 10 else "SECURE"
        }

    @staticmethod
    def detect_session_hijacking(user_id: int, current_ip: str, current_ua: str) -> bool:
        """
        Checks for session hijacking indicators like sudden IP or UA switches.
        """
        active_session = UserSession.query.filter_by(user_id=user_id, is_active=True).first()
        if not active_session:
            return False
            
        # If IP changed significantly (e.g. different subnet) or UA changed
        if active_session.ip_address != current_ip or active_session.user_agent != current_ua:
            AuditService.log_action(
                action="SESSION_HIJACK_SUSPICION",
                user_id=user_id,
                risk_level='CRITICAL',
                meta_data={
                    "old_ip": active_session.ip_address,
                    "new_ip": current_ip,
                    "old_ua": active_session.user_agent,
                    "new_ua": current_ua
                }
            )
            return True
        return False

    @staticmethod
    def forensic_search(criteria: Dict[str, Any]) -> List[AuditLog]:
        """
        Performs high-complexity multi-vector forensic searches.
        Used for deeper security investigation.
        """
        query = AuditLog.query
        
        # 1. IP range search (subnet matching)
        if criteria.get('ip_prefix'):
            query = query.filter(AuditLog.ip_address.like(f"{criteria['ip_prefix']}%"))
            
        # 2. Risk range search
        if criteria.get('min_risk'):
            risk_map = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2, 'CRITICAL': 3}
            # This would require a custom hybrid property or SQL mapping
            # For now simplified filtering
            if criteria['min_risk'] == 'CRITICAL':
                query = query.filter_by(risk_level='CRITICAL')
            elif criteria['min_risk'] == 'HIGH':
                query = query.filter(AuditLog.risk_level.in_(['HIGH', 'CRITICAL']))

        # 3. Payload content search (Searching inside JSON strings)
        if criteria.get('payload_query'):
            query = query.filter(
                (AuditLog.new_values.ilike(f"%{criteria['payload_query']}%")) |
                (AuditLog.meta_data.ilike(f"%{criteria['payload_query']}%"))
            )

        # 4. Temporal correlation (Actions happening within seconds of each other)
        if criteria.get('correlation_token'):
            # Logical grouping by some token in meta_data
            query = query.filter(AuditLog.meta_data.ilike(f"%{criteria['correlation_token']}%"))

        return query.order_by(AuditLog.timestamp.desc()).limit(200).all()

    @staticmethod
    def export_audit_trail(user_id: Optional[int] = None, format: str = 'json') -> str:
        """
        Generates an encrypted or formatted audit trail for compliance.
        Returns a string representation (JSON or pseudo-CSV).
        """
        logs = AuditLog.query.filter_by(user_id=user_id).all() if user_id else AuditLog.query.all()
        
        if format == 'json':
            return json.dumps([log.to_dict() for log in logs], indent=2)
            
        elif format == 'csv':
            # Pseudo-CSV construction
            header = "id,timestamp,user_id,action,risk_level,ip_address\n"
            rows = [f"{l.id},{l.timestamp},{l.user_id},{l.action},{l.risk_level},{l.ip_address}" for l in logs]
            return header + "\n".join(rows)
            
        return "Unsupported format"
