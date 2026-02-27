from datetime import datetime, timedelta
from backend.extensions import db
from backend.models.weather import WeatherData, AdvisorySubscription
from backend.utils.weather_api_client import WeatherAPIClient
import logging

logger = logging.getLogger(__name__)


class CropAdvisoryService:
    CROP_DATABASE = {
        "Wheat": {
            "optimal_temp_min": 15,
            "optimal_temp_max": 25,
            "optimal_humidity_min": 50,
            "optimal_humidity_max": 70,
            "planting_month": ["October", "November"],
            "harvesting_month": ["March", "April"],
            "water_requirement": "moderate",
            "frost_sensitive": True,
        },
        "Rice": {
            "optimal_temp_min": 20,
            "optimal_temp_max": 35,
            "optimal_humidity_min": 70,
            "optimal_humidity_max": 90,
            "planting_month": ["June", "July"],
            "harvesting_month": ["October", "November"],
            "water_requirement": "high",
            "frost_sensitive": True,
        },
        "Maize": {
            "optimal_temp_min": 18,
            "optimal_temp_max": 30,
            "optimal_humidity_min": 50,
            "optimal_humidity_max": 80,
            "planting_month": ["June", "July"],
            "harvesting_month": ["September", "October"],
            "water_requirement": "moderate",
            "frost_sensitive": False,
        },
        "Cotton": {
            "optimal_temp_min": 21,
            "optimal_temp_max": 30,
            "optimal_humidity_min": 40,
            "optimal_humidity_max": 60,
            "planting_month": ["May", "June"],
            "harvesting_month": ["October", "November"],
            "water_requirement": "low",
            "frost_sensitive": True,
        },
        "Tomato": {
            "optimal_temp_min": 18,
            "optimal_temp_max": 28,
            "optimal_humidity_min": 50,
            "optimal_humidity_max": 70,
            "planting_month": ["January", "February", "July", "August"],
            "harvesting_month": ["April", "May", "October", "November"],
            "water_requirement": "moderate",
            "frost_sensitive": True,
        },
        "Potato": {
            "optimal_temp_min": 15,
            "optimal_temp_max": 22,
            "optimal_humidity_min": 60,
            "optimal_humidity_max": 80,
            "planting_month": ["September", "October"],
            "harvesting_month": ["January", "February"],
            "water_requirement": "moderate",
            "frost_sensitive": False,
        },
        "Sugarcane": {
            "optimal_temp_min": 20,
            "optimal_temp_max": 35,
            "optimal_humidity_min": 60,
            "optimal_humidity_max": 90,
            "planting_month": ["October", "November", "February", "March"],
            "harvesting_month": ["October", "November", "December"],
            "water_requirement": "high",
            "frost_sensitive": False,
        },
        "Groundnut": {
            "optimal_temp_min": 20,
            "optimal_temp_max": 30,
            "optimal_humidity_min": 40,
            "optimal_humidity_max": 60,
            "planting_month": ["June", "July"],
            "harvesting_month": ["October", "November"],
            "water_requirement": "low",
            "frost_sensitive": False,
        },
    }

    @staticmethod
    def get_crop_recommendations(location, soil_type=None):
        weather = WeatherService.get_latest_weather(location)
        if not weather:
            return {"error": "Weather data not available"}

        current_month = datetime.now().strftime("%B")
        recommendations = []

        for crop, requirements in CropAdvisoryService.CROP_DATABASE.items():
            score = 0
            reasons = []

            if (
                weather.temperature >= requirements["optimal_temp_min"]
                and weather.temperature <= requirements["optimal_temp_max"]
            ):
                score += 30
                reasons.append("Temperature suitable")
            else:
                reasons.append("Temperature may not be optimal")

            if (
                weather.humidity >= requirements["optimal_humidity_min"]
                and weather.humidity <= requirements["optimal_humidity_max"]
            ):
                score += 20
                reasons.append("Humidity suitable")
            else:
                reasons.append("Humidity may not be optimal")

            if current_month in requirements["planting_month"]:
                score += 30
                reasons.append("Ideal planting time")
            elif current_month in requirements["harvesting_month"]:
                score += 20
                reasons.append("Harvesting season")

            if soil_type:
                if requirements["water_requirement"] == "high" and soil_type in [
                    "clay",
                    "loam",
                ]:
                    score += 20
                elif requirements["water_requirement"] == "low" and soil_type in [
                    "sandy"
                ]:
                    score += 20
                elif requirements["water_requirement"] == "moderate":
                    score += 10

            if score > 0:
                recommendations.append(
                    {
                        "crop": crop,
                        "score": score,
                        "reasons": reasons,
                        "planting_time": requirements["planting_month"],
                        "harvesting_time": requirements["harvesting_month"],
                        "water_requirement": requirements["water_requirement"],
                    }
                )

        recommendations.sort(key=lambda x: x["score"], reverse=True)

        return {
            "location": location,
            "current_weather": {
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "condition": weather.weather_condition,
            },
            "current_month": current_month,
            "recommendations": recommendations[:5],
        }

    @staticmethod
    def get_planting_alerts(user_id):
        subscriptions = AdvisorySubscription.query.filter_by(
            user_id=user_id, is_active=True
        ).all()
        alerts = []

        current_month = datetime.now().strftime("%B")

        for sub in subscriptions:
            crop_data = CropAdvisoryService.CROP_DATABASE.get(sub.crop_name)
            if not crop_data:
                continue

            if current_month in crop_data["planting_month"]:
                alerts.append(
                    {
                        "type": "PLANTING",
                        "crop": sub.crop_name,
                        "location": sub.location,
                        "message": f"Best time to plant {sub.crop_name} in {sub.location}. Conditions are optimal.",
                        "priority": "HIGH",
                        "action": "Start planting operations",
                    }
                )

            if current_month in crop_data["harvesting_month"]:
                alerts.append(
                    {
                        "type": "HARVESTING",
                        "crop": sub.crop_name,
                        "location": sub.location,
                        "message": f"Harvesting time for {sub.crop_name} in {sub.location}. Prepare for harvest.",
                        "priority": "HIGH",
                        "action": "Prepare harvesting equipment",
                    }
                )

        return alerts

    @staticmethod
    def analyze_climate_patterns(location, days=30):
        threshold = datetime.utcnow() - timedelta(days=days)
        weather_data = (
            WeatherData.query.filter(
                WeatherData.location == location, WeatherData.timestamp >= threshold
            )
            .order_by(WeatherData.timestamp.asc())
            .all()
        )

        if not weather_data:
            return {"error": "Insufficient data for climate analysis"}

        temperatures = [w.temperature for w in weather_data]
        humidities = [w.humidity for w in weather_data]
        rainfall_data = [w.rainfall for w in weather_data]

        total_rainfall = sum(rainfall_data)
        rainy_days = len([r for r in rainfall_data if r > 2.5])

        avg_temp = sum(temperatures) / len(temperatures)
        avg_humidity = sum(humidities) / len(humidities)
        temp_trend = temperatures[-1] - temperatures[0]

        analysis = {
            "location": location,
            "period_days": days,
            "average_temperature": round(avg_temp, 1),
            "average_humidity": round(avg_humidity, 1),
            "total_rainfall": round(total_rainfall, 1),
            "rainy_days": rainy_days,
            "temperature_trend": "Increasing"
            if temp_trend > 2
            else "Decreasing"
            if temp_trend < -2
            else "Stable",
            "temperature_change": round(temp_trend, 1),
        }

        if avg_temp > 30:
            analysis["advisory"] = (
                "High temperatures. Consider heat-resistant crops and increase irrigation."
            )
        elif avg_temp < 15:
            analysis["advisory"] = (
                "Cool conditions. Consider cold-tolerant crops and delay planting."
            )

        if total_rainfall > 100:
            analysis["rainfall_advisory"] = (
                "High rainfall. Monitor for waterlogging and fungal diseases."
            )
        elif total_rainfall < 20:
            analysis["rainfall_advisory"] = (
                "Low rainfall. Plan for additional irrigation."
            )

        return analysis

    @staticmethod
    def get_seasonal_plan(location, crop_name):
        crop_data = CropAdvisoryService.CROP_DATABASE.get(crop_name)
        if not crop_data:
            return {"error": "Crop not found in database"}

        weather = WeatherService.get_latest_weather(location)
        if not weather:
            return {"error": "Weather data not available"}

        current_month = datetime.now().strftime("%B")
        months_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        plan = {
            "crop": crop_name,
            "location": location,
            "current_month": current_month,
            "current_conditions": {
                "temperature": weather.temperature,
                "humidity": weather.humidity,
                "condition": weather.weather_condition,
            },
            "planting_schedule": [],
            "care_timeline": [],
        }

        for month in crop_data["planting_month"]:
            plan["planting_schedule"].append(
                {
                    "month": month,
                    "activity": "Planting",
                    "description": f"Optimal time to plant {crop_name}",
                }
            )

        for month in crop_data["harvesting_month"]:
            plan["planting_schedule"].append(
                {
                    "month": month,
                    "activity": "Harvesting",
                    "description": f"Harvest ready for {crop_name}",
                }
            )

        current_index = months_order.index(current_month)

        for i in range(1, 4):
            future_month = months_order[(current_index + i) % 12]
            if future_month in crop_data["planting_month"]:
                plan["care_timeline"].append(
                    {
                        "month": future_month,
                        "weeks_ahead": i * 4,
                        "activity": "Prepare for planting",
                        "tasks": ["Prepare soil", "Arrange seeds", "Check irrigation"],
                    }
                )
            elif future_month in crop_data["harvesting_month"]:
                plan["care_timeline"].append(
                    {
                        "month": future_month,
                        "weeks_ahead": i * 4,
                        "activity": "Prepare for harvest",
                        "tasks": [
                            "Harvesting equipment ready",
                            "Storage arrangements",
                            "Market preparation",
                        ],
                    }
                )

        return plan


from backend.services.weather_service import WeatherService
