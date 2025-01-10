import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from backend.api.services.bus_189_service import fetch_live_departures_189  # Import live data fetcher

# Path to the log file
LOG_FILE = "/mnt/NAS_SSD/NAS_SSD/AppData/mvg/bus_service_debug.log"

def write_to_log(message):
    """Ensure the log file exists and append debug information."""
    log_dir = "/mnt/NAS_SSD/NAS_SSD/AppData/mvg"
    log_file = os.path.join(log_dir, "bus_service_debug.log")

    # Ensure the directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")

def get_bus_departures():
    """
    Generate the schedule for bus 189 to Unterföhring by combining:
    1. Live API data (priority for immediate departures)
    2. Hardcoded schedule (every 20 minutes from 06:08 to 19:48)
    """
    try:
        # Set up timezone handling
        berlin_tz = ZoneInfo("Europe/Berlin")
        utc_tz = ZoneInfo("UTC")

        # Get current date/time in appropriate timezones
        # We need Berlin time for schedule generation but UTC for timestamps
        current_date = datetime.now(berlin_tz).date()
        current_timestamp = int(datetime.now(utc_tz).timestamp())

        # Define the start and end times for the regular schedule
        # Bus 189 runs every 20 minutes between these times
        start_time = time(6, 8)   # First bus at 06:08
        end_time = time(19, 48)   # Last bus at 19:48

        # Get real-time data first - this is highest priority
        live_departures = fetch_live_departures_189()
        # Add is_live flag to live departures
        for dep in live_departures:
            dep['is_live'] = True
        write_to_log(f"Live Departures: {live_departures}")

        # Generate the regular schedule
        hardcoded_departures = []
        current_time = start_time
        while current_time <= end_time:
            # Convert each schedule time to a full datetime with timezone
            departure = datetime.combine(current_date, current_time).replace(tzinfo=berlin_tz)
            # Convert to UTC timestamp for consistency
            utc_departure = int(departure.astimezone(utc_tz).timestamp())
            
            # Only include future departures
            if utc_departure > current_timestamp:
                hardcoded_departures.append({
                    "line": "189",
                    "destination": "Unterföhring",
                    "timestamp": utc_departure,
                    "minutes": int((utc_departure - current_timestamp) / 60),
                    "is_live": False  # Add is_live flag to hardcoded departures
                })
            # Increment by 20 minutes for next departure
            current_time = (datetime.combine(current_date, current_time) + timedelta(minutes=20)).time()

        write_to_log(f"Hardcoded Departures: {hardcoded_departures}")

        # Combine live and scheduled departures
        final_departures = []
        
        # Step 1: Add all live departures first
        # These take priority as they're real-time data
        if live_departures:
            final_departures.extend(live_departures)

        # Step 2: Add scheduled departures
        if live_departures:
            # If we have live data, find the last live departure time
            last_live_time = max(dep["timestamp"] for dep in live_departures)
            # Only add scheduled departures that are at least 10 minutes after
            # the last live departure to avoid conflicts
            future_hardcoded = [
                dep for dep in hardcoded_departures 
                if dep["timestamp"] > (last_live_time + 600)  # 600 seconds = 10 minutes
            ]
        else:
            # If no live data, use all scheduled departures
            future_hardcoded = hardcoded_departures

        # Add the filtered scheduled departures
        final_departures.extend(future_hardcoded)
        
        # Sort all departures by time
        final_departures.sort(key=lambda dep: dep["timestamp"])

        write_to_log(f"Final Reconciled Departures: {final_departures}")

        return {"buses": final_departures}

    except Exception as e:
        # Log any errors and return empty list as fallback
        write_to_log(f"Error generating bus schedule: {str(e)}")
        return {"buses": []}