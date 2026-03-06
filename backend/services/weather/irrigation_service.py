# Weather-based irrigation service

class WeatherIrrigationService:
    def __init__(self, weather_api_key):
        self.api_key = weather_api_key
    
    async def get_weather_data(self, location):
        # Fetch weather data from API
        pass
    
    def should_irrigate(self, weather_data):
        if weather_data.get('rain_expected'):
            return False
        if weather_data.get('humidity', 0) > 80:
            return False
        return True
    
    def calculate_duration(self, weather_data):
        temp = weather_data.get('temperature', 25)
        if temp > 35:
            return 45  # minutes
        elif temp > 30:
            return 30
        return 20

