from mvg import MvgApi
from datetime import datetime

STATION_IDS = [
    {"name": "Prinz-Eugen-Park", "id": "de:09774:2856"},
    {"name": "Prinz-Eugen-Park", "id": "de:09162:632"}
]

def get_tram_departures():
    """Get tram departures sorted by direction"""
    try:
        current_timestamp = datetime.now().timestamp()
        
        # Get cached data and last fetch time
        static_departures = getattr(get_tram_departures, '_cached_departures', None)
        last_fetch_time = getattr(get_tram_departures, '_last_fetch_time', 0)
        
        # Only fetch new data every 180 seconds (3 minutes)
        if not static_departures or (current_timestamp - last_fetch_time) >= 180:
            try:
                northbound = []
                southbound = []
                
                for station in STATION_IDS:
                    mvg = MvgApi(station["id"])
                    departures = mvg.departures()
                    
                    for dep in departures:
                        if dep.get("type") == "Tram":  # Matches actual API response
                            planned_time = dep.get("planned", 0)
                            actual_time = dep.get("time", planned_time)
                            minutes = int((actual_time - current_timestamp) // 60)
                            
                            if minutes >= 0:
                                tram_info = {
                                    "line": dep.get("line", "Unknown"),
                                    "destination": dep.get("destination", "Unknown"),
                                    "minutes": minutes,
                                    "timestamp": actual_time,
                                    "delay": actual_time - planned_time if planned_time else 0,
                                    "is_live": True
                                }
                                
                                if "st. emmeram" in dep.get("destination", "").lower():
                                    northbound.append(tram_info)
                                else:
                                    southbound.append(tram_info)
                
                # Only update cache if we successfully got new data
                if northbound or southbound:
                    northbound.sort(key=lambda x: x["minutes"])
                    southbound.sort(key=lambda x: x["minutes"])
                    
                    get_tram_departures._cached_departures = {
                        "northbound": northbound[:4],
                        "southbound": southbound[:4]
                    }
                    get_tram_departures._last_fetch_time = current_timestamp
                    return get_tram_departures._cached_departures
                elif static_departures:
                    # If no new data but we have cache, keep using it
                    return static_departures
                
            except Exception as e:
                print(f"Error fetching new tram data: {str(e)}")
                if static_departures:
                    return static_departures
                return {"northbound": [], "southbound": []}
        
        # Update minutes in cached data
        if static_departures:
            result = {
                "northbound": [],
                "southbound": []
            }
            
            for direction in ['northbound', 'southbound']:
                result[direction] = [
                    {**dep, 'minutes': int((dep['timestamp'] - current_timestamp) // 60)}
                    for dep in static_departures[direction]
                    if int((dep['timestamp'] - current_timestamp) // 60) >= 0
                ]
            
            return result
            
        return {"northbound": [], "southbound": []}
        
    except Exception as e:
        print(f"Error in get_tram_departures: {str(e)}")
        return {
            "northbound": [],
            "southbound": []
        }
