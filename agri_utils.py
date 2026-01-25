"""
Agricultural Data Utilities
Comprehensive utility functions for the AgriTech platform
Provides crop data, calculations, and helper functions
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import json

# ============================================================
# CROP DATABASE
# ============================================================

CROP_DATABASE = {
    "rice": {
        "name": "Rice",
        "scientific_name": "Oryza sativa",
        "category": "cereal",
        "growing_season": ["kharif"],
        "duration_days": (120, 150),
        "water_requirement_mm": (1200, 2000),
        "optimal_temperature": (20, 35),
        "optimal_ph": (5.5, 7.0),
        "nutrients_required": {"nitrogen": "high", "phosphorus": "medium", "potassium": "medium"},
        "common_diseases": ["blast", "brown_spot", "bacterial_blight", "sheath_blight"],
        "harvest_indicators": ["golden_color", "bent_panicles", "hard_grains"],
        "storage_conditions": {"temperature": (15, 20), "humidity": (12, 14)},
        "yield_per_hectare_kg": (3000, 6000),
        "market_price_range_inr": (1800, 2500)
    },
    "wheat": {
        "name": "Wheat",
        "scientific_name": "Triticum aestivum",
        "category": "cereal",
        "growing_season": ["rabi"],
        "duration_days": (100, 140),
        "water_requirement_mm": (400, 600),
        "optimal_temperature": (10, 25),
        "optimal_ph": (6.0, 7.5),
        "nutrients_required": {"nitrogen": "high", "phosphorus": "medium", "potassium": "low"},
        "common_diseases": ["rust", "powdery_mildew", "karnal_bunt", "loose_smut"],
        "harvest_indicators": ["golden_straw", "hard_grain", "dry_leaves"],
        "storage_conditions": {"temperature": (10, 15), "humidity": (10, 12)},
        "yield_per_hectare_kg": (3000, 5000),
        "market_price_range_inr": (1900, 2400)
    },
    "maize": {
        "name": "Maize/Corn",
        "scientific_name": "Zea mays",
        "category": "cereal",
        "growing_season": ["kharif", "rabi"],
        "duration_days": (80, 110),
        "water_requirement_mm": (500, 800),
        "optimal_temperature": (21, 27),
        "optimal_ph": (5.8, 7.0),
        "nutrients_required": {"nitrogen": "high", "phosphorus": "medium", "potassium": "high"},
        "common_diseases": ["leaf_blight", "rust", "stalk_rot", "downy_mildew"],
        "harvest_indicators": ["dry_husks", "milky_kernels", "black_layer"],
        "storage_conditions": {"temperature": (10, 15), "humidity": (12, 14)},
        "yield_per_hectare_kg": (4000, 8000),
        "market_price_range_inr": (1700, 2200)
    },
    "cotton": {
        "name": "Cotton",
        "scientific_name": "Gossypium hirsutum",
        "category": "fiber",
        "growing_season": ["kharif"],
        "duration_days": (150, 180),
        "water_requirement_mm": (700, 1300),
        "optimal_temperature": (21, 30),
        "optimal_ph": (6.0, 8.0),
        "nutrients_required": {"nitrogen": "medium", "phosphorus": "high", "potassium": "high"},
        "common_diseases": ["boll_rot", "wilt", "leaf_curl", "bacterial_blight"],
        "harvest_indicators": ["open_bolls", "white_fiber", "dry_bracts"],
        "storage_conditions": {"temperature": (20, 25), "humidity": (8, 10)},
        "yield_per_hectare_kg": (1500, 2500),
        "market_price_range_inr": (5500, 7000)
    },
    "sugarcane": {
        "name": "Sugarcane",
        "scientific_name": "Saccharum officinarum",
        "category": "cash_crop",
        "growing_season": ["kharif", "spring"],
        "duration_days": (270, 365),
        "water_requirement_mm": (1500, 2500),
        "optimal_temperature": (20, 35),
        "optimal_ph": (6.0, 7.5),
        "nutrients_required": {"nitrogen": "high", "phosphorus": "medium", "potassium": "high"},
        "common_diseases": ["red_rot", "smut", "wilt", "grassy_shoot"],
        "harvest_indicators": ["mature_cane", "high_brix", "dry_lower_leaves"],
        "storage_conditions": {"temperature": (25, 30), "humidity": (80, 85)},
        "yield_per_hectare_kg": (60000, 100000),
        "market_price_range_inr": (280, 350)
    },
    "soybean": {
        "name": "Soybean",
        "scientific_name": "Glycine max",
        "category": "legume",
        "growing_season": ["kharif"],
        "duration_days": (90, 120),
        "water_requirement_mm": (450, 700),
        "optimal_temperature": (20, 30),
        "optimal_ph": (6.0, 7.0),
        "nutrients_required": {"nitrogen": "low", "phosphorus": "high", "potassium": "medium"},
        "common_diseases": ["rust", "pod_blight", "charcoal_rot", "yellow_mosaic"],
        "harvest_indicators": ["yellow_leaves", "dry_pods", "rattling_seeds"],
        "storage_conditions": {"temperature": (10, 15), "humidity": (10, 12)},
        "yield_per_hectare_kg": (1500, 2500),
        "market_price_range_inr": (3500, 4500)
    },
    "tomato": {
        "name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "category": "vegetable",
        "growing_season": ["kharif", "rabi", "summer"],
        "duration_days": (60, 90),
        "water_requirement_mm": (400, 600),
        "optimal_temperature": (18, 27),
        "optimal_ph": (6.0, 7.0),
        "nutrients_required": {"nitrogen": "medium", "phosphorus": "high", "potassium": "high"},
        "common_diseases": ["early_blight", "late_blight", "leaf_curl", "bacterial_wilt"],
        "harvest_indicators": ["red_color", "firm_texture", "easy_detachment"],
        "storage_conditions": {"temperature": (12, 15), "humidity": (85, 90)},
        "yield_per_hectare_kg": (25000, 40000),
        "market_price_range_inr": (10, 50)
    },
    "potato": {
        "name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "category": "vegetable",
        "growing_season": ["rabi"],
        "duration_days": (90, 120),
        "water_requirement_mm": (500, 700),
        "optimal_temperature": (15, 25),
        "optimal_ph": (5.5, 6.5),
        "nutrients_required": {"nitrogen": "high", "phosphorus": "high", "potassium": "high"},
        "common_diseases": ["late_blight", "early_blight", "black_scurf", "wart"],
        "harvest_indicators": ["dry_vines", "mature_skin", "proper_size"],
        "storage_conditions": {"temperature": (2, 4), "humidity": (90, 95)},
        "yield_per_hectare_kg": (20000, 35000),
        "market_price_range_inr": (10, 30)
    },
    "onion": {
        "name": "Onion",
        "scientific_name": "Allium cepa",
        "category": "vegetable",
        "growing_season": ["kharif", "rabi"],
        "duration_days": (90, 150),
        "water_requirement_mm": (350, 550),
        "optimal_temperature": (13, 24),
        "optimal_ph": (6.0, 7.0),
        "nutrients_required": {"nitrogen": "medium", "phosphorus": "medium", "potassium": "medium"},
        "common_diseases": ["purple_blotch", "downy_mildew", "basal_rot", "smut"],
        "harvest_indicators": ["fallen_tops", "mature_bulb", "dry_neck"],
        "storage_conditions": {"temperature": (0, 4), "humidity": (65, 70)},
        "yield_per_hectare_kg": (15000, 25000),
        "market_price_range_inr": (10, 60)
    },
    "groundnut": {
        "name": "Groundnut/Peanut",
        "scientific_name": "Arachis hypogaea",
        "category": "oilseed",
        "growing_season": ["kharif", "rabi"],
        "duration_days": (100, 130),
        "water_requirement_mm": (500, 700),
        "optimal_temperature": (25, 30),
        "optimal_ph": (6.0, 6.5),
        "nutrients_required": {"nitrogen": "low", "phosphorus": "high", "potassium": "medium"},
        "common_diseases": ["tikka_disease", "rust", "collar_rot", "stem_rot"],
        "harvest_indicators": ["yellow_leaves", "mature_pods", "dark_veins"],
        "storage_conditions": {"temperature": (5, 10), "humidity": (65, 70)},
        "yield_per_hectare_kg": (1500, 2500),
        "market_price_range_inr": (4500, 6000)
    }
}

# ============================================================
# FERTILIZER RECOMMENDATIONS
# ============================================================

FERTILIZER_DATABASE = {
    "urea": {
        "name": "Urea",
        "formula": "CO(NH2)2",
        "nutrient_content": {"nitrogen": 46, "phosphorus": 0, "potassium": 0},
        "application_rate_kg_per_hectare": (80, 120),
        "best_time": "vegetative_stage",
        "precautions": ["avoid_excess", "split_application", "irrigate_after"]
    },
    "dap": {
        "name": "DAP (Diammonium Phosphate)",
        "formula": "(NH4)2HPO4",
        "nutrient_content": {"nitrogen": 18, "phosphorus": 46, "potassium": 0},
        "application_rate_kg_per_hectare": (50, 100),
        "best_time": "basal_application",
        "precautions": ["avoid_direct_contact", "mix_with_soil"]
    },
    "mop": {
        "name": "MOP (Muriate of Potash)",
        "formula": "KCl",
        "nutrient_content": {"nitrogen": 0, "phosphorus": 0, "potassium": 60},
        "application_rate_kg_per_hectare": (40, 80),
        "best_time": "before_planting",
        "precautions": ["avoid_chloride_sensitive_crops"]
    },
    "npk_complex": {
        "name": "NPK Complex (10:26:26)",
        "formula": "Complex",
        "nutrient_content": {"nitrogen": 10, "phosphorus": 26, "potassium": 26},
        "application_rate_kg_per_hectare": (100, 150),
        "best_time": "basal_application",
        "precautions": ["balanced_nutrition", "soil_test_based"]
    },
    "ssp": {
        "name": "SSP (Single Super Phosphate)",
        "formula": "Ca(H2PO4)2",
        "nutrient_content": {"nitrogen": 0, "phosphorus": 16, "potassium": 0},
        "application_rate_kg_per_hectare": (150, 250),
        "best_time": "basal_application",
        "precautions": ["good_for_acidic_soil", "provides_calcium"]
    }
}

# ============================================================
# WEATHER BASED ADVISORIES
# ============================================================

def get_weather_advisory(
    temperature: float,
    humidity: float,
    rainfall_mm: float,
    wind_speed_kmph: float
) -> Dict[str, Union[str, List[str]]]:
    """
    Generate agricultural advisory based on weather conditions
    
    Args:
        temperature: Current temperature in Celsius
        humidity: Relative humidity percentage
        rainfall_mm: Expected/actual rainfall in mm
        wind_speed_kmph: Wind speed in km/h
    
    Returns:
        Dictionary containing advisory level and recommendations
    """
    advisories = []
    risk_level = "low"
    
    # Temperature based advisories
    if temperature > 40:
        advisories.append("Extreme heat alert: Provide shade and increase irrigation frequency")
        advisories.append("Avoid field operations during peak heat hours (11 AM - 4 PM)")
        risk_level = "high"
    elif temperature > 35:
        advisories.append("High temperature: Mulching recommended to conserve soil moisture")
        risk_level = "medium"
    elif temperature < 10:
        advisories.append("Cold weather: Protect sensitive crops from frost damage")
        advisories.append("Avoid irrigation during night to prevent frost formation")
        risk_level = "medium"
    elif temperature < 5:
        advisories.append("Frost warning: Cover young plants with straw or plastic sheets")
        risk_level = "high"
    
    # Humidity based advisories
    if humidity > 85:
        advisories.append("High humidity: Monitor for fungal diseases, avoid overhead irrigation")
        advisories.append("Ensure proper plant spacing for air circulation")
        if risk_level != "high":
            risk_level = "medium"
    elif humidity < 30:
        advisories.append("Low humidity: Increase irrigation frequency, watch for pest infestations")
    
    # Rainfall based advisories
    if rainfall_mm > 100:
        advisories.append("Heavy rainfall expected: Ensure proper drainage in fields")
        advisories.append("Postpone fertilizer and pesticide application")
        advisories.append("Harvest mature crops immediately to prevent damage")
        risk_level = "high"
    elif rainfall_mm > 50:
        advisories.append("Moderate rainfall: Check drainage systems, avoid waterlogging")
        if risk_level != "high":
            risk_level = "medium"
    elif rainfall_mm < 5 and humidity < 50:
        advisories.append("Dry conditions: Plan for supplemental irrigation")
    
    # Wind based advisories
    if wind_speed_kmph > 50:
        advisories.append("High wind alert: Secure crop supports, avoid spraying operations")
        risk_level = "high"
    elif wind_speed_kmph > 30:
        advisories.append("Windy conditions: Avoid pesticide spraying to prevent drift")
    
    # Disease risk assessment
    disease_risk = calculate_disease_risk(temperature, humidity, rainfall_mm)
    if disease_risk["risk_level"] == "high":
        advisories.extend(disease_risk["preventive_measures"])
    
    return {
        "risk_level": risk_level,
        "temperature_status": categorize_temperature(temperature),
        "humidity_status": categorize_humidity(humidity),
        "rainfall_status": categorize_rainfall(rainfall_mm),
        "advisories": advisories,
        "disease_risk": disease_risk
    }


def calculate_disease_risk(
    temperature: float,
    humidity: float,
    rainfall_mm: float
) -> Dict[str, Union[str, List[str]]]:
    """
    Calculate disease risk based on weather parameters
    """
    risk_score = 0
    high_risk_diseases = []
    preventive_measures = []
    
    # Fungal disease conditions (warm + humid)
    if 20 <= temperature <= 30 and humidity > 80:
        risk_score += 3
        high_risk_diseases.extend(["rust", "powdery_mildew", "downy_mildew"])
        preventive_measures.append("Apply preventive fungicide spray")
    
    # Bacterial disease conditions (warm + wet)
    if temperature > 25 and rainfall_mm > 20:
        risk_score += 2
        high_risk_diseases.extend(["bacterial_blight", "bacterial_wilt"])
        preventive_measures.append("Avoid working in wet fields to prevent disease spread")
    
    # Late blight conditions (cool + humid)
    if 15 <= temperature <= 22 and humidity > 85:
        risk_score += 3
        high_risk_diseases.append("late_blight")
        preventive_measures.append("Scout for late blight symptoms daily")
        preventive_measures.append("Apply protectant fungicides preventively")
    
    # Determine risk level
    if risk_score >= 5:
        risk_level = "high"
    elif risk_score >= 3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_level": risk_level,
        "risk_score": risk_score,
        "high_risk_diseases": list(set(high_risk_diseases)),
        "preventive_measures": preventive_measures
    }


def categorize_temperature(temp: float) -> str:
    """Categorize temperature for display"""
    if temp < 10:
        return "cold"
    elif temp < 20:
        return "cool"
    elif temp < 30:
        return "moderate"
    elif temp < 40:
        return "hot"
    else:
        return "extreme_heat"


def categorize_humidity(humidity: float) -> str:
    """Categorize humidity for display"""
    if humidity < 30:
        return "very_dry"
    elif humidity < 50:
        return "dry"
    elif humidity < 70:
        return "moderate"
    elif humidity < 85:
        return "humid"
    else:
        return "very_humid"


def categorize_rainfall(rainfall: float) -> str:
    """Categorize rainfall for display"""
    if rainfall < 5:
        return "dry"
    elif rainfall < 20:
        return "light"
    elif rainfall < 50:
        return "moderate"
    elif rainfall < 100:
        return "heavy"
    else:
        return "very_heavy"


# ============================================================
# CROP RECOMMENDATIONS
# ============================================================

def recommend_crops(
    soil_type: str,
    ph: float,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    temperature: float,
    humidity: float,
    rainfall_mm: float,
    season: str = None
) -> List[Dict]:
    """
    Recommend suitable crops based on soil and environmental conditions
    
    Args:
        soil_type: Type of soil (sandy, loamy, clay, etc.)
        ph: Soil pH value
        nitrogen: Nitrogen content (kg/ha)
        phosphorus: Phosphorus content (kg/ha)
        potassium: Potassium content (kg/ha)
        temperature: Average temperature in Celsius
        humidity: Average humidity percentage
        rainfall_mm: Average annual rainfall
        season: Current/target season (kharif, rabi, summer)
    
    Returns:
        List of recommended crops with suitability scores
    """
    recommendations = []
    
    for crop_id, crop in CROP_DATABASE.items():
        score = 0
        factors = []
        
        # pH compatibility (0-25 points)
        ph_min, ph_max = crop["optimal_ph"]
        if ph_min <= ph <= ph_max:
            score += 25
            factors.append({"factor": "pH", "status": "optimal", "score": 25})
        elif ph_min - 0.5 <= ph <= ph_max + 0.5:
            score += 15
            factors.append({"factor": "pH", "status": "acceptable", "score": 15})
        else:
            factors.append({"factor": "pH", "status": "not_suitable", "score": 0})
        
        # Temperature compatibility (0-25 points)
        temp_min, temp_max = crop["optimal_temperature"]
        if temp_min <= temperature <= temp_max:
            score += 25
            factors.append({"factor": "temperature", "status": "optimal", "score": 25})
        elif temp_min - 5 <= temperature <= temp_max + 5:
            score += 15
            factors.append({"factor": "temperature", "status": "acceptable", "score": 15})
        else:
            factors.append({"factor": "temperature", "status": "not_suitable", "score": 0})
        
        # Water requirement compatibility (0-25 points)
        water_min, water_max = crop["water_requirement_mm"]
        if water_min <= rainfall_mm <= water_max:
            score += 25
            factors.append({"factor": "water", "status": "optimal", "score": 25})
        elif water_min * 0.7 <= rainfall_mm <= water_max * 1.3:
            score += 15
            factors.append({"factor": "water", "status": "acceptable", "score": 15})
        else:
            score += 5
            factors.append({"factor": "water", "status": "irrigation_needed", "score": 5})
        
        # Season compatibility (0-25 points)
        if season:
            if season.lower() in crop["growing_season"]:
                score += 25
                factors.append({"factor": "season", "status": "optimal", "score": 25})
            else:
                factors.append({"factor": "season", "status": "off_season", "score": 0})
        else:
            score += 15  # Partial score if season not specified
            factors.append({"factor": "season", "status": "not_specified", "score": 15})
        
        # Calculate suitability percentage
        suitability = (score / 100) * 100
        
        if suitability >= 40:  # Only recommend if at least 40% suitable
            recommendations.append({
                "crop_id": crop_id,
                "crop_name": crop["name"],
                "scientific_name": crop["scientific_name"],
                "category": crop["category"],
                "suitability_score": suitability,
                "factors": factors,
                "expected_yield_range": crop["yield_per_hectare_kg"],
                "duration_days": crop["duration_days"],
                "common_diseases": crop["common_diseases"][:3],
                "nutrients_required": crop["nutrients_required"]
            })
    
    # Sort by suitability score
    recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    return recommendations[:10]  # Return top 10 recommendations


# ============================================================
# YIELD PREDICTION
# ============================================================

def estimate_yield(
    crop_id: str,
    area_hectares: float,
    soil_quality: str = "medium",
    irrigation_type: str = "rainfed",
    fertilizer_usage: str = "moderate"
) -> Dict:
    """
    Estimate crop yield based on conditions
    
    Args:
        crop_id: Crop identifier from database
        area_hectares: Land area in hectares
        soil_quality: low, medium, high
        irrigation_type: rainfed, partial, full
        fertilizer_usage: low, moderate, high, optimal
    
    Returns:
        Yield estimation with financial projections
    """
    if crop_id not in CROP_DATABASE:
        return {"error": f"Crop '{crop_id}' not found in database"}
    
    crop = CROP_DATABASE[crop_id]
    base_yield_min, base_yield_max = crop["yield_per_hectare_kg"]
    base_yield = (base_yield_min + base_yield_max) / 2
    
    # Quality multipliers
    soil_multipliers = {"low": 0.7, "medium": 1.0, "high": 1.2}
    irrigation_multipliers = {"rainfed": 0.8, "partial": 1.0, "full": 1.2}
    fertilizer_multipliers = {"low": 0.75, "moderate": 1.0, "high": 1.15, "optimal": 1.25}
    
    # Calculate adjusted yield
    soil_mult = soil_multipliers.get(soil_quality, 1.0)
    irr_mult = irrigation_multipliers.get(irrigation_type, 1.0)
    fert_mult = fertilizer_multipliers.get(fertilizer_usage, 1.0)
    
    adjusted_yield = base_yield * soil_mult * irr_mult * fert_mult
    total_yield = adjusted_yield * area_hectares
    
    # Financial projections
    price_min, price_max = crop["market_price_range_inr"]
    avg_price = (price_min + price_max) / 2
    
    return {
        "crop": crop["name"],
        "area_hectares": area_hectares,
        "estimated_yield_per_hectare_kg": round(adjusted_yield, 2),
        "total_estimated_yield_kg": round(total_yield, 2),
        "yield_range": {
            "minimum": round(total_yield * 0.85, 2),
            "maximum": round(total_yield * 1.15, 2)
        },
        "financial_projection": {
            "estimated_revenue_inr": round(total_yield * avg_price, 2),
            "revenue_range": {
                "minimum": round(total_yield * 0.85 * price_min, 2),
                "maximum": round(total_yield * 1.15 * price_max, 2)
            },
            "market_price_per_kg": {"min": price_min, "max": price_max}
        },
        "factors_applied": {
            "soil_quality": {"value": soil_quality, "multiplier": soil_mult},
            "irrigation": {"value": irrigation_type, "multiplier": irr_mult},
            "fertilizer": {"value": fertilizer_usage, "multiplier": fert_mult}
        },
        "harvest_timeline": {
            "duration_days": crop["duration_days"],
            "expected_harvest": (
                datetime.now() + timedelta(days=sum(crop["duration_days"]) // 2)
            ).strftime("%Y-%m-%d")
        }
    }


# ============================================================
# FERTILIZER CALCULATOR
# ============================================================

def calculate_fertilizer_requirement(
    crop_id: str,
    area_hectares: float,
    soil_nitrogen: float,
    soil_phosphorus: float,
    soil_potassium: float
) -> Dict:
    """
    Calculate fertilizer requirements based on crop needs and soil status
    
    Args:
        crop_id: Crop identifier
        area_hectares: Land area in hectares
        soil_nitrogen: Current soil N content (kg/ha)
        soil_phosphorus: Current soil P content (kg/ha)
        soil_potassium: Current soil K content (kg/ha)
    
    Returns:
        Fertilizer recommendations with quantities and schedule
    """
    if crop_id not in CROP_DATABASE:
        return {"error": f"Crop '{crop_id}' not found"}
    
    crop = CROP_DATABASE[crop_id]
    nutrients_needed = crop["nutrients_required"]
    
    # Base requirements per hectare (kg)
    base_requirements = {
        "high": {"N": 120, "P": 60, "K": 60},
        "medium": {"N": 80, "P": 40, "K": 40},
        "low": {"N": 40, "P": 20, "K": 20}
    }
    
    # Calculate deficits
    n_requirement = base_requirements[nutrients_needed["nitrogen"]]["N"]
    p_requirement = base_requirements[nutrients_needed["phosphorus"]]["P"]
    k_requirement = base_requirements[nutrients_needed["potassium"]]["K"]
    
    n_deficit = max(0, n_requirement - soil_nitrogen)
    p_deficit = max(0, p_requirement - soil_phosphorus)
    k_deficit = max(0, k_requirement - soil_potassium)
    
    # Calculate fertilizer quantities
    recommendations = []
    
    # Urea for Nitrogen (46% N)
    if n_deficit > 0:
        urea_quantity = (n_deficit / 0.46) * area_hectares
        recommendations.append({
            "fertilizer": "Urea",
            "quantity_kg": round(urea_quantity, 2),
            "nutrient_supplied": {"N": round(n_deficit * area_hectares, 2)},
            "application_schedule": [
                {"stage": "basal", "percentage": 30},
                {"stage": "tillering", "percentage": 40},
                {"stage": "panicle_initiation", "percentage": 30}
            ]
        })
    
    # DAP for Phosphorus (46% P, 18% N)
    if p_deficit > 0:
        dap_quantity = (p_deficit / 0.46) * area_hectares
        recommendations.append({
            "fertilizer": "DAP",
            "quantity_kg": round(dap_quantity, 2),
            "nutrient_supplied": {
                "P": round(p_deficit * area_hectares, 2),
                "N": round(p_deficit * 0.39 * area_hectares, 2)  # Bonus N
            },
            "application_schedule": [
                {"stage": "basal", "percentage": 100}
            ]
        })
    
    # MOP for Potassium (60% K)
    if k_deficit > 0:
        mop_quantity = (k_deficit / 0.60) * area_hectares
        recommendations.append({
            "fertilizer": "MOP",
            "quantity_kg": round(mop_quantity, 2),
            "nutrient_supplied": {"K": round(k_deficit * area_hectares, 2)},
            "application_schedule": [
                {"stage": "basal", "percentage": 50},
                {"stage": "flowering", "percentage": 50}
            ]
        })
    
    return {
        "crop": crop["name"],
        "area_hectares": area_hectares,
        "soil_status": {
            "nitrogen": {"current": soil_nitrogen, "required": n_requirement, "deficit": n_deficit},
            "phosphorus": {"current": soil_phosphorus, "required": p_requirement, "deficit": p_deficit},
            "potassium": {"current": soil_potassium, "required": k_requirement, "deficit": k_deficit}
        },
        "fertilizer_recommendations": recommendations,
        "total_cost_estimate_inr": estimate_fertilizer_cost(recommendations),
        "application_tips": [
            "Apply basal dose before transplanting/sowing",
            "Split nitrogen application for better efficiency",
            "Avoid fertilizer application during heavy rains",
            "Irrigate immediately after fertilizer application"
        ]
    }


def estimate_fertilizer_cost(recommendations: List[Dict]) -> Dict:
    """Estimate cost of recommended fertilizers"""
    prices_per_kg = {
        "Urea": 6,
        "DAP": 27,
        "MOP": 18,
        "NPK Complex": 25,
        "SSP": 8
    }
    
    total_cost = 0
    cost_breakdown = []
    
    for rec in recommendations:
        price = prices_per_kg.get(rec["fertilizer"], 20)
        cost = rec["quantity_kg"] * price
        total_cost += cost
        cost_breakdown.append({
            "fertilizer": rec["fertilizer"],
            "quantity_kg": rec["quantity_kg"],
            "price_per_kg": price,
            "cost_inr": round(cost, 2)
        })
    
    return {
        "total_cost_inr": round(total_cost, 2),
        "breakdown": cost_breakdown
    }


# ============================================================
# IRRIGATION SCHEDULER
# ============================================================

def generate_irrigation_schedule(
    crop_id: str,
    planting_date: str,
    soil_type: str,
    current_season: str,
    area_hectares: float
) -> Dict:
    """
    Generate irrigation schedule based on crop growth stages
    
    Args:
        crop_id: Crop identifier
        planting_date: Date of planting (YYYY-MM-DD)
        soil_type: sandy, loamy, clay
        current_season: kharif, rabi, summer
        area_hectares: Land area
    
    Returns:
        Detailed irrigation schedule
    """
    if crop_id not in CROP_DATABASE:
        return {"error": f"Crop '{crop_id}' not found"}
    
    crop = CROP_DATABASE[crop_id]
    planting = datetime.strptime(planting_date, "%Y-%m-%d")
    duration_avg = sum(crop["duration_days"]) // 2
    
    # Soil water holding capacity (mm per irrigation)
    soil_capacity = {"sandy": 20, "loamy": 40, "clay": 50}
    capacity = soil_capacity.get(soil_type, 35)
    
    # Season adjustment
    season_multiplier = {"kharif": 0.7, "rabi": 1.0, "summer": 1.4}
    multiplier = season_multiplier.get(current_season, 1.0)
    
    # Growth stage water requirements (% of total)
    stages = [
        {"name": "germination", "days": (0, 15), "water_pct": 10},
        {"name": "vegetative", "days": (15, 45), "water_pct": 30},
        {"name": "flowering", "days": (45, 75), "water_pct": 35},
        {"name": "maturity", "days": (75, duration_avg), "water_pct": 25}
    ]
    
    total_water_mm = sum(crop["water_requirement_mm"]) / 2
    schedule = []
    
    for stage in stages:
        stage_start = planting + timedelta(days=stage["days"][0])
        stage_end = planting + timedelta(days=stage["days"][1])
        stage_duration = stage["days"][1] - stage["days"][0]
        
        water_needed = (total_water_mm * stage["water_pct"] / 100) * multiplier
        irrigations_needed = max(1, int(water_needed / capacity))
        interval = max(1, stage_duration // irrigations_needed)
        
        schedule.append({
            "stage": stage["name"],
            "start_date": stage_start.strftime("%Y-%m-%d"),
            "end_date": stage_end.strftime("%Y-%m-%d"),
            "water_requirement_mm": round(water_needed, 2),
            "irrigation_frequency_days": interval,
            "water_per_irrigation_mm": round(capacity * multiplier, 2),
            "critical": stage["name"] in ["flowering", "vegetative"]
        })
    
    return {
        "crop": crop["name"],
        "planting_date": planting_date,
        "expected_harvest": (planting + timedelta(days=duration_avg)).strftime("%Y-%m-%d"),
        "soil_type": soil_type,
        "area_hectares": area_hectares,
        "total_water_requirement_mm": round(total_water_mm * multiplier, 2),
        "total_water_liters": round(total_water_mm * multiplier * area_hectares * 10000, 2),
        "schedule": schedule,
        "tips": [
            "Irrigate during early morning or evening to minimize evaporation",
            "Use drip irrigation for 30-50% water savings",
            "Monitor soil moisture before irrigation",
            "Critical stages require priority during water scarcity"
        ]
    }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_crop_info(crop_id: str) -> Optional[Dict]:
    """Get detailed information about a specific crop"""
    return CROP_DATABASE.get(crop_id)


def get_all_crops() -> List[Dict]:
    """Get list of all crops in database"""
    return [
        {"id": crop_id, "name": data["name"], "category": data["category"]}
        for crop_id, data in CROP_DATABASE.items()
    ]


def get_crops_by_season(season: str) -> List[Dict]:
    """Get crops suitable for a specific season"""
    return [
        {"id": crop_id, "name": data["name"], "category": data["category"]}
        for crop_id, data in CROP_DATABASE.items()
        if season.lower() in data["growing_season"]
    ]


def get_crops_by_category(category: str) -> List[Dict]:
    """Get crops of a specific category"""
    return [
        {"id": crop_id, "name": data["name"]}
        for crop_id, data in CROP_DATABASE.items()
        if data["category"] == category.lower()
    ]


def convert_area(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert area between different units
    
    Supported units: hectare, acre, bigha, square_meter, square_feet
    """
    # Convert to square meters first
    to_sqm = {
        "hectare": 10000,
        "acre": 4046.86,
        "bigha": 2508.38,  # Standard bigha
        "square_meter": 1,
        "square_feet": 0.0929
    }
    
    if from_unit not in to_sqm or to_unit not in to_sqm:
        raise ValueError(f"Unsupported unit. Use: {list(to_sqm.keys())}")
    
    sqm = value * to_sqm[from_unit]
    return round(sqm / to_sqm[to_unit], 4)


def days_to_harvest(planting_date: str, crop_id: str) -> Dict:
    """Calculate days remaining to harvest"""
    if crop_id not in CROP_DATABASE:
        return {"error": "Crop not found"}
    
    crop = CROP_DATABASE[crop_id]
    planting = datetime.strptime(planting_date, "%Y-%m-%d")
    duration_min, duration_max = crop["duration_days"]
    
    harvest_min = planting + timedelta(days=duration_min)
    harvest_max = planting + timedelta(days=duration_max)
    
    today = datetime.now()
    days_elapsed = (today - planting).days
    days_remaining_min = max(0, duration_min - days_elapsed)
    days_remaining_max = max(0, duration_max - days_elapsed)
    
    return {
        "crop": crop["name"],
        "planting_date": planting_date,
        "days_since_planting": days_elapsed,
        "harvest_window": {
            "earliest": harvest_min.strftime("%Y-%m-%d"),
            "latest": harvest_max.strftime("%Y-%m-%d")
        },
        "days_remaining": {
            "minimum": days_remaining_min,
            "maximum": days_remaining_max
        },
        "growth_percentage": min(100, round((days_elapsed / duration_min) * 100, 1))
    }
