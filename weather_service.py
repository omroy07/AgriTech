"""
Weather Service Module
Provides weather data processing and agricultural advisories
for the AgriTech platform
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import math


class WeatherService:
    """Service class for weather-related operations"""
    
    # Weather condition mappings
    WEATHER_CONDITIONS = {
        "clear": {"icon": "☀️", "description": "Clear sky", "farming_impact": "ideal"},
        "partly_cloudy": {"icon": "⛅", "description": "Partly cloudy", "farming_impact": "good"},
        "cloudy": {"icon": "☁️", "description": "Cloudy", "farming_impact": "good"},
        "overcast": {"icon": "🌥️", "description": "Overcast", "farming_impact": "moderate"},
        "light_rain": {"icon": "🌦️", "description": "Light rain", "farming_impact": "caution"},
        "moderate_rain": {"icon": "🌧️", "description": "Moderate rain", "farming_impact": "delay"},
        "heavy_rain": {"icon": "⛈️", "description": "Heavy rain", "farming_impact": "avoid"},
        "thunderstorm": {"icon": "🌩️", "description": "Thunderstorm", "farming_impact": "danger"},
        "drizzle": {"icon": "🌧️", "description": "Drizzle", "farming_impact": "caution"},
        "fog": {"icon": "🌫️", "description": "Fog", "farming_impact": "delay"},
        "haze": {"icon": "😶‍🌫️", "description": "Haze", "farming_impact": "caution"},
        "snow": {"icon": "❄️", "description": "Snow", "farming_impact": "danger"},
        "windy": {"icon": "💨", "description": "Windy", "farming_impact": "caution"}
    }
    
    # Crop-specific weather sensitivities
    CROP_WEATHER_SENSITIVITY = {
        "rice": {
            "optimal_temp": (25, 35),
            "critical_low_temp": 15,
            "critical_high_temp": 42,
            "drought_sensitive": False,
            "waterlogging_tolerant": True,
            "frost_sensitive": True
        },
        "wheat": {
            "optimal_temp": (15, 25),
            "critical_low_temp": 5,
            "critical_high_temp": 35,
            "drought_sensitive": True,
            "waterlogging_tolerant": False,
            "frost_sensitive": False
        },
        "maize": {
            "optimal_temp": (21, 30),
            "critical_low_temp": 10,
            "critical_high_temp": 40,
            "drought_sensitive": True,
            "waterlogging_tolerant": False,
            "frost_sensitive": True
        },
        "tomato": {
            "optimal_temp": (20, 28),
            "critical_low_temp": 10,
            "critical_high_temp": 35,
            "drought_sensitive": True,
            "waterlogging_tolerant": False,
            "frost_sensitive": True
        },
        "potato": {
            "optimal_temp": (15, 22),
            "critical_low_temp": 5,
            "critical_high_temp": 30,
            "drought_sensitive": True,
            "waterlogging_tolerant": False,
            "frost_sensitive": True
        }
    }
    
    def __init__(self):
        self.forecast_cache = {}
        self.cache_expiry = timedelta(hours=1)
    
    def analyze_weather_for_farming(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        rainfall: float,
        condition: str = "clear"
    ) -> Dict:
        """
        Comprehensive weather analysis for farming operations
        
        Args:
            temperature: Temperature in Celsius
            humidity: Relative humidity percentage
            wind_speed: Wind speed in km/h
            rainfall: Rainfall in mm
            condition: Weather condition string
        
        Returns:
            Detailed analysis with recommendations
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "weather_summary": self._get_weather_summary(temperature, humidity, rainfall, condition),
            "farming_conditions": self._assess_farming_conditions(
                temperature, humidity, wind_speed, rainfall
            ),
            "field_operations": self._get_operation_advisories(
                temperature, humidity, wind_speed, rainfall, condition
            ),
            "spray_conditions": self._assess_spray_conditions(
                temperature, humidity, wind_speed, rainfall
            ),
            "irrigation_advice": self._get_irrigation_advice(
                temperature, humidity, rainfall
            ),
            "disease_risk": self._calculate_disease_pressure(
                temperature, humidity, rainfall
            ),
            "pest_risk": self._calculate_pest_pressure(
                temperature, humidity
            ),
            "alerts": self._generate_weather_alerts(
                temperature, humidity, wind_speed, rainfall, condition
            )
        }
        
        return analysis
    
    def _get_weather_summary(
        self,
        temperature: float,
        humidity: float,
        rainfall: float,
        condition: str
    ) -> Dict:
        """Generate weather summary"""
        condition_info = self.WEATHER_CONDITIONS.get(
            condition,
            {"icon": "🌡️", "description": condition, "farming_impact": "unknown"}
        )
        
        return {
            "condition": condition,
            "icon": condition_info["icon"],
            "description": condition_info["description"],
            "temperature": {
                "value": temperature,
                "unit": "°C",
                "feel": self._calculate_feels_like(temperature, humidity),
                "category": self._categorize_temperature(temperature)
            },
            "humidity": {
                "value": humidity,
                "unit": "%",
                "category": self._categorize_humidity(humidity)
            },
            "rainfall": {
                "value": rainfall,
                "unit": "mm",
                "category": self._categorize_rainfall(rainfall)
            },
            "overall_farming_impact": condition_info["farming_impact"]
        }
    
    def _assess_farming_conditions(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        rainfall: float
    ) -> Dict:
        """Assess overall farming conditions"""
        score = 100  # Start with perfect score
        issues = []
        
        # Temperature assessment
        if temperature < 10 or temperature > 40:
            score -= 30
            issues.append("Extreme temperature - limit field exposure")
        elif temperature < 15 or temperature > 35:
            score -= 15
            issues.append("Sub-optimal temperature for most crops")
        
        # Humidity assessment
        if humidity > 90:
            score -= 20
            issues.append("Very high humidity - disease risk elevated")
        elif humidity < 30:
            score -= 15
            issues.append("Low humidity - increase irrigation monitoring")
        
        # Wind assessment
        if wind_speed > 40:
            score -= 25
            issues.append("High winds - avoid spraying and outdoor work")
        elif wind_speed > 25:
            score -= 10
            issues.append("Moderate winds - spray with caution")
        
        # Rainfall assessment
        if rainfall > 50:
            score -= 30
            issues.append("Heavy rainfall - postpone field operations")
        elif rainfall > 20:
            score -= 15
            issues.append("Moderate rainfall - check field conditions before work")
        
        # Determine condition rating
        if score >= 80:
            rating = "excellent"
            color = "green"
        elif score >= 60:
            rating = "good"
            color = "lightgreen"
        elif score >= 40:
            rating = "fair"
            color = "yellow"
        elif score >= 20:
            rating = "poor"
            color = "orange"
        else:
            rating = "unsuitable"
            color = "red"
        
        return {
            "score": max(0, score),
            "rating": rating,
            "color": color,
            "issues": issues,
            "recommendation": self._get_general_recommendation(score, issues)
        }
    
    def _get_operation_advisories(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        rainfall: float,
        condition: str
    ) -> Dict:
        """Get advisories for specific farming operations"""
        operations = {}
        
        # Plowing/Tilling
        if rainfall < 5 and wind_speed < 30:
            operations["plowing"] = {
                "suitable": True,
                "score": 90 if humidity > 40 else 70,
                "note": "Good conditions for soil preparation"
            }
        else:
            operations["plowing"] = {
                "suitable": False,
                "score": 30,
                "note": "Soil too wet or windy for plowing"
            }
        
        # Sowing/Planting
        if 15 <= temperature <= 35 and rainfall < 10 and humidity >= 40:
            operations["sowing"] = {
                "suitable": True,
                "score": 85,
                "note": "Favorable conditions for sowing"
            }
        else:
            operations["sowing"] = {
                "suitable": rainfall < 20 and temperature > 10,
                "score": 50 if rainfall < 20 else 20,
                "note": "Check soil moisture before sowing"
            }
        
        # Harvesting
        if rainfall < 5 and humidity < 70:
            operations["harvesting"] = {
                "suitable": True,
                "score": 95,
                "note": "Excellent conditions for harvesting"
            }
        elif rainfall < 10:
            operations["harvesting"] = {
                "suitable": True,
                "score": 70,
                "note": "Harvest possible, monitor conditions"
            }
        else:
            operations["harvesting"] = {
                "suitable": False,
                "score": 20,
                "note": "Too wet for harvesting - risk of crop damage"
            }
        
        # Fertilizer Application
        if rainfall > 30:
            operations["fertilizer"] = {
                "suitable": False,
                "score": 10,
                "note": "Heavy rain will wash away fertilizer"
            }
        elif rainfall > 5:
            operations["fertilizer"] = {
                "suitable": True,
                "score": 70,
                "note": "Light rain helps fertilizer absorption"
            }
        else:
            operations["fertilizer"] = {
                "suitable": True,
                "score": 85,
                "note": "Irrigate after application if no rain expected"
            }
        
        # Irrigation
        if rainfall > 20:
            operations["irrigation"] = {
                "suitable": False,
                "score": 20,
                "note": "Natural rainfall sufficient - skip irrigation"
            }
        elif rainfall > 5:
            operations["irrigation"] = {
                "suitable": False,
                "score": 40,
                "note": "Reduce irrigation quantity"
            }
        else:
            operations["irrigation"] = {
                "suitable": True,
                "score": 90,
                "note": "Irrigation recommended based on crop needs"
            }
        
        return operations
    
    def _assess_spray_conditions(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        rainfall: float
    ) -> Dict:
        """Assess conditions for pesticide/herbicide spraying"""
        spray_score = 100
        issues = []
        recommendations = []
        
        # Wind check (most critical)
        if wind_speed > 15:
            spray_score -= 40
            issues.append(f"Wind speed {wind_speed} km/h - spray drift risk")
            recommendations.append("Wait for wind to calm below 15 km/h")
        elif wind_speed > 10:
            spray_score -= 15
            issues.append("Moderate wind - use low drift nozzles")
        
        # Rainfall check
        if rainfall > 0:
            spray_score -= 30
            issues.append("Rain will wash off spray")
            recommendations.append("Wait for dry conditions")
        
        # Temperature check
        if temperature > 35:
            spray_score -= 25
            issues.append("High temperature - rapid evaporation")
            recommendations.append("Spray in early morning or late evening")
        elif temperature < 10:
            spray_score -= 20
            issues.append("Low temperature - reduced efficacy")
        
        # Humidity check
        if humidity < 40:
            spray_score -= 15
            issues.append("Low humidity - increased evaporation")
            recommendations.append("Add adjuvants to improve coverage")
        elif humidity > 85:
            spray_score -= 10
            issues.append("High humidity - slow drying")
        
        # Determine suitability
        if spray_score >= 70:
            suitable = True
            window = "Good spray window"
        elif spray_score >= 50:
            suitable = True
            window = "Marginal spray window - proceed with caution"
        else:
            suitable = False
            window = "Poor spray conditions - postpone application"
        
        # Best spray time recommendation
        best_time = "early morning (6-9 AM)" if temperature > 25 else "late morning (9-11 AM)"
        
        return {
            "suitable": suitable,
            "score": max(0, spray_score),
            "window_assessment": window,
            "issues": issues,
            "recommendations": recommendations,
            "best_spray_time": best_time,
            "droplet_size_recommendation": "medium" if wind_speed < 10 else "coarse"
        }
    
    def _get_irrigation_advice(
        self,
        temperature: float,
        humidity: float,
        rainfall: float
    ) -> Dict:
        """Get irrigation advice based on weather"""
        # Calculate evapotranspiration estimate (simplified Penman approximation)
        # ET = 0.0023 * (T + 17.8) * (Tmax - Tmin)^0.5 * Ra
        et_estimate = 0.0023 * (temperature + 17.8) * math.sqrt(max(1, temperature * 0.3)) * 10
        
        # Adjust for humidity
        et_adjusted = et_estimate * (1 - (humidity / 200))
        
        # Account for rainfall
        net_water_loss = max(0, et_adjusted - rainfall)
        
        if rainfall > 30:
            advice = "Skip irrigation - soil saturated from rainfall"
            irrigation_needed = False
            reduction = 100
        elif rainfall > 15:
            advice = "Reduce irrigation by 50-70%"
            irrigation_needed = True
            reduction = 60
        elif rainfall > 5:
            advice = "Reduce irrigation by 20-30%"
            irrigation_needed = True
            reduction = 25
        elif temperature > 35 and humidity < 50:
            advice = "Increase irrigation frequency - high evaporation conditions"
            irrigation_needed = True
            reduction = -20  # Negative means increase
        else:
            advice = "Normal irrigation schedule"
            irrigation_needed = True
            reduction = 0
        
        return {
            "irrigation_needed": irrigation_needed,
            "advice": advice,
            "estimated_et_mm": round(et_adjusted, 2),
            "net_water_loss_mm": round(net_water_loss, 2),
            "adjustment_percentage": reduction,
            "best_time": "early morning (5-7 AM) or evening (6-8 PM)",
            "tips": [
                "Check soil moisture at 6-inch depth before irrigation",
                "Use drip irrigation for water efficiency",
                "Mulching reduces evaporation by 20-30%"
            ]
        }
    
    def _calculate_disease_pressure(
        self,
        temperature: float,
        humidity: float,
        rainfall: float
    ) -> Dict:
        """Calculate disease pressure based on weather conditions"""
        diseases = []
        overall_risk = 0
        
        # Fungal diseases (favor warm + humid)
        if humidity > 80 and 18 <= temperature <= 28:
            fungal_risk = min(100, (humidity - 70) * 2 + (rainfall * 2))
            overall_risk = max(overall_risk, fungal_risk)
            if fungal_risk > 50:
                diseases.append({
                    "type": "Fungal diseases",
                    "risk": fungal_risk,
                    "examples": ["Late blight", "Powdery mildew", "Rust"],
                    "prevention": "Apply preventive fungicide, improve air circulation"
                })
        
        # Bacterial diseases (favor warm + wet)
        if rainfall > 10 and temperature > 22:
            bacterial_risk = min(100, rainfall * 2 + (humidity - 60))
            overall_risk = max(overall_risk, bacterial_risk)
            if bacterial_risk > 40:
                diseases.append({
                    "type": "Bacterial diseases",
                    "risk": bacterial_risk,
                    "examples": ["Bacterial wilt", "Bacterial spot", "Fire blight"],
                    "prevention": "Avoid working in wet fields, remove infected plants"
                })
        
        # Viral transmission risk (insect activity)
        if 20 <= temperature <= 32 and humidity < 80:
            viral_risk = min(80, (temperature - 15) * 2)
            if viral_risk > 50:
                diseases.append({
                    "type": "Viral diseases (via vectors)",
                    "risk": viral_risk,
                    "examples": ["Mosaic virus", "Leaf curl virus"],
                    "prevention": "Control insect vectors, use reflective mulches"
                })
        
        # Root rot risk (waterlogging)
        if rainfall > 50:
            root_risk = min(100, rainfall - 30)
            overall_risk = max(overall_risk, root_risk)
            diseases.append({
                "type": "Root diseases",
                "risk": root_risk,
                "examples": ["Root rot", "Damping off"],
                "prevention": "Improve drainage, avoid overwatering"
            })
        
        # Determine risk level
        if overall_risk >= 70:
            risk_level = "high"
            color = "red"
        elif overall_risk >= 40:
            risk_level = "moderate"
            color = "orange"
        else:
            risk_level = "low"
            color = "green"
        
        return {
            "overall_risk_score": round(overall_risk, 1),
            "risk_level": risk_level,
            "color": color,
            "active_diseases": diseases,
            "general_advice": self._get_disease_prevention_advice(overall_risk, diseases)
        }
    
    def _calculate_pest_pressure(
        self,
        temperature: float,
        humidity: float
    ) -> Dict:
        """Calculate pest pressure based on weather"""
        pests = []
        overall_risk = 0
        
        # Aphids (moderate temp, any humidity)
        if 15 <= temperature <= 28:
            aphid_risk = 60 if 18 <= temperature <= 25 else 40
            pests.append({
                "pest": "Aphids",
                "risk": aphid_risk,
                "conditions": "Active in moderate temperatures",
                "control": "Neem oil spray, introduce ladybugs"
            })
            overall_risk = max(overall_risk, aphid_risk)
        
        # Whiteflies (warm + humid)
        if temperature > 22 and humidity > 60:
            whitefly_risk = min(80, (temperature - 20) * 3 + (humidity - 50))
            pests.append({
                "pest": "Whiteflies",
                "risk": whitefly_risk,
                "conditions": "Thrive in warm, humid conditions",
                "control": "Yellow sticky traps, insecticidal soap"
            })
            overall_risk = max(overall_risk, whitefly_risk)
        
        # Spider mites (hot + dry)
        if temperature > 28 and humidity < 50:
            mite_risk = min(90, (temperature - 25) * 4 + (60 - humidity))
            pests.append({
                "pest": "Spider mites",
                "risk": mite_risk,
                "conditions": "Favor hot, dry conditions",
                "control": "Increase humidity, apply miticide"
            })
            overall_risk = max(overall_risk, mite_risk)
        
        # Caterpillars/larvae (warm)
        if 20 <= temperature <= 35:
            caterpillar_risk = 50
            pests.append({
                "pest": "Caterpillars/Larvae",
                "risk": caterpillar_risk,
                "conditions": "Active in warm weather",
                "control": "Bt spray, hand-picking, pheromone traps"
            })
            overall_risk = max(overall_risk, caterpillar_risk)
        
        # Determine risk level
        if overall_risk >= 70:
            risk_level = "high"
        elif overall_risk >= 40:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        return {
            "overall_risk_score": round(overall_risk, 1),
            "risk_level": risk_level,
            "active_pests": pests,
            "scouting_advice": "Scout fields twice weekly during high-risk periods",
            "general_prevention": [
                "Maintain field hygiene - remove crop residues",
                "Use crop rotation to break pest cycles",
                "Encourage beneficial insects",
                "Install pheromone traps for monitoring"
            ]
        }
    
    def _generate_weather_alerts(
        self,
        temperature: float,
        humidity: float,
        wind_speed: float,
        rainfall: float,
        condition: str
    ) -> List[Dict]:
        """Generate weather alerts"""
        alerts = []
        
        # Heat alert
        if temperature > 40:
            alerts.append({
                "type": "extreme_heat",
                "severity": "critical",
                "icon": "🔥",
                "message": f"Extreme heat warning: {temperature}°C",
                "actions": [
                    "Avoid field work between 11 AM - 4 PM",
                    "Ensure adequate water for workers and livestock",
                    "Provide shade for sensitive crops",
                    "Increase irrigation frequency"
                ]
            })
        elif temperature > 38:
            alerts.append({
                "type": "heat",
                "severity": "warning",
                "icon": "🌡️",
                "message": f"Heat advisory: {temperature}°C",
                "actions": [
                    "Work in cooler hours of the day",
                    "Monitor crops for heat stress signs"
                ]
            })
        
        # Frost alert
        if temperature < 4:
            alerts.append({
                "type": "frost",
                "severity": "critical",
                "icon": "❄️",
                "message": f"Frost warning: {temperature}°C",
                "actions": [
                    "Cover sensitive crops with cloth or plastic",
                    "Apply pre-frost irrigation",
                    "Use smudge pots or heaters in orchards",
                    "Harvest mature produce immediately"
                ]
            })
        
        # Heavy rain alert
        if rainfall > 50:
            alerts.append({
                "type": "heavy_rain",
                "severity": "critical",
                "icon": "🌊",
                "message": f"Heavy rainfall alert: {rainfall}mm expected",
                "actions": [
                    "Clear drainage channels",
                    "Harvest ready crops immediately",
                    "Postpone all field operations",
                    "Protect stored produce from moisture"
                ]
            })
        
        # High wind alert
        if wind_speed > 50:
            alerts.append({
                "type": "high_wind",
                "severity": "critical",
                "icon": "🌪️",
                "message": f"High wind warning: {wind_speed} km/h",
                "actions": [
                    "Secure greenhouses and structures",
                    "Stake tall crops",
                    "Do not spray any chemicals",
                    "Keep workers safe indoors"
                ]
            })
        elif wind_speed > 35:
            alerts.append({
                "type": "wind",
                "severity": "warning",
                "icon": "💨",
                "message": f"Wind advisory: {wind_speed} km/h",
                "actions": [
                    "Avoid spraying operations",
                    "Check crop supports"
                ]
            })
        
        # Disease alert (based on conditions)
        if humidity > 85 and 18 <= temperature <= 28:
            alerts.append({
                "type": "disease_risk",
                "severity": "warning",
                "icon": "🦠",
                "message": "High disease pressure conditions",
                "actions": [
                    "Scout for disease symptoms",
                    "Apply preventive fungicides",
                    "Improve air circulation in dense plantings"
                ]
            })
        
        return alerts
    
    def _calculate_feels_like(self, temperature: float, humidity: float) -> float:
        """Calculate feels-like temperature (heat index approximation)"""
        if temperature < 27:
            return temperature
        
        # Simplified heat index calculation
        hi = -8.785 + 1.611 * temperature + 2.339 * humidity
        hi -= 0.146 * temperature * humidity
        hi -= 0.012 * (temperature ** 2) - 0.016 * (humidity ** 2)
        hi += 0.002 * (temperature ** 2) * humidity
        hi += 0.001 * temperature * (humidity ** 2)
        hi -= 0.000002 * (temperature ** 2) * (humidity ** 2)
        
        return round(hi, 1)
    
    def _categorize_temperature(self, temp: float) -> str:
        """Categorize temperature"""
        if temp < 5:
            return "freezing"
        elif temp < 15:
            return "cold"
        elif temp < 25:
            return "pleasant"
        elif temp < 35:
            return "warm"
        elif temp < 42:
            return "hot"
        else:
            return "extreme"
    
    def _categorize_humidity(self, humidity: float) -> str:
        """Categorize humidity"""
        if humidity < 30:
            return "very_dry"
        elif humidity < 50:
            return "dry"
        elif humidity < 70:
            return "comfortable"
        elif humidity < 85:
            return "humid"
        else:
            return "very_humid"
    
    def _categorize_rainfall(self, rainfall: float) -> str:
        """Categorize rainfall"""
        if rainfall == 0:
            return "none"
        elif rainfall < 5:
            return "trace"
        elif rainfall < 20:
            return "light"
        elif rainfall < 50:
            return "moderate"
        elif rainfall < 100:
            return "heavy"
        else:
            return "extreme"
    
    def _get_general_recommendation(self, score: int, issues: List[str]) -> str:
        """Get general recommendation based on score"""
        if score >= 80:
            return "Excellent conditions for all farming operations. Proceed as planned."
        elif score >= 60:
            return "Good conditions with minor limitations. Most operations can proceed."
        elif score >= 40:
            return "Fair conditions. Plan activities carefully and monitor weather closely."
        elif score >= 20:
            return "Poor conditions. Limit field operations to essential tasks only."
        else:
            return "Unsuitable conditions. Postpone all field operations until weather improves."
    
    def _get_disease_prevention_advice(
        self,
        risk_score: float,
        diseases: List[Dict]
    ) -> List[str]:
        """Get disease prevention advice"""
        advice = []
        
        if risk_score >= 70:
            advice.append("Apply preventive fungicide/bactericide immediately")
            advice.append("Increase scouting frequency to daily")
            advice.append("Remove and destroy any infected plant material")
        elif risk_score >= 40:
            advice.append("Monitor crops closely for disease symptoms")
            advice.append("Ensure good air circulation in fields")
            advice.append("Avoid overhead irrigation if possible")
        else:
            advice.append("Maintain regular scouting schedule")
            advice.append("Continue good cultural practices")
        
        return advice
    
    def get_crop_specific_advice(
        self,
        crop: str,
        temperature: float,
        humidity: float,
        rainfall: float
    ) -> Dict:
        """Get weather advice specific to a crop"""
        crop_lower = crop.lower()
        
        if crop_lower not in self.CROP_WEATHER_SENSITIVITY:
            return {
                "error": f"Crop '{crop}' not in database",
                "available_crops": list(self.CROP_WEATHER_SENSITIVITY.keys())
            }
        
        sensitivity = self.CROP_WEATHER_SENSITIVITY[crop_lower]
        warnings = []
        recommendations = []
        
        # Temperature analysis
        opt_min, opt_max = sensitivity["optimal_temp"]
        if temperature < sensitivity["critical_low_temp"]:
            warnings.append(f"Critical: Temperature too low for {crop}")
            recommendations.append("Provide frost protection immediately")
        elif temperature > sensitivity["critical_high_temp"]:
            warnings.append(f"Critical: Temperature too high for {crop}")
            recommendations.append("Implement cooling measures, increase irrigation")
        elif temperature < opt_min:
            warnings.append(f"Temperature below optimal for {crop}")
            recommendations.append("Monitor for cold stress symptoms")
        elif temperature > opt_max:
            warnings.append(f"Temperature above optimal for {crop}")
            recommendations.append("Provide shade if possible, ensure adequate water")
        
        # Drought/water sensitivity
        if rainfall < 5 and sensitivity["drought_sensitive"]:
            warnings.append(f"{crop} is drought-sensitive - irrigation needed")
            recommendations.append("Increase irrigation frequency")
        
        # Waterlogging sensitivity
        if rainfall > 50 and not sensitivity["waterlogging_tolerant"]:
            warnings.append(f"{crop} does not tolerate waterlogging")
            recommendations.append("Ensure proper drainage, consider raised beds")
        
        return {
            "crop": crop,
            "temperature_status": "optimal" if opt_min <= temperature <= opt_max else "sub-optimal",
            "warnings": warnings,
            "recommendations": recommendations,
            "sensitivity_profile": sensitivity
        }


# Create singleton instance
weather_service = WeatherService()


def get_weather_analysis(
    temperature: float,
    humidity: float,
    wind_speed: float,
    rainfall: float,
    condition: str = "clear"
) -> Dict:
    """
    Convenience function to get weather analysis
    
    Args:
        temperature: Temperature in Celsius
        humidity: Relative humidity (%)
        wind_speed: Wind speed in km/h
        rainfall: Rainfall in mm
        condition: Weather condition
    
    Returns:
        Complete weather analysis for farming
    """
    return weather_service.analyze_weather_for_farming(
        temperature, humidity, wind_speed, rainfall, condition
    )
