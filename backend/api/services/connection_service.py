from datetime import datetime, time, timedelta
import time as time_module
from zoneinfo import ZoneInfo

def get_hardcoded_189_times():
    """Generate today's 189 bus schedule in German timezone"""
    bus_times = []
    current_date = datetime.now(ZoneInfo("Europe/Berlin")).date()
    
    # Schedule starts at 6:08 and runs every 20 minutes until 19:48
    # Times are :08, :28, and :48 past each hour
    start_time = time(6, 8)  # 6:08
    end_time = time(19, 48)  # 19:48
    
    current_time = start_time
    while current_time <= end_time:
        # Create datetime for this departure in German timezone
        departure = datetime.combine(current_date, current_time)
        departure = departure.replace(tzinfo=ZoneInfo("Europe/Berlin"))
        # Convert to Unix timestamp
        timestamp = int(departure.timestamp())
        bus_times.append(timestamp)
        
        # Add 20 minutes
        departure = departure + timedelta(minutes=20)
        current_time = departure.time()
    
    return bus_times

def calculate_connections(northbound_trams, buses):
    """Calculate connections using hardcoded 189 schedule"""
    TRAM_TO_SE_TIME = 4      # Minutes from PEP to St. Emmeram
    TRAM_TO_BUS_WALK_TIME = 1  # Minutes to walk from tram to bus stop
    
    # Get today's 189 schedule
    bus_189_times = get_hardcoded_189_times()
    current_time = int(datetime.now(ZoneInfo("Europe/Berlin")).timestamp())
    
    # Filter to only future bus times
    future_bus_times = [t for t in bus_189_times if t > current_time]
    
    for tram in northbound_trams:
        # Calculate when tram arrives at St. Emmeram
        tram_arrival_at_SE = tram['timestamp'] + (TRAM_TO_SE_TIME * 60)
        earliest_possible_bus = tram_arrival_at_SE + (TRAM_TO_BUS_WALK_TIME * 60)
        
        # Find next 189 bus after earliest possible time
        next_buses = [t for t in future_bus_times if t > earliest_possible_bus]
        
        if next_buses and earliest_possible_bus < bus_189_times[-1]:  # Only show connections if within service hours
            next_bus_time = next_buses[0]
            layover_minutes = int((next_bus_time - tram_arrival_at_SE) / 60) - TRAM_TO_BUS_WALK_TIME
            
            tram['connection'] = {
                "status": calculate_connection_status(layover_minutes),
                "next_bus_time": next_bus_time
            }
        else:
            tram['connection'] = None
    
    return northbound_trams
