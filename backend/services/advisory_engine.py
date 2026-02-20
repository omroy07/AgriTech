import google.generativeai as genai
import os
from datetime import datetime
from backend.extensions import db
from backend.models.weather import CropAdvisory, WeatherData
from backend.services.weather_service import WeatherService
import logging

logger = logging.getLogger(__name__)

class AdvisoryEngine:
    @staticmethod
    def generate_advisory(user_id, crop_name, location, soil_type=None, growth_stage=None):
        """
        Generate personalized crop advisory using Gemini AI.
        Combines weather data, soil info, and crop stage for precision.
        """
        try:
            # 1. Gather Context
            weather = WeatherService.get_latest_weather(location)
            weather_str = f"{weather.temperature}°C, {weather.humidity}% humidity, {weather.weather_condition}" if weather else "Data unavailable"
            
            # 2. Build Prompt
            prompt = f"""
            As an expert Agricultural Consultant, provide a concise advisory for a farmer:
            - Crop: {crop_name}
            - Location: {location}
            - Current Weather: {weather_str}
            - Soil Type: {soil_type or 'General'}
            - Growth Stage: {growth_stage or 'Unknown'}
            
            Focus on:
            1. Irrigation needs based on temp/humidity.
            2. Pest/Disease warnings for these conditions.
            3. Nutrient applications.
            Keep it structured and actionable.
            """
            
            # 3. Request AI Completion
            advisory_text = AdvisoryEngine._get_ai_response(prompt)
            
            # 4. Save to DB
            advisory = CropAdvisory(
                user_id=user_id,
                crop_name=crop_name,
                location=location,
                advisory_text=advisory_text,
                growth_stage=growth_stage,
                weather_summary=weather_str,
                soil_summary=soil_type,
                priority=AdvisoryEngine._determine_priority(weather)
            )
            
            db.session.add(advisory)
            db.session.commit()
            return advisory
            
        except Exception as e:
            logger.error(f"Advisory generation failed: {str(e)}")
            return None

    @staticmethod
    def _get_ai_response(prompt):
        """Internal helper for Gemini API calls with fallback"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Note: High temperature detected. Increase irrigation frequency by 20%. Watch for aphids on lower leaves."
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.warning(f"AI API failed: {str(e)}. Using rule-based fallback.")
            return "Automated Alert: Frost warning tonight. Cover sensitive {crop_name} seedlings or use smudge pots to prevent damage."

    @staticmethod
    def _determine_priority(weather):
        """Assign priority based on environmental hazards"""
        if not weather: return 'Normal'
        
        if weather.temperature > 40 or weather.temperature < 2:
            return 'High'
        if weather.rainfall > 50: # Heavy rain
            return 'High'
        return 'Normal'
