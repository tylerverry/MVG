import requests
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class WeatherService:
    def __init__(self):
        self.API_KEY = os.getenv('OPENWEATHER_API_KEY', "535155cbe44494b5bb60c08cfe379f60")
        self.LAT = "48.16381"
        self.LON = "11.63320"
        self.cache = None
        self.cache_time = None
        self.CACHE_DURATION = timedelta(minutes=15)

    def _is_cache_valid(self):
        if not self.cache or not self.cache_time:
            return False
        return datetime.now() - self.cache_time < self.CACHE_DURATION

    def _get_daily_minmax(self):
        """Get forecast min/max temperatures for the next 12 hours"""
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": self.LAT,
                "lon": self.LON,
                "appid": self.API_KEY,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            forecast_data = response.json()
            
            now = datetime.now()
            forecast_window = now + timedelta(hours=12)
            
            relevant_forecasts = [
                item for item in forecast_data['list']
                if now.timestamp() <= item['dt'] <= forecast_window.timestamp()
            ]
            
            if relevant_forecasts:
                temps = [item['main']['temp'] for item in relevant_forecasts]
                return round(min(temps)), round(max(temps))
            
            return None, None
                
        except Exception as e:
            logger.error(f"Error fetching forecast: {str(e)}")
            return None, None

    def get_weather(self):
        """Get current weather and daily forecast in both English and German"""
        try:
            if self._is_cache_valid():
                return self.cache

            # Fetch weather in English
            url = "https://api.openweathermap.org/data/2.5/weather"
            params_en = {
                "lat": self.LAT,
                "lon": self.LON,
                "appid": self.API_KEY,
                "units": "metric",
                "lang": "en"
            }
            response_en = requests.get(url, params=params_en, timeout=5)
            response_en.raise_for_status()
            weather_data_en = response_en.json()

            # Fetch weather in German
            params_de = {
                "lat": self.LAT,
                "lon": self.LON,
                "appid": self.API_KEY,
                "units": "metric",
                "lang": "de"
            }
            response_de = requests.get(url, params=params_de, timeout=5)
            response_de.raise_for_status()
            weather_data_de = response_de.json()

            # Get daily min/max
            daily_min, daily_max = self._get_daily_minmax()

            processed_data = {
                "temp": round(weather_data_en["main"]["temp"]),
                "temp_min": daily_min if daily_min is not None else round(weather_data_en["main"]["temp_min"]),
                "temp_max": daily_max if daily_max is not None else round(weather_data_en["main"]["temp_max"]),
                "humidity": weather_data_en["main"]["humidity"],
                "wind_speed": round(weather_data_en["wind"]["speed"] * 3.6, 1),  # m/s to km/h
                "condition": weather_data_en["weather"][0]["main"].lower(),
                "description_en": weather_data_en["weather"][0]["description"],
                "description_de": weather_data_de["weather"][0]["description"],
                "icon": weather_data_en["weather"][0]["icon"]
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
