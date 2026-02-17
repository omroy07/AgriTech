import requests
import time
import logging

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """
    Client for interacting with third-party weather APIs.
    Includes retry logic and basic error handling.
    """
    def __init__(self, api_key=None, base_url="https://api.openweathermap.org/data/2.5"):
        self.api_key = api_key or "MOCK_API_KEY"
        self.base_url = base_url

    def get_current_weather(self, location, retries=3):
        """Fetch current weather for a location with automatic retries"""
        params = {
            'q': location,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        for attempt in range(retries):
            try:
                # Mocking the actual request for demonstration if no key is provided
                if self.api_key == "MOCK_API_KEY":
                    return self._get_mock_weather(location)
                
                response = requests.get(f"{self.base_url}/weather", params=params, timeout=5)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.warning(f"Weather API attempt {attempt + 1} failed for {location}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
                else:
                    logger.error(f"Weather API finalized failure for {location}")
                    return None

    def _get_mock_weather(self, location):
        """Provides simulated data for development and testing"""
        import random
        return {
            'main': {
                'temp': random.uniform(15, 45),
                'humidity': random.uniform(20, 95)
            },
            'weather': [{'main': random.choice(['Clear', 'Cloudy', 'Rain', 'Storm']), 'description': 'weather status'}],
            'wind': {
                'speed': random.uniform(1, 15),
                'deg': random.uniform(0, 360)
            },
            'name': location,
            'dt': int(time.time())
        }
