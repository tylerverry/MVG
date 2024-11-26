from mvg import MvgApi
from datetime import datetime

# Station IDs for Prinz-Eugen-Park
STATION_IDS = [
    {"name": "Prinz-Eugen-Park", "id": "de:09774:2856"},
    {"name": "Prinz-Eugen-Park", "id": "de:09162:632"}
]

# Define walking time threshold
WALKING_TIME_THRESHOLD = 6

# Color coding function
def get_time_color(minutes_until_departure):
    if minutes_until_departure < 5:
        return "\033[91m"  # Red for missed trams
    elif WALKING_TIME_THRESHOLD <= minutes_until_departure <= 8:
        return "\033[92m"  # Green for optimal timing
    else:
        return ""  # Default terminal color for longer waits

try:
    northbound_departures = []
    southbound_departures = []

    for station in STATION_IDS:
        station_id = station["id"]
        mvg = MvgApi(station_id)
        departures = mvg.departures()

        for dep in departures:
            if dep.get("type") == "Tram":
                planned_time = dep.get("planned", 0)
                current_time = datetime.now().timestamp()
                minutes_until_departure = int((planned_time - current_time) // 60)

                dep["minutes"] = minutes_until_departure
                dep["station_id"] = station_id

                # Categorize based on destination or your own logic
                destination = dep.get("destination", "").lower()
                if "st. emmeram" in destination:
                    northbound_departures.append(dep)
                else:
                    southbound_departures.append(dep)

    # Function to display departures
    def display_departures(title, departures):
        print(f"\n{title}:")
        for dep in sorted(departures, key=lambda x: x["minutes"]):
            color = get_time_color(dep["minutes"])
            line = dep.get("line", "Unknown")
            destination = dep.get("destination", "Unknown")
            minutes = dep["minutes"]

            if minutes >= 0:  # Only show trams you can catch
                print(f"{color}Line {line} to {destination} in {minutes} minutes\033[0m")

    # Display categorized departures
    display_departures("Northbound Tram Departures", northbound_departures)
    display_departures("Southbound Tram Departures", southbound_departures)

    # Add a timestamp for last update
    last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n\033[94mLast updated: {last_update}\033[0m")

except Exception as e:
    print(f"An error occurred: {e}")
