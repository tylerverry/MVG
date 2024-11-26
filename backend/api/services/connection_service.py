def calculate_connection_status(layover_minutes):
    """Calculate connection status based on layover time"""
    if layover_minutes < 2:
        return "red"    # Likely to miss connection
    elif layover_minutes < 5:
        return "yellow" # Tight connection
    elif layover_minutes <= 10:
        return "green"  # Comfortable connection
    else:
        return "none"   # Too long to wait

def calculate_connections(northbound_trams, buses):
    """Calculate connection information for each northbound tram"""
    TRAM_TO_BUS_WALK_TIME = 3  # Minutes to walk from tram to bus stop
    
    connections = []
    
    for tram in northbound_trams:
        tram_arrival_time = tram['timestamp']
        earliest_possible_bus = tram_arrival_time + (TRAM_TO_BUS_WALK_TIME * 60)
        
        # Find next available bus after walking time
        next_buses = [
            bus for bus in buses 
            if bus['timestamp'] > earliest_possible_bus
        ]
        
        if next_buses:
            next_bus = next_buses[0]
            layover_minutes = int((next_bus['timestamp'] - tram_arrival_time) / 60) - TRAM_TO_BUS_WALK_TIME
            
            connections.append({
                "tram_id": f"{tram['line']}_{tram['timestamp']}",
                "next_bus": {
                    "line": next_bus['line'],
                    "destination": next_bus['destination'],
                    "minutes_after_tram": layover_minutes
                },
                "status": calculate_connection_status(layover_minutes)
            })
        else:
            connections.append({
                "tram_id": f"{tram['line']}_{tram['timestamp']}",
                "next_bus": None,
                "status": "none"
            })
    
    return connections
