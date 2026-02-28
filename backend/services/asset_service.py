"""
Asset Health Monitoring & Predictive Maintenance Service
Manages farm asset lifecycle, health tracking, and AI-powered failure predictions.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, or_, func
from backend.extensions import db
from backend.models import FarmAsset, MaintenanceLog, User
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class AssetService:
    """
    Handles farm asset operations including health monitoring, 
    predictive analysis, and maintenance recommendations.
    """
    
    # Asset health score thresholds
    HEALTH_CRITICAL = 30
    HEALTH_WARNING = 60
    HEALTH_GOOD = 85
    
    # Default maintenance intervals (hours)
    MAINTENANCE_INTERVALS = {
        'tractor': 200,
        'tiller': 150,
        'pump': 100,
        'harvester': 180,
        'sprayer': 120,
        'default': 150
    }
    
    @staticmethod
    def create_asset(user_id: int, asset_data: Dict) -> FarmAsset:
        """
        Register a new farm asset for tracking.
        
        Args:
            user_id: Owner user ID
            asset_data: Asset details
            
        Returns:
            Created FarmAsset object
        """
        try:
            # Generate unique asset ID
            asset_id = f"AST-{datetime.utcnow().strftime('%Y%m%d')}-{user_id}-{FarmAsset.query.count() + 1:04d}"
            
            asset = FarmAsset(
                asset_id=asset_id,
                user_id=user_id,
                asset_type=asset_data.get('asset_type', 'unknown'),
                asset_name=asset_data.get('asset_name', 'Unnamed Asset'),
                manufacturer=asset_data.get('manufacturer'),
                model=asset_data.get('model'),
                serial_number=asset_data.get('serial_number'),
                purchase_date=datetime.fromisoformat(asset_data['purchase_date']) if asset_data.get('purchase_date') else None,
                purchase_price=asset_data.get('purchase_price'),
                health_score=100.0,
                status='ACTIVE',
                alert_threshold_days=asset_data.get('alert_threshold_days', 7)
            )
            
            # Calculate first maintenance due date
            maintenance_interval = AssetService.MAINTENANCE_INTERVALS.get(
                asset_data.get('asset_type', '').lower(),
                AssetService.MAINTENANCE_INTERVALS['default']
            )
            
            if asset.purchase_date:
                asset.next_maintenance_due = asset.purchase_date + timedelta(hours=maintenance_interval)
            
            db.session.add(asset)
            db.session.commit()
            
            logger.info(f"Asset created: {asset_id} for user {user_id}")
            return asset
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating asset: {str(e)}")
            raise
    
    @staticmethod
    def update_telemetry(asset_id: str, telemetry_data: Dict) -> Tuple[FarmAsset, float]:
        """
        Update asset telemetry and recalculate health score.
        
        Args:
            asset_id: Asset identifier
            telemetry_data: Sensor data (runtime, temperature, vibration, etc.)
            
        Returns:
            Tuple of (updated asset, new health score)
        """
        try:
            asset = FarmAsset.query.filter_by(asset_id=asset_id).first()
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Store telemetry
            asset.last_telemetry = json.dumps(telemetry_data)
            
            # Update runtime
            if 'runtime_hours' in telemetry_data:
                asset.total_runtime_hours += telemetry_data['runtime_hours']
            
            # Calculate health score based on telemetry
            health_score = AssetService._calculate_health_score(asset, telemetry_data)
            asset.health_score = health_score
            
            # Check maintenance due
            AssetService._check_maintenance_due(asset)
            
            db.session.commit()
            
            logger.info(f"Telemetry updated for {asset_id}, health: {health_score:.1f}")
            return asset, health_score
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating telemetry for {asset_id}: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_health_score(asset: FarmAsset, telemetry: Dict) -> float:
        """
        Calculate asset health score based on multiple factors.
        
        Scoring factors:
        - Runtime hours vs expected lifespan
        - Sensor anomalies (temperature, vibration, fuel efficiency)
        - Time since last maintenance
        - Historical failure patterns
        """
        score = 100.0
        
        # Factor 1: Runtime degradation (max -30 points)
        if asset.total_runtime_hours > 0:
            expected_lifespan = 5000  # Default hours
            wear_ratio = asset.total_runtime_hours / expected_lifespan
            score -= min(30, wear_ratio * 30)
        
        # Factor 2: Sensor anomalies (max -25 points)
        if 'temperature_c' in telemetry:
            temp = telemetry['temperature_c']
            if temp > 95:  # Overheating
                score -= 15
            elif temp > 85:
                score -= 8
        
        if 'vibration_level' in telemetry:
            vibration = telemetry['vibration_level']
            if vibration > 80:  # High vibration
                score -= 10
            elif vibration > 60:
                score -= 5
        
        if 'fuel_efficiency' in telemetry:
            efficiency = telemetry['fuel_efficiency']
            if efficiency < 60:  # Poor efficiency
                score -= 10
            elif efficiency < 75:
                score -= 5
        
        # Factor 3: Maintenance overdue (max -20 points)
        if asset.next_maintenance_due:
            days_overdue = (datetime.utcnow() - asset.next_maintenance_due).days
            if days_overdue > 0:
                score -= min(20, days_overdue * 2)
        
        # Factor 4: Recent maintenance issues (max -15 points)
        recent_logs = MaintenanceLog.query.filter(
            and_(
                MaintenanceLog.asset_id == asset.id,
                MaintenanceLog.completed_date >= datetime.utcnow() - timedelta(days=90),
                MaintenanceLog.maintenance_type.in_(['REPAIR', 'EMERGENCY'])
            )
        ).count()
        
        score -= min(15, recent_logs * 5)
        
        # Factor 5: Error codes (max -10 points)
        if 'error_codes' in telemetry and telemetry['error_codes']:
            error_count = len(telemetry['error_codes'])
            score -= min(10, error_count * 3)
        
        return max(0.0, min(100.0, score))
    
    @staticmethod
    def _check_maintenance_due(asset: FarmAsset):
        """Check if maintenance is overdue and update status."""
        if asset.next_maintenance_due and datetime.utcnow() > asset.next_maintenance_due:
            days_overdue = (datetime.utcnow() - asset.next_maintenance_due).days
            if days_overdue > 7:
                logger.warning(f"Asset {asset.asset_id} maintenance overdue by {days_overdue} days")
    
    @staticmethod
    def predict_failure_ai(asset_id: str) -> Dict:
        """
        Use Gemini AI to predict potential failures based on asset history.
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Prediction results including days to failure, risk factors, recommendations
        """
        try:
            asset = FarmAsset.query.filter_by(asset_id=asset_id).first()
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Gather asset context
            maintenance_history = MaintenanceLog.query.filter_by(
                asset_id=asset.id
            ).order_by(MaintenanceLog.completed_date.desc()).limit(10).all()
            
            # Build prompt for Gemini
            prompt = AssetService._build_prediction_prompt(asset, maintenance_history)
            
            # Call Gemini AI
            if not GEMINI_API_KEY:
                logger.warning("Gemini API key not configured, using fallback prediction")
                return AssetService._fallback_prediction(asset)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            # Parse AI response
            prediction = AssetService._parse_ai_prediction(response.text, asset)
            
            # Update asset with prediction
            asset.predicted_days_to_failure = prediction['days_to_failure']
            db.session.commit()
            
            logger.info(f"AI prediction for {asset_id}: {prediction['days_to_failure']} days to failure")
            return prediction
            
        except Exception as e:
            logger.error(f"Error in AI prediction for {asset_id}: {str(e)}")
            return AssetService._fallback_prediction(asset)
    
    @staticmethod
    def _build_prediction_prompt(asset: FarmAsset, maintenance_logs: List[MaintenanceLog]) -> str:
        """Build Gemini prompt for failure prediction."""
        
        telemetry = json.loads(asset.last_telemetry) if asset.last_telemetry else {}
        
        prompt = f"""Analyze this farm equipment and predict potential failures:

**Asset Information:**
- Type: {asset.asset_type}
- Model: {asset.manufacturer} {asset.model}
- Age: {(datetime.utcnow() - asset.purchase_date).days if asset.purchase_date else 0} days
- Total Runtime: {asset.total_runtime_hours} hours
- Current Health Score: {asset.health_score:.1f}/100

**Latest Telemetry:**
{json.dumps(telemetry, indent=2)}

**Recent Maintenance History:**
"""
        
        for log in maintenance_logs:
            prompt += f"- {log.maintenance_type}: {log.description} ({log.completed_date.strftime('%Y-%m-%d') if log.completed_date else 'Scheduled'})\n"
        
        prompt += """
**Analysis Required:**
1. Predict the number of days until likely failure or major issue
2. Identify top 3 risk factors
3. Provide specific maintenance recommendations
4. Assess urgency level (LOW, MEDIUM, HIGH, CRITICAL)

**Response Format (JSON):**
{
  "days_to_failure": <number>,
  "confidence": <0-100>,
  "risk_factors": ["factor1", "factor2", "factor3"],
  "recommendations": ["action1", "action2", "action3"],
  "urgency": "LOW|MEDIUM|HIGH|CRITICAL",
  "reasoning": "brief explanation"
}
"""
        return prompt
    
    @staticmethod
    def _parse_ai_prediction(ai_response: str, asset: FarmAsset) -> Dict:
        """Parse Gemini AI response into structured prediction."""
        try:
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                prediction = json.loads(json_str)
            else:
                raise ValueError("No JSON found in AI response")
            
            # Validate and return
            return {
                'asset_id': asset.asset_id,
                'days_to_failure': prediction.get('days_to_failure', 30),
                'confidence': prediction.get('confidence', 50),
                'risk_factors': prediction.get('risk_factors', []),
                'recommendations': prediction.get('recommendations', []),
                'urgency': prediction.get('urgency', 'MEDIUM'),
                'reasoning': prediction.get('reasoning', ''),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing AI prediction: {str(e)}")
            return AssetService._fallback_prediction(asset)
    
    @staticmethod
    def _fallback_prediction(asset: FarmAsset) -> Dict:
        """Fallback prediction when AI is unavailable."""
        # Rule-based prediction
        days = 90  # Default
        
        if asset.health_score < AssetService.HEALTH_CRITICAL:
            days = 7
            urgency = 'CRITICAL'
        elif asset.health_score < AssetService.HEALTH_WARNING:
            days = 30
            urgency = 'HIGH'
        elif asset.health_score < AssetService.HEALTH_GOOD:
            days = 60
            urgency = 'MEDIUM'
        else:
            days = 120
            urgency = 'LOW'
        
        return {
            'asset_id': asset.asset_id,
            'days_to_failure': days,
            'confidence': 60,
            'risk_factors': ['Automated assessment based on health score'],
            'recommendations': ['Schedule routine maintenance', 'Monitor telemetry closely'],
            'urgency': urgency,
            'reasoning': f'Rule-based prediction: Health score {asset.health_score:.1f}',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def log_maintenance(asset_id: str, maintenance_data: Dict) -> MaintenanceLog:
        """
        Record a maintenance activity.
        
        Args:
            asset_id: Asset identifier
            maintenance_data: Maintenance details
            
        Returns:
            Created MaintenanceLog object
        """
        try:
            asset = FarmAsset.query.filter_by(asset_id=asset_id).first()
            if not asset:
                raise ValueError(f"Asset {asset_id} not found")
            
            # Generate log ID
            log_id = f"MAINT-{datetime.utcnow().strftime('%Y%m%d')}-{asset.id}-{MaintenanceLog.query.count() + 1:04d}"
            
            # Record pre-maintenance health
            pre_health = asset.health_score
            
            log = MaintenanceLog(
                log_id=log_id,
                asset_id=asset.id,
                maintenance_type=maintenance_data.get('maintenance_type', 'ROUTINE'),
                description=maintenance_data.get('description', ''),
                parts_replaced=json.dumps(maintenance_data.get('parts_replaced', [])),
                cost=maintenance_data.get('cost', 0.0),
                pre_maintenance_health=pre_health,
                technician_name=maintenance_data.get('technician_name'),
                technician_notes=maintenance_data.get('technician_notes'),
                scheduled_date=datetime.fromisoformat(maintenance_data['scheduled_date']) if maintenance_data.get('scheduled_date') else None,
                status=maintenance_data.get('status', 'SCHEDULED')
            )
            
            db.session.add(log)
            
            # If completed, update asset
            if maintenance_data.get('status') == 'COMPLETED':
                log.completed_date = datetime.utcnow()
                asset.last_maintenance_date = datetime.utcnow()
                
                # Boost health score after maintenance
                health_improvement = maintenance_data.get('health_improvement', 15)
                asset.health_score = min(100.0, asset.health_score + health_improvement)
                log.post_maintenance_health = asset.health_score
                
                # Schedule next maintenance
                maintenance_interval = AssetService.MAINTENANCE_INTERVALS.get(
                    asset.asset_type.lower(),
                    AssetService.MAINTENANCE_INTERVALS['default']
                )
                asset.next_maintenance_due = datetime.utcnow() + timedelta(hours=maintenance_interval)
            
            db.session.commit()
            
            logger.info(f"Maintenance log created: {log_id} for asset {asset_id}")
            return log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error logging maintenance: {str(e)}")
            raise
    
    @staticmethod
    def get_assets_by_user(user_id: int, filters: Optional[Dict] = None) -> List[FarmAsset]:
        """
        Get all assets owned by a user with optional filters.
        
        Args:
            user_id: Owner user ID
            filters: Optional filters (status, asset_type, health_range)
            
        Returns:
            List of FarmAsset objects
        """
        query = FarmAsset.query.filter_by(user_id=user_id)
        
        if filters:
            if 'status' in filters:
                query = query.filter(FarmAsset.status == filters['status'])
            
            if 'asset_type' in filters:
                query = query.filter(FarmAsset.asset_type == filters['asset_type'])
            
            if 'health_min' in filters:
                query = query.filter(FarmAsset.health_score >= filters['health_min'])
            
            if 'health_max' in filters:
                query = query.filter(FarmAsset.health_score <= filters['health_max'])
        
        return query.order_by(FarmAsset.created_at.desc()).all()
    
    @staticmethod
    def get_critical_assets(health_threshold: float = HEALTH_CRITICAL) -> List[FarmAsset]:
        """Get all assets with health below threshold."""
        return FarmAsset.query.filter(
            and_(
                FarmAsset.health_score < health_threshold,
                FarmAsset.status == 'ACTIVE'
            )
        ).order_by(FarmAsset.health_score).all()
    
    @staticmethod
    def get_asset_summary(user_id: int) -> Dict:
        """Get summary statistics for user's assets."""
        assets = FarmAsset.query.filter_by(user_id=user_id).all()
        
        total = len(assets)
        active = sum(1 for a in assets if a.status == 'ACTIVE')
        critical = sum(1 for a in assets if a.health_score < AssetService.HEALTH_CRITICAL)
        warning = sum(1 for a in assets if AssetService.HEALTH_CRITICAL <= a.health_score < AssetService.HEALTH_WARNING)
        
        avg_health = sum(a.health_score for a in assets) / total if total > 0 else 100.0
        
        return {
            'total_assets': total,
            'active': active,
            'critical_health': critical,
            'warning_health': warning,
            'average_health': round(avg_health, 2),
            'maintenance_overdue': sum(1 for a in assets if a.next_maintenance_due and datetime.utcnow() > a.next_maintenance_due)
        }
