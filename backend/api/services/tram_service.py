from mvg import MvgApi
from datetime import datetime

STATION_IDS = [
    {"name": "Prinz-Eugen-Park", "id": "de:09774:2856"},
    {"name": "Prinz-Eugen-Park", "id": "de:09162:632"}
]

def get_tram_departures():
    """Get tram departures sorted by direction"""
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
                        "minutes": minutes,
                        "timestamp": planned_time  # Added for connection calculations
                    }
                    
                    if "st. emmeram" in dep.get("destination", "").lower():
                        northbound.append(tram_info)
                    else:
                        southbound.append(tram_info)
    
    northbound.sort(key=lambda x: x["minutes"])
    southbound.sort(key=lambda x: x["minutes"])
    
    return {
        "northbound": northbound[:4],  # Limit to 4 departures
        "southbound": southbound[:4]
    }
