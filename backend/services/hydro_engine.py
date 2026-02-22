from backend.models.irrigation import AquiferLevel, WaterRightsQuota, IrrigationZone
from backend.models.sustainability import SustainabilityScore
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class HydroEngine:
    """
    Subsurface Water Quota & Regional Aquifer Management Engine (L3-1605).
    """

    @staticmethod
    def calculate_regional_depletion(aquifer_id):
        """
        Aggregates usage across all farms in a geo-zone to calculate depletion.
        """
        aquifer = AquiferLevel.query.get(aquifer_id)
        if not aquifer:
            return 0.0

        quotas = WaterRightsQuota.query.filter_by(aquifer_id=aquifer_id).all()
        total_used = sum(q.used_quota_liters for q in quotas)
        
        # Simple depletion model: 1cm drop for every 1M liters withdrawn (Simulation)
        depletion_meters = total_used / 1_000_000_000 # Scaling factor
        
        aquifer.current_depth_meters -= depletion_meters
        aquifer.depletion_rate = depletion_meters / 0.25 # Quarterly rate simulation
        
        db.session.commit()
        return aquifer.current_depth_meters

    @staticmethod
    def validate_quota_trade(initiator_farm_id, responder_farm_id):
        """
        Strict Geo-Fencing Check (L3-1605):
        Refuses BarterTransaction for water quotas if farms drawing from different aquifers.
        """
        initiator_quota = WaterRightsQuota.query.filter_by(farm_id=initiator_farm_id).first()
        responder_quota = WaterRightsQuota.query.filter_by(farm_id=responder_farm_id).first()

        if not initiator_quota or not responder_quota:
            return False, "One or both farms do not have registered water rights quotas."

        if initiator_quota.aquifer_id != responder_quota.aquifer_id:
            logger.warning(f"Hydro-Lock: Blocked trade between farm {initiator_farm_id} and {responder_farm_id} due to Aquifer mismatch.")
            return False, "Geo-Fencing Violation: Water rights cannot be traded across different aquifer regions."

        return True, "Aquifer check passed."

    @staticmethod
    def update_sustainability_metrics(farm_id):
        """
        Ties SustainabilityScore to water quota utilization.
        """
        quota = WaterRightsQuota.query.filter_by(farm_id=farm_id).first()
        score = SustainabilityScore.query.filter_by(farm_id=farm_id).first()
        
        if quota and score:
            ratio = quota.used_quota_liters / quota.total_quota_liters
            score.water_quota_utilization_ratio = ratio
            
            # Heavy penalty if nearing quota
            if ratio > 0.9:
                score.overall_rating = max(0, score.overall_rating - 15.0)
                
            db.session.commit()
            return ratio
        return 0.0
