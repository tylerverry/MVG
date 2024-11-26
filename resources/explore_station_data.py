import json
from mvg import MvgApi

# St. Emmeram Station ID
ST_EMMERAM_ID = "de:09162:600"

def fetch_all_station_data(station_id):
    try:
        # Initialize the MVG API for the station
        mvg = MvgApi(station_id)

        # Fetch departures from the station
        departures = mvg.departures()

        # Fetch additional station data if available (adjust as needed)
        station_info = mvg.get_station_info() if hasattr(mvg, "get_station_info") else {}

        # Print results
        print("\n=== Departures ===")
        print(json.dumps(departures, indent=4, ensure_ascii=False))

        if station_info:
            print("\n=== Station Info ===")
            print(json.dumps(station_info, indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"Error fetching data for station {station_id}: {str(e)}")

if __name__ == "__main__":
    print(f"Fetching all available data for station ID: {ST_EMMERAM_ID}")
    fetch_all_station_data(ST_EMMERAM_ID)
