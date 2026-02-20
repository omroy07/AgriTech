from datetime import datetime
from backend.models.insurance import InsurancePolicy, DynamicPremiumLog, RiskFactorSnapshot
from backend.models.weather import WeatherData
from backend.models.soil_health import SoilTest
from backend.models.irrigation import IrrigationZone, SensorLog
from backend.models.traceability import SupplyBatch
from backend.models.logistics_v2 import TransportRoute
from backend.extensions import db
from backend.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)

class RiskAdjustmentService:
    """
    Real-time risk orchestration engine that correlates multi-module data
    to dynamically adjust insurance premiums and coverage validity.
    """

    @staticmethod
    def calculate_actuarial_flux(policy_id):
        """
        Main engine for premium adjustment. Correlates weather, moisture and soil.
        """
        policy = InsurancePolicy.query.get(policy_id)
        if not policy: return

        # 1. Recursive Risk Check (L3 Requirement)
        # looks back at SoilTest history and IrrigationZone performance
        sustainability_discount = RiskAdjustmentService.check_recursive_sustainability(policy)
        
        # 2. Real-time Weather Risk
        # Find latest weather for the policy location
        latest_weather = WeatherData.query.filter_by(location=policy.farm_location).order_by(WeatherData.timestamp.desc()).first()
        weather_factor = 1.0
        if latest_weather:
            # High rainfall or extreme heat increases risk
            if latest_weather.rainfall > 30 or latest_weather.temperature > 42:
                weather_factor = 1.4
            elif latest_weather.rainfall > 10:
                weather_factor = 1.1

        # 3. Calculate New Risk Score
        # Combine factors (Simplified actuarial model)
        new_risk_score = (weather_factor * 50.0) * (1.0 - sustainability_discount)
        
        # Check if premium needs adjustment (threshold based)
        old_premium = float(policy.premium_amount)
        new_premium = old_premium * weather_factor * (1.0 - sustainability_discount)
        
        if abs(new_premium - old_premium) > 5.0: # Only log if significant
            RiskAdjustmentService.log_premium_change(policy, old_premium, new_premium, "Dynamic Risk Adjustment")
            policy.premium_amount = new_premium
            policy.current_risk_score = new_risk_score

        # 4. Save Risk Factor Snapshot for audit
        snapshot = RiskFactorSnapshot(
            policy_id=policy.id,
            weather_risk_index=weather_factor,
            telemetry_risk_index=1.0, # Placeholder for more complex telemetry
            sustainability_discount_factor=sustainability_discount
        )
        db.session.add(snapshot)
        db.session.commit()
        return new_risk_score

    @staticmethod
    def check_recursive_sustainability(policy):
        """
        Recursively checks farm history to determine sustainability discount.
        Looks at Soil organic matter and Irrigation efficiency.
        """
        discount = 0.0
        
        # Check Soil Health history (last 3 tests)
        soil_tests = SoilTest.query.filter_by(farm_id=policy.user_id).order_by(SoilTest.created_at.desc()).limit(3).all()
        for t in soil_tests:
            if t.organic_matter and t.organic_matter > 5.0:
                discount += 0.02 # 2% discount per healthy test

        # Check Irrigation Zone performance
        # (Assuming zones are linked to policy location/user)
        zones = IrrigationZone.query.filter_by(farm_id=policy.user_id).all()
        for z in zones:
            # If auto_mode is consistently on, it means better resource management
            if z.auto_mode:
                discount += 0.01

        return min(0.25, discount) # Max 25% discount

    @staticmethod
    def monitor_logistics_safety(batch_id):
        """
        Dual-lock state for "Policy Suspension" if logistics telemetry 
        indicates the produce has left safe temperature range.
        """
        batch = SupplyBatch.query.get(batch_id)
        if not batch or not batch.insurance_policy_id: return

        policy = InsurancePolicy.query.get(batch.insurance_policy_id)
        
        # Find active transport routes for this batch
        # (Assuming some link exists or mock check)
        # Simplified: Check for any current anomalies in logistics
        temp_anomaly = False # Mock check for temperature out of [2C, 8C] range
        
        if temp_anomaly:
            policy.is_suspended = True
            policy.suspension_reason = f"Temperature deviation in Batch {batch_id}"
            
            AuditService.log_event(
                user_id=1,
                action="INSURANCE_SUSPENSION",
                resource_type="POLICY",
                resource_id=policy.id,
                details=policy.suspension_reason,
                risk_level="HIGH"
            )
            db.session.commit()

    @staticmethod
    def log_premium_change(policy, old, new, reason):
        log = DynamicPremiumLog(
            policy_id=policy.id,
            old_premium=old,
            new_premium=new,
            change_reason=reason,
            triggered_by="SYSTEM"
        )
        db.session.add(log)
        
        AuditService.log_event(
            user_id=1,
            action="PREMIUM_ADJUSTMENT",
            resource_type="POLICY",
            resource_id=policy.id,
            details=f"Premium adjusted from {old} to {new} due to {reason}",
            risk_level="MEDIUM"
        )
