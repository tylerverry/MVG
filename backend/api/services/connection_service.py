from datetime import datetime
from zoneinfo import ZoneInfo

def calculate_connection_status(layover_minutes):
    """
    Determine the quality of a connection based on layover time.
    
    Args:
        layover_minutes (int): Minutes between tram arrival and bus departure
                             (after accounting for walk time)
    
    Returns:
        str: Connection status
            "green"  -> Ideal connection (0-5 minutes wait)
            "yellow" -> Acceptable wait (6-10 minutes)
            "red"    -> Long wait (>10 minutes)
    """
    if 0 <= layover_minutes <= 5:
        return "green"    # Ideal connection, including tight but viable transfers
    elif 6 <= layover_minutes <= 10:
        return "yellow"   # Acceptable wait time
    else:
        return "red"      # Too long, might want to catch next tram

def calculate_connections(northbound_trams, buses):
    """
    Calculate connection possibilities between northbound trams and the 189 bus.
    
    Args:
        northbound_trams (list): Trams heading to St. Emmeram
        buses (dict): Bus schedule from get_bus_departures()
    
    The function:
    1. Takes into account 4 minutes tram journey time to St. Emmeram
    2. Adds 1 minute for walking to the bus stop
    3. Finds the next available bus after the tram arrival + walk time
    4. Calculates the waiting time and determines connection quality
    5. Embeds this information directly into the tram objects
    
    Returns:
        list: Modified northbound_trams with connection information added
    """
    try:
        # Constants for timing calculations
        TRAM_TO_SE_TIME = 4      # Minutes from Prinz-Eugen-Park to St. Emmeram
        TRAM_TO_BUS_WALK_TIME = 1  # Minutes to walk from tram to bus stop
        
        # Get current time in UTC to match timestamps
        current_time = int(datetime.now(ZoneInfo("UTC")).timestamp())
        
        # Filter to only use future bus departures
        bus_departures = [
            bus for bus in buses.get('buses', [])
            if bus['timestamp'] > current_time
        ]
        
        for tram in northbound_trams:
            # Calculate when tram arrives at St. Emmeram (in UTC)
            tram_arrival_at_SE = tram['timestamp'] + (TRAM_TO_SE_TIME * 60)
            
            # Calculate earliest possible bus after walking to stop
            earliest_possible_bus = tram_arrival_at_SE + (TRAM_TO_BUS_WALK_TIME * 60)
            
            # Find next available bus after arrival + walk time
            next_buses = [
                bus for bus in bus_departures 
                if bus['timestamp'] > earliest_possible_bus
            ]
            
            if next_buses:
                next_bus = next_buses[0]
                
                # Calculate layover time in minutes
                # Subtract walk time as it's not actually waiting time
                layover_minutes = int((next_bus['timestamp'] - tram_arrival_at_SE) / 60) - TRAM_TO_BUS_WALK_TIME
                
                # Debug output (in Berlin time for readability)
                berlin_tz = ZoneInfo("Europe/Berlin")
                print(f"\nConnection calculation for tram:")
                print(f"Tram arrives at SE: {datetime.fromtimestamp(tram_arrival_at_SE, berlin_tz).strftime('%H:%M')}")
                print(f"Next bus departs: {datetime.fromtimestamp(next_bus['timestamp'], berlin_tz).strftime('%H:%M')}")
                print(f"Layover minutes: {layover_minutes}")
                
                # Embed connection information in tram object
                tram['connection'] = {
                    "status": calculate_connection_status(layover_minutes),
                    "next_bus_time": next_bus['timestamp']
                }
            else:
                # No more buses available today or schedule ended
                tram['connection'] = None

        return northbound_trams

    except Exception as e:
        print(f"Error calculating connections: {str(e)}")
        return northbound_trams
