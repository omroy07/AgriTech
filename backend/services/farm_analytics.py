from backend.models.farm import Farm, FarmAsset
from backend.models.traceability import SupplyBatch
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class FarmAnalytics:
    @staticmethod
    def get_farm_kpis(farm_id):
        """
        Calculate key performance indicators for a specific farm.
        Includes total asset value, production volume, and worker stats.
        """
        farm = Farm.query.get(farm_id)
        if not farm:
            return None
            
        # 1. Total Asset Value
        total_assets = db.session.query(db.func.sum(FarmAsset.current_valuation))\
            .filter(FarmAsset.farm_id == farm_id).scalar() or 0
            
        # 2. Production Volume (from SupplyBatch)
        # Assuming SupplyBatch is linked to the farm owner/location
        # In a more complex schema, SupplyBatch would have a farm_id
        # For now, let's just count batches handled by members of this farm
        production_volume = db.session.query(db.func.sum(SupplyBatch.quantity))\
            .filter(SupplyBatch.farm_location == farm.location).scalar() or 0
            
        # 3. Asset Health Distribution
        condition_counts = db.session.query(FarmAsset.condition, db.func.count(FarmAsset.id))\
            .filter(FarmAsset.farm_id == farm_id)\
            .group_by(FarmAsset.condition).all()
            
        return {
            'farm_name': farm.name,
            'total_asset_value': float(total_assets),
            'production_volume': float(production_volume),
            'asset_health': dict(condition_counts),
            'acreage': farm.acreage
        }

    @staticmethod
    def calculate_depreciation(farm_id, annual_rate=0.15):
        """
        Simulate asset depreciation (for accounting/valuation).
        Reduces valuation by a percentage of total value per year.
        """
        assets = FarmAsset.query.filter_by(farm_id=farm_id).all()
        for asset in assets:
            if asset.purchase_value:
                # Simple linear monthly depreciation simulation for demo
                # Real logic would use purchase_date
                asset.current_valuation *= (1 - annual_rate / 12)
        
        db.session.commit()
        return True
