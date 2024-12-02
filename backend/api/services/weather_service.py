import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.API_KEY = "535155cbe44494b5bb60c08cfe379f60"
        self.LAT = "48.16381"
        self.LON = "11.63320"
        self.cache = None
        self.cache_time = None
        self.CACHE_DURATION = timedelta(minutes=15)

    def _is_cache_valid(self):
        """Check if cached data is still valid"""
        if not self.cache or not self.cache_time:
            return False
        return datetime.now() - self.cache_time < self.CACHE_DURATION

    def get_weather(self):
        """Get weather data, using cache if valid"""
        try:
            if self._is_cache_valid():
                return self.cache

            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": self.LAT,
                "lon": self.LON,
                "appid": self.API_KEY,
                "units": "metric"
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            weather_data = response.json()

            processed_data = {
                "temp": round(weather_data["main"]["temp"]),
                "temp_min": round(weather_data["main"]["temp_min"]),
                "temp_max": round(weather_data["main"]["temp_max"]),
                "humidity": weather_data["main"]["humidity"],
                "wind_speed": round(weather_data["wind"]["speed"] * 3.6, 1),  # m/s to km/h
                "condition": weather_data["weather"][0]["main"].lower(),
                "description": weather_data["weather"][0]["description"],
                "icon": weather_data["weather"][0]["icon"]
            }

            # Update cache
            self.cache = processed_data
            self.cache_time = datetime.now()

            return processed_data

        except requests.Timeout:
            logger.error("Weather API timeout")
            return self._get_fallback_data("API timeout")
        except requests.RequestException as e:
            logger.error(f"Weather API error: {str(e)}")
            return self._get_fallback_data("API error")
        except Exception as e:
            logger.error(f"Unexpected error in weather service: {str(e)}")
            return self._get_fallback_data("Unknown error")

    def _get_fallback_data(self, error_type):
        """Return cached data if available, otherwise error data"""
        if self.cache:
            self.cache["error"] = error_type
            return self.cache
        
        return {
            "temp": None,
            "temp_min": None,
            "temp_max": None,
            "humidity": None,
            "wind_speed": None,
            "condition": "unknown",
            "description": "Weather data unavailable",
            "icon": "50d",  # Mist icon as fallback
            "error": error_type
        }

# Create a singleton instance
weather_service = WeatherService()
