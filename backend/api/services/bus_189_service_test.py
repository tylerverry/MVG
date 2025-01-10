import sys
from pathlib import Path
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

# Add the project root directory to sys.path
project_root = Path(__file__).resolve().parents[3]  # Adjust depth as needed
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import the service
from backend.api.services.bus_189_service import fetch_live_departures_189

def debug_print(label, data):
    """Helper function to print debug information."""
    print(f"\n=== {label} ===")
    for item in data:
        print(item)

def test_reconcile_departures():
    """
    Fetch live data, generate hardcoded data, and reconcile the two
    with preference for live data when available.
    """
    try:
        # Initialize timezones
        berlin_tz = ZoneInfo("Europe/Berlin")
        utc_tz = ZoneInfo("UTC")

        # Get current date and timestamp
        current_date = datetime.now(berlin_tz).date()
        current_timestamp = int(datetime.now(utc_tz).timestamp())

        # Define hardcoded schedule boundaries
        start_time = time(6, 8)  # First bus at 06:08
        end_time = time(19, 48)  # Last bus at 19:48

        # Generate the hardcoded schedule
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
                    "minutes": int((utc_departure - current_timestamp) / 60)
                })
            current_time = (datetime.combine(current_date, current_time) + timedelta(minutes=20)).time()

        debug_print("Hardcoded Departures", hardcoded_departures)

        # Fetch live data
        live_departures = fetch_live_departures_189()
        debug_print("Live Departures", live_departures)

        # Reconciliation logic
        def is_close(time1, time2, threshold=5 * 60):
            return abs(time1 - time2) <= threshold

        final_departures = []
        hardcoded_dict = {dep["timestamp"]: dep for dep in hardcoded_departures}

        for live_dep in live_departures:
            live_time = live_dep["timestamp"]
            close_hardcoded = [
                time for time in hardcoded_dict if is_close(live_time, time)
            ]

            if close_hardcoded:
                final_departures.append(live_dep)
                for time in close_hardcoded:
                    del hardcoded_dict[time]
            else:
                final_departures.append(live_dep)

        # Add remaining hardcoded departures
        final_departures.extend(hardcoded_dict.values())
        final_departures.sort(key=lambda dep: dep["timestamp"])

        debug_print("Final Reconciled Departures", final_departures)

        return {"buses": final_departures}

    except Exception as e:
        print(f"Error during test reconciliation: {str(e)}")
        return {"buses": []}

if __name__ == "__main__":
    print("Running bus service test...")
    result = test_reconcile_departures()
    print("\n=== Final Output ===")
    print(result)