from flask import Flask, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from .services.tram_service import get_tram_departures
from .services.bus_service import get_bus_departures
from .services.connection_service import calculate_connections

app = Flask(__name__, 
    static_folder='../static',
    template_folder='../templates'
)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/data')
def get_combined_data():
    """Get all transport data including connections"""
    try:
        # Get base data
        trams = get_tram_departures()
        buses = get_bus_departures()
        
        # Calculate connections for northbound trams
        connections = calculate_connections(
            northbound_trams=trams['northbound'],
            buses=buses['buses']
        )
        
        return jsonify({
            'trams': trams,
            'buses': buses,
            'connections': connections,
            'lastUpdated': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Keep individual endpoints for flexibility
@app.route('/api/trams')
def get_trams():
    """Get only tram data"""
    try:
        return jsonify(get_tram_departures())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/buses')
def get_buses():
    """Get only bus data"""
    try:
        return jsonify(get_bus_departures())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
