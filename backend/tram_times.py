from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from mvg import MvgApi
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
CORS(app)

STATION_IDS = [
    {"name": "Prinz-Eugen-Park", "id": "de:09774:2856"},
    {"name": "Prinz-Eugen-Park", "id": "de:09162:632"}
]

@app.route('/')
def home():
    return send_from_directory('static', 'index.html')

@app.route('/api/trams')
def get_tram_times():
    try:
        northbound = []
        southbound = []
        
        for station in STATION_IDS:
            mvg = MvgApi(station["id"])
            departures = mvg.departures()
            
            for dep in departures:
                if dep.get("type") == "Tram":
                    current_time = datetime.now().timestamp()
                    planned_time = dep.get("planned", 0)
                    minutes = int((planned_time - current_time) // 60)
                    
                    if minutes >= 0:
                        tram_info = {
                            "line": dep.get("line", "Unknown"),
                            "destination": dep.get("destination", "Unknown"),
                            "minutes": minutes
                        }
                        
                        if "st. emmeram" in dep.get("destination", "").lower():
                            northbound.append(tram_info)
                        else:
                            southbound.append(tram_info)
        
        northbound.sort(key=lambda x: x["minutes"])
        southbound.sort(key=lambda x: x["minutes"])
        
        return jsonify({
            "northbound": northbound,
            "southbound": southbound,
            "lastUpdated": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error: {str(e)}")  # Added for debugging
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
