from flask import Flask, jsonify, render_template, make_response
from flask_cors import CORS
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Now import from backend
from backend.api.services.tram_service import get_tram_departures
from backend.api.services.bus_service import get_bus_departures, debug_logs
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
    return add_cache_headers(response, max_age=3600)  # Cache HTML for 1 hour

@app.route('/api/data')
def get_combined_data():
    """Get all transport data including connections and weather"""
    try:
        # Get base data
        trams = get_tram_departures()
        buses = get_bus_departures()
        weather = weather_service.get_weather()
        
        # Calculate connections and update northbound trams
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

@app.route('/api/weather/debug')
def weather_debug():
    """Debug endpoint for weather service"""
    try:
        return jsonify({
            "current_weather": weather_service.get_weather(),
            "cache_time": weather_service.cache_time.isoformat() if weather_service.cache_time else None,
            "cache_valid": weather_service._is_cache_valid()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug')
def debug():
    """Debug endpoint for bus service"""
    try:
        return jsonify({
            "logs": debug_logs,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
