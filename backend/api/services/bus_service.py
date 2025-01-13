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
        mvg = MvgApi(ST_EMMERAM_ID)
        departures = mvg.departures()
        
        filtered_departures = []
        current_time = int(datetime.now().timestamp())
        
        for dep in departures:
            if dep.get("line") == "189" and "unterföhring" in dep.get("destination", "").lower():
                planned_time = dep.get("planned", 0)
                actual_time = dep.get("time", planned_time)
                
                minutes = int((actual_time - current_time) // 60)
                
                if minutes >= 0:
                    filtered_departures.append({
                        "line": "189",
                        "destination": "Unterföhring",
                        "timestamp": actual_time,
                        "minutes": minutes,
                        "is_live": True,
                        "delay": actual_time - planned_time
                    })
        
        return filtered_departures

    except Exception as e:
        print(f"Error fetching live data: {str(e)}")
        return []

def get_bus_departures():
    """Generate the schedule for bus 189 to Unterföhring."""
    try:
        current_timestamp = int(datetime.now().timestamp())
        
        # Get live data first
        live_departures = fetch_live_departures_189()
        
        # Generate hardcoded schedule
        hardcoded_departures = []
        if datetime.now().weekday() < 5:  # Monday-Friday only
            start_time = time(6, 8)
            end_time = time(20, 28)
            current_time = start_time
            
            while current_time <= end_time:
                departure_time = datetime.combine(datetime.now().date(), current_time)
                timestamp = int(departure_time.timestamp())
                
                if timestamp > current_timestamp:
                    hardcoded_departures.append({
                        "line": "189",
                        "destination": "Unterföhring",
                        "timestamp": timestamp,
                        "minutes": int((timestamp - current_timestamp) // 60),
                        "is_live": False
                    })
                current_time = (datetime.combine(datetime.now().date(), current_time) 
                              + timedelta(minutes=20)).time()
        
        # Combine departures
        final_departures = []
        
        # Add all live departures first
        if live_departures:
            final_departures.extend(live_departures)
            
            # Only add scheduled departures that are at least 10 minutes after last live departure
            last_live_time = max(dep["timestamp"] for dep in live_departures)
            future_hardcoded = [
                dep for dep in hardcoded_departures 
                if dep["timestamp"] > (last_live_time + 600)  # 10 minutes
            ]
            final_departures.extend(future_hardcoded)
        else:
            final_departures.extend(hardcoded_departures)
        
        final_departures.sort(key=lambda x: x["timestamp"])
        return {"buses": final_departures}
        
    except Exception as e:
        print(f"Error generating bus schedule: {str(e)}")
        return {"buses": []}