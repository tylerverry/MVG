def calculate_connection_status(layover_minutes):
    """
    Calculate connection status based on layover time
    Green: 2-5 minutes (ideal connection)
    Yellow: 6-10 minutes (acceptable wait)
    Red: >10 minutes (too long, consider next tram)
    None: <2 minutes (likely to miss connection)
    """
    if layover_minutes < 2:
        return "none"    # Likely to miss connection
    elif 2 <= layover_minutes <= 5:
        return "green"   # Ideal connection
    elif 6 <= layover_minutes <= 10:
        return "yellow"  # Acceptable wait
    else:
        return "red"     # Too long, consider next tram

def calculate_connections(northbound_trams, buses):
    """Calculate connection information for the 189 bus to Unterföhring"""
    TRAM_TO_SE_TIME = 4      # Minutes from PEP to St. Emmeram
    TRAM_TO_BUS_WALK_TIME = 1  # Minutes to walk from tram to bus stop
    
    connections = []
    
    # Filter for only 189 buses to Unterföhring
    relevant_buses = [
        bus for bus in buses 
        if bus.get("line") == "189" and "unterföhring" in bus.get("destination", "").lower()
    ]
    
    for tram in northbound_trams:
        tram_arrival_at_SE = tram['timestamp'] + (TRAM_TO_SE_TIME * 60)
        earliest_possible_bus = tram_arrival_at_SE + (TRAM_TO_BUS_WALK_TIME * 60)
        
        # Find next 189 bus after walking time
        next_buses = [
            bus for bus in relevant_buses 
            if bus['timestamp'] > earliest_possible_bus
        ]
        
        if next_buses:
            next_bus = next_buses[0]
            layover_minutes = int((next_bus['timestamp'] - tram_arrival_at_SE) / 60) - TRAM_TO_BUS_WALK_TIME
            
            connections.append({
                "tram_id": f"{tram['line']}_{tram['timestamp']}",
                "status": calculate_connection_status(layover_minutes)
            })
        else:
            connections.append({
                "tram_id": f"{tram['line']}_{tram['timestamp']}",
                "status": "none"
            })
    
    return connections
