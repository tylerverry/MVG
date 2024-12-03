from flask import Flask, jsonify, render_template, make_response
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path
import requests

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Now import from backend
from backend.api.services.tram_service import get_tram_departures
from backend.api.services.bus_service import get_bus_departures
from backend.api.services.connection_service import calculate_connections
from backend.api.services.weather_service import weather_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)
CORS(app)

def add_cache_headers(response, max_age=15):
    """Add appropriate cache headers to response"""
    response.headers['Cache-Control'] = f'public, max-age={max_age}'
    response.headers['Expires'] = (
        datetime.utcnow() + timedelta(seconds=max_age)
    ).strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@app.route('/')
def home():
    response = make_response(render_template('index.html'))
    return add_cache_headers(response, max_age=3600)

@app.route('/api/weather/debug')
def weather_debug():
    try:
        # Try current weather first
        current = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": "48.16381",
                "lon": "11.63320",
                "appid": "535155cbe44494b5bb60c08cfe379f60",
                "units": "metric"
            },
            timeout=5
        )
        current.raise_for_status()

        # Then try forecast
        forecast = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params={
                "lat": "48.16381",
                "lon": "11.63320",
                "appid": "535155cbe44494b5bb60c08cfe379f60",
                "units": "metric"
            },
            timeout=5
        )
        forecast.raise_for_status()
        
        return jsonify({
            "current_weather": current.json(),
            "forecast": forecast.json(),
            "weather_service": weather_service.get_weather()
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500
    
@app.route('/api/data')
def get_combined_data():
    try:
        trams = get_tram_departures()
        buses = get_bus_departures()
        weather = weather_service.get_weather()
        
        trams['northbound'] = calculate_connections(
            northbound_trams=trams['northbound'],
            buses=buses
        )
        
        response = make_response(jsonify({
            'trams': trams,
            'buses': buses,
            'weather': weather,
            'lastUpdated': int(datetime.now().timestamp())
        }))
        return add_cache_headers(response, max_age=15)
        
    except Exception as e:
        logger.error(f"Error in combined data endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
