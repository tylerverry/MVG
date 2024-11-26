from mvg import MvgApi
from datetime import datetime

STATION_IDS = [
    {"name": "St. Emmeram", "id": "de:09162:600"},
    {"name": "St. Emmeram", "id": "de:09772:4019"}
]

def get_bus_departures():
    """Get bus departures from St. Emmeram"""
    bus_departures = []
    
    for station in STATION_IDS:
        mvg = MvgApi(station["id"])
        departures = mvg.departures()
        
        for dep in departures:
            if dep.get("type") == "Bus":
                current_time = datetime.now().timestamp()
                planned_time = dep.get("planned", 0)
                minutes = int((planned_time - current_time) // 60)
                
                if minutes >= 0:
                    bus_departures.append({
                        "line": dep.get("line", "Unknown"),
                        "destination": dep.get("destination", "Unknown"),
                        "minutes": minutes,
                        "timestamp": planned_time  # Added for connection calculations
                    })
    
    bus_departures.sort(key=lambda x: x["minutes"])
    return {"buses": bus_departures}
