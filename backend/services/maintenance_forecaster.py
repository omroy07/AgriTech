"""
Predictive Maintenance Service — L3-1641
========================================
Analyzes asset telemetry to predict mechanical failures.
"""

from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.iot_maintenance import AssetTelemetry, MaintenancePrediction
from backend.models.farm import FarmAsset
import logging

logger = logging.getLogger(__name__)

class MaintenanceForecaster:
    
    @staticmethod
    def analyze_vibration_anomaly(asset_id: int):
        """
        Detects anomalies in vibration patterns likely indicating bearing wear.
        """
        recent_logs = AssetTelemetry.query.filter_by(asset_id=asset_id).order_by(AssetTelemetry.recorded_at.desc()).limit(10).all()
        if len(recent_logs) < 5:
            return 0.0
            
        avg_vibe = sum(l.vibration_amplitude for l in recent_logs) / len(recent_logs)
        # Simple threshold detection
        if avg_vibe > 8.5:
             return 0.85 # High probability of bearing failure
        return 0.1

    @staticmethod
    def run_inference(asset_id: int):
        """
        Runs the predictive engine for a specific asset.
        """
        asset = FarmAsset.query.get(asset_id)
        if not asset: return
        
        vibe_risk = MaintenanceForecaster.analyze_vibration_anomaly(asset_id)
        
        # Temp risk: > 105C is dangerous
        latest = AssetTelemetry.query.filter_by(asset_id=asset_id).order_by(AssetTelemetry.recorded_at.desc()).first()
        temp_risk = 0.9 if latest and latest.coolant_temp_c > 105 else 0.0
        
        final_prob = max(vibe_risk, temp_risk)
        criticality = 'CRITICAL' if final_prob > 0.7 else 'MEDIUM' if final_prob > 0.3 else 'LOW'
        
        prediction = MaintenancePrediction(
            asset_id=asset_id,
            failure_probability=final_prob,
            estimated_remaining_useful_life_hrs=100 * (1 - final_prob),
            predicted_component_failure="TRACTOR_ENGINE_CORE" if temp_risk > 0.5 else "HYDRAULIC_SYSTEM",
            criticality_level=criticality
        )
        db.session.add(prediction)
        
        if criticality == 'CRITICAL':
            logger.warning(f"ASSET {asset_id} FAILURE IMMINENT. Probability: {final_prob*100:.1f}%")
            
        db.session.commit()
        return prediction
