from mvg import MvgApi
from datetime import datetime, timedelta

def get_combined_departures(station_id, iterations=3, step=20):
    """
    Fetch departures by simulating time offset via multiple API calls.
    
    :param station_id: The ID of the station to query.
    :param iterations: Number of sequential calls to simulate offset.
    :param step: Minutes to step forward with each iteration.
    :return: A list of departures (unfiltered for debugging).
    """
    mvg = MvgApi(station_id)
    current_time = datetime.now()
    all_departures = []

    try:
        for i in range(iterations):
            # Calculate the time range for this iteration
            offset_time = current_time + timedelta(minutes=i * step)
            departures = mvg.departures()  # Fetch API data
            
            # Debug: Log all departures
            print(f"Iteration {i + 1}, Offset: {offset_time}")
            for dep in departures:
                print(f"Bus {dep.get('line')} to {dep.get('destination')} at {dep.get('planned')}")

            all_departures.extend(departures)  # Add all departures for debugging
        
        return all_departures
    except Exception as e:
        print(f"Error fetching combined departures: {e}")
        return []

def get_bus_departures():
    """Get unique bus departures from St. Emmeram."""
    station_id = "de:09162:600"  # Replace with the correct station ID
    all_departures = get_combined_departures(station_id, iterations=5, step=20)

    # Remove duplicates by converting to a dictionary with a unique key
    unique_departures = {
        (dep.get("line"), dep.get("destination"), dep.get("planned")): dep
        for dep in all_departures
        if dep.get("type") == "Bus"  # Only keep buses
    }

    # Debug: Print unique departures
    print("\nUnique Bus Departures:")
    for key, dep in unique_departures.items():
        print(f"Bus {dep.get('line')} to {dep.get('destination')} at {dep.get('planned')}")

    # Prepare the bus departures list
    bus_departures = []
    for dep in unique_departures.values():
        current_time = datetime.now().timestamp()
        planned_time = dep.get("planned", 0)
        minutes = int((planned_time - current_time) // 60)

        if minutes >= 0:  # Only future departures
            bus_departures.append({
                "line": dep.get("line", "Unknown"),
                "destination": dep.get("destination", "Unknown"),
                "minutes": minutes,
                "timestamp": planned_time
            })

    bus_departures.sort(key=lambda x: x["minutes"])
    return {"buses": bus_departures}
