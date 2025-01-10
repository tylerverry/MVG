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
        """Get weather forecast for the next 6 hours"""
        try:
            if self._is_cache_valid():
                return self.cache

            # Fetch forecast data
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": self.LAT,
                "lon": self.LON,
                "appid": self.API_KEY,
                "units": "metric",
                "cnt": 3  # Limit to next 3 time slots (9 hours)
            }

            # Get forecast in both languages
            response_en = requests.get(url, params=dict(params, lang="en"), timeout=5)
            response_en.raise_for_status()
            forecast_en = response_en.json()

            response_de = requests.get(url, params=dict(params, lang="de"), timeout=5)
            response_de.raise_for_status()
            forecast_de = response_de.json()

            # Process forecast data
            forecasts = forecast_en['list'][:2]  # Next 6 hours (2 time slots)
            
            if forecasts:
                # Find most relevant conditions
                max_pop = max(f['pop'] for f in forecasts)  # Highest rain probability
                min_feels_like = min(f['main']['feels_like'] for f in forecasts)
                max_wind = max(f['wind']['speed'] for f in forecasts)
                
                # Get the forecast with highest rain probability
                worst_forecast = max(forecasts, key=lambda x: x['pop'])
                
                # Find matching German description
                de_forecast = next(
                    f for f in forecast_de['list'] 
                    if f['dt'] == worst_forecast['dt']
                )

                # Get all "feels like" temperatures for the forecast period
                feels_like_temps = [f['main']['feels_like'] for f in forecasts]
                
                processed_data = {
                    "temp": round(feels_like_temps[0]),                # Current feels like
                    "temp_min": round(min(feels_like_temps)),         # Min feels like
                    "temp_max": round(max(feels_like_temps)),         # Max feels like
                    "humidity": worst_forecast['main']['humidity'],
                    "wind_speed": round(max_wind * 3.6, 1),          # m/s to km/h
                    "condition": worst_forecast['weather'][0]['main'].lower(),
                    "description_en": worst_forecast['weather'][0]['description'],
                    "description_de": de_forecast['weather'][0]['description'],
                    "icon": worst_forecast['weather'][0]['icon'],
                    "rain_chance": round(max_pop * 100),             # Convert to percentage
                    "forecast_time": worst_forecast['dt']
                }

                # Add rain/snow volume if present
                if 'rain' in worst_forecast:
                    processed_data['rain_volume'] = worst_forecast['rain'].get('3h', 0)
                if 'snow' in worst_forecast:
                    processed_data['snow_volume'] = worst_forecast['snow'].get('3h', 0)

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
