import os
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from mvg import MvgApi
from pathlib import Path

# Constants
ST_EMMERAM_ID = "de:09162:600"
LINE_TO_FILTER = "189"
DESTINATION_TO_FILTER = "Unterföhring"

# Get the project root directory (3 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = "bus_service_debug.log"

debug_logs = []

def add_debug_log(message):
    """Add a message to the debug logs."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    debug_logs.append(f"{timestamp} - {message}")
    # Keep only the last 100 logs
    if len(debug_logs) > 100:
        debug_logs.pop(0)

def write_to_log(message):
    """Ensure the log file exists and append debug information."""
    try:
        # Create logs directory if it doesn't exist
        LOG_DIR.mkdir(exist_ok=True)
        
        log_path = LOG_DIR / LOG_FILE
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Writing to log: {log_path}")  # Debug print
        with open(log_path, "a") as f:
            f.write(f"{timestamp} - {message}\n")
            
    except Exception as e:
        print(f"Logging error: {str(e)}")  # Fallback to console

def fetch_live_departures_189():
    """Fetch live API departures for the 189 bus toward Unterföhring."""
    try:
        add_debug_log("Starting MVG API request")
        
        mvg = MvgApi(ST_EMMERAM_ID)
        departures = mvg.departures()
        
        add_debug_log(f"Raw MVG API response: {departures}")
        
        filtered_departures = []
        current_time = int(datetime.now().timestamp())
        
        for dep in departures:
            add_debug_log(f"Processing departure: {dep}")
            
            if dep["line"] == LINE_TO_FILTER and DESTINATION_TO_FILTER in dep["destination"]:
                # Get planned and actual times
                planned_time = dep["planned"]
                actual_time = dep["time"]
                
                add_debug_log(f"Found 189 bus: planned={planned_time}, actual={actual_time}")
                
                # Calculate delay in minutes
                delay = actual_time - planned_time
                
                minutes = int((actual_time - current_time) / 60)
                
                filtered_departures.append({
                    "line": dep["line"],
                    "destination": dep["destination"],
                    "timestamp": actual_time,
                    "minutes": minutes,
                    "is_live": True,  # All MVG API responses are live
                    "delay": int(delay)  # Delay in seconds
                })

        add_debug_log(f"Filtered departures: {filtered_departures}")
        return filtered_departures

    except Exception as e:
        add_debug_log(f"Error fetching live data: {str(e)}")
        return []

def get_bus_departures():
    """Generate the schedule for bus 189 to Unterföhring."""
    try:
        berlin_tz = ZoneInfo("Europe/Berlin")
        utc_tz = ZoneInfo("UTC")
        current_date = datetime.now(berlin_tz).date()
        current_timestamp = int(datetime.now(utc_tz).timestamp())

        # Get live data first
        live_departures = fetch_live_departures_189()
        write_to_log(f"Live Departures: {live_departures}")

        # Check if today is a weekday (Monday to Friday)
        if current_date.weekday() < 5:  # 0 = Monday, 4 = Friday
            # Generate hardcoded schedule
            start_time = time(6, 8)   # First bus at 06:08
            end_time = time(20, 28)    # Last bus at 20:28
            
            hardcoded_departures = []
            current_time = start_time
            while current_time <= end_time:
                departure = datetime.combine(current_date, current_time).replace(tzinfo=berlin_tz)
                utc_departure = int(departure.astimezone(utc_tz).timestamp())
                
                if utc_departure > current_timestamp:
                    hardcoded_departures.append({
                        "line": "189",
                        "destination": "Unterföhring",
                        "timestamp": utc_departure,
                        "minutes": int((utc_departure - current_timestamp) / 60),
                        "is_live": False
                    })
                current_time = (datetime.combine(current_date, current_time) + timedelta(minutes=20)).time()

            write_to_log(f"Hardcoded Departures: {hardcoded_departures}")
        else:
            write_to_log("No bus service on weekends.")
            hardcoded_departures = []  # No departures on weekends

        # Combine departures
        final_departures = []
        
        # Add all live departures first
        if live_departures:
            final_departures.extend(live_departures)

            # Only add scheduled departures that are at least 10 minutes after last live departure
            last_live_time = max(dep["timestamp"] for dep in live_departures)
            future_hardcoded = [
                dep for dep in hardcoded_departures 
                if dep["timestamp"] > (last_live_time + 600)
            ]
        else:
            future_hardcoded = hardcoded_departures

        final_departures.extend(future_hardcoded)
        final_departures.sort(key=lambda dep: dep["timestamp"])

        write_to_log(f"Final Reconciled Departures: {final_departures}")
        return {"buses": final_departures}

    except Exception as e:
        write_to_log(f"Error generating bus schedule: {str(e)}")
        return {"buses": []}