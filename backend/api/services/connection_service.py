from datetime import datetime
import logging

def calculate_connections(northbound_trams, buses):
    """Calculate connection possibilities between northbound trams and the 189 bus."""
    try:
        # Constants for timing calculations
        TRAM_TO_SE_TIME = 4      # Minutes from Prinz-Eugen-Park to St. Emmeram
        TRAM_TO_BUS_WALK_TIME = 1  # Minutes to walk from tram to bus stop
        
        current_time = int(datetime.now().timestamp())
        
        bus_departures = [
            bus for bus in buses.get('buses', [])
            if bus['timestamp'] > current_time
        ]
        
        for tram in northbound_trams:
            tram_arrival_at_SE = tram['timestamp'] + (TRAM_TO_SE_TIME * 60)
            earliest_possible_bus = tram_arrival_at_SE + (TRAM_TO_BUS_WALK_TIME * 60)
            
            next_buses = [
                bus for bus in bus_departures 
                if bus['timestamp'] > earliest_possible_bus
            ]
            
            if next_buses:
                next_bus = next_buses[0]
                layover_minutes = int((next_bus['timestamp'] - tram_arrival_at_SE) / 60) - TRAM_TO_BUS_WALK_TIME
                
                tram['connection'] = {
                    "next_bus_time": next_bus['timestamp'],
                    "wait_minutes": layover_minutes  # Just pass the raw minutes instead of a status
                }
            else:
                tram['connection'] = None

        return northbound_trams

    except Exception as e:
        logging.error(f"Error calculating connections: {str(e)}")
        return northbound_trams
