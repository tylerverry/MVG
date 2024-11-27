from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

def get_bus_departures():
    """
    Generate the hardcoded schedule for bus 189 to Unterföhring.
    
    The bus runs every 20 minutes from 6:08 to 19:48,
    with departures at :08, :28, and :48 past each hour.
    
    Returns:
        dict: Contains a list of future bus departures with timestamps in UTC
              to match the MVG API's timestamp format
    """
    try:
        # Initialize timezones - we need both because we're converting between them
        berlin_tz = ZoneInfo("Europe/Berlin")
        utc_tz = ZoneInfo("UTC")
        
        # Get current date in Berlin time (for schedule generation)
        current_date = datetime.now(berlin_tz).date()
        # Get current timestamp in UTC (for filtering past departures)
        current_timestamp = int(datetime.now(utc_tz).timestamp())
        
        bus_departures = []
        
        # Define the schedule boundaries in Berlin time
        start_time = time(6, 8)   # First bus at 06:08
        end_time = time(19, 48)   # Last bus at 19:48
        
        current_time = start_time
        while current_time <= end_time:
            # Create a datetime object for this departure in Berlin time
            departure = datetime.combine(current_date, current_time)
            departure = departure.replace(tzinfo=berlin_tz)
            
            # Convert to UTC timestamp to match MVG API format
            utc_departure = departure.astimezone(utc_tz)
            timestamp = int(utc_departure.timestamp())
            
            # Only include future departures
            if timestamp > current_timestamp:
                minutes_until = int((timestamp - current_timestamp) / 60)
                bus_departures.append({
                    "line": "189",
                    "destination": "Unterföhring",
                    "timestamp": timestamp,  # UTC timestamp
                    "minutes": minutes_until
                })
            
            # Move to next departure time (20 minute intervals)
            departure = departure + timedelta(minutes=20)
            current_time = departure.time()

        return {"buses": bus_departures}

    except Exception as e:
        print(f"Error generating bus schedule: {str(e)}")
        return {"buses": []}
