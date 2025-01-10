from datetime import datetime
import logging

def calculate_connections(northbound_trams, buses):
    """Calculate connection possibilities between northbound trams and the 189 bus."""
    try:
        # Constants for timing calculations
        TRAM_TO_SE_TIME = 4      # Minutes from Prinz-Eugen-Park to St. Emmeram
        TRAM_TO_BUS_WALK_TIME = 1  # Minutes to walk from tram to bus stop
        
        current_time = int(datetime.now().timestamp())
        
        # Separate live and scheduled bus departures
        bus_departures = buses.get('buses', [])
        live_buses = [bus for bus in bus_departures if bus.get('is_live', False)]
        scheduled_buses = [bus for bus in bus_departures if not bus.get('is_live', False)]
        
        for tram in northbound_trams:
            tram_arrival_at_SE = tram['timestamp'] + (TRAM_TO_SE_TIME * 60)
            earliest_possible_bus = tram_arrival_at_SE + (TRAM_TO_BUS_WALK_TIME * 60)
            
            # First try to find a live bus
            next_live_buses = [
                bus for bus in live_buses 
                if bus['timestamp'] > earliest_possible_bus
            ]
            
            # If no live buses, look for scheduled buses
            next_scheduled_buses = [
                bus for bus in scheduled_buses 
                if bus['timestamp'] > earliest_possible_bus
            ]
            
            # Use live bus if available, otherwise use scheduled
            next_bus = None
            if next_live_buses:
                next_bus = next_live_buses[0]
            elif next_scheduled_buses:
                next_bus = next_scheduled_buses[0]
            
            if next_bus:
                layover_minutes = int((next_bus['timestamp'] - tram_arrival_at_SE) / 60) - TRAM_TO_BUS_WALK_TIME
                
                tram['connection'] = {
                    "next_bus_time": next_bus['timestamp'],
                    "wait_minutes": layover_minutes,
                    "is_live_bus": next_bus.get('is_live', False)  # Add this for debugging
                }
            else:
                tram['connection'] = None

        return northbound_trams

    except Exception as e:
        logging.error(f"Error calculating connections: {str(e)}")
        return northbound_trams
