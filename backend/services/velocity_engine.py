from datetime import datetime, timedelta
# L3-1560: Predictive Harvest Velocity & Autonomous Futures Hedging
from backend.models.farm import Farm
from backend.models.weather import WeatherData
from backend.models.soil_health import SoilTest
from backend.models.sustainability import CarbonLedger
from backend.extensions import db
import logging

logger = logging.getLogger(__name__)

class VelocityEngine:
    """
    Predictive engine for harvest timing and yield volume.
    Correlates Growing Degree Days (GDD) with moisture and soil flux.
    """

    BASE_TEMP = 10.0 # Base temp for GDD (example for corn/wheat)

    @staticmethod
    def calculate_harvest_readiness(farm_id):
        """
        Calculates the 0-100% readiness index based on cumulative heat units.
        """
        farm = Farm.query.get(farm_id)
        if not farm: return 0.0

        # 1. Fetch recent weather history (last 30 days)
        weather_logs = WeatherData.query.filter(
            WeatherData.location == farm.location,
            WeatherData.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).all()

        if not weather_logs: 
            return farm.harvest_readiness_index # No new data

        # 2. Daily GDD aggregation: Sum( (MaxT + MinT)/2 - BaseT )
        # Simplified: Sum( AvgT - BaseT )
        cumulative_gdd = 0.0
        for log in weather_logs:
            daily_contribution = max(0, (log.temperature or 0) - VelocityEngine.BASE_TEMP)
            cumulative_gdd += daily_contribution

        # 3. Maturity Threshold normalization
        # Imagine 1200 GDD is 100% maturity for this crop
        target_gdd = 1200.0
        readiness = (cumulative_gdd / target_gdd) * 100.0
        readiness = min(100.0, readiness)

        # 4. Adjustment based on moisture (Stressed crops mature faster or fail)
        latest_soil = SoilTest.query.filter_by(farm_id=farm_id).order_by(SoilTest.created_at.desc()).first()
        if latest_soil and latest_soil.organic_matter < 3.0:
            readiness += 5.0 # Accelerated stress maturity

        # 5. Update Farm
        farm.harvest_readiness_index = readiness
        farm.last_velocity_update = datetime.utcnow()
        db.session.commit()

        return readiness

    @staticmethod
    def predict_yield_volume(farm_id):
        """
        Estimates total KG yield based on acreage and soil health.
        """
        farm = Farm.query.get(farm_id)
        if not farm: return 0.0

        # Base yield: 5000 kg per acre
        base_yield_per_acre = 5000.0
        
        # Adjust for soil nutrients
        latest_soil = SoilTest.query.filter_by(farm_id=farm_id).order_by(SoilTest.created_at.desc()).first()
        nutrient_factor = 1.0
        if latest_soil:
            # High NPK and Organic Matter boost yield
            if latest_soil.nitrogen > 50 and latest_soil.organic_matter > 4.0:
                nutrient_factor = 1.2
            elif latest_soil.nitrogen < 20:
                nutrient_factor = 0.8

        predicted = farm.acreage * base_yield_per_acre * nutrient_factor
        farm.predicted_yield_volume = predicted
        db.session.commit()

        return predicted

    @staticmethod
    def calculate_hedge_ratio(farm_id):
        """
        L3 Requirement: Dynamic Hedge Ratio based on Weather Volatility.
        Returns percentage (0.0 - 1.0) of crop to lock in futures.
        """
        # Calculate weather volatility (Std dev of temp/rain in last 7 days)
        # Higher volatility = Lock in MORE now to protect against failure
        # (Simplified: check for extreme weather count)
        extreme_count = WeatherData.query.filter(
            WeatherData.location == "Example", # Link to farm location
            (WeatherData.temperature > 40) | (WeatherData.rainfall > 30)
        ).count()

        if extreme_count > 5:
            return 0.8 # Lock 80% (Risk averse)
        elif extreme_count > 2:
            return 0.5 # Lock 50%
        else:
            return 0.3 # Lock 30% (Betting on spot price)
