from mvg import MvgApi
from datetime import datetime

# Configuration
ST_EMMERAM_ID = "de:09162:600"
LINE_TO_FILTER = "189"
DESTINATION_TO_FILTER = "Unterföhring"

def fetch_live_departures_189():
    """
    Fetch live API departures for the 189 bus toward Unterföhring.

    Returns:
        list: A list of departures with 'timestamp', 'line', 'destination', and 'minutes' fields.
    """
    try:
        # Initialize the MVG API for St. Emmeram
        mvg = MvgApi(ST_EMMERAM_ID)

        # Fetch departures and filter for 189 toward Unterföhring
        departures = mvg.departures()
        filtered_departures = [
            {
                "line": dep["line"],
                "destination": dep["destination"],
                "timestamp": dep["planned"],
                "minutes": int((dep["planned"] - int(datetime.now().timestamp())) / 60)
            }
            for dep in departures
            if dep["line"] == LINE_TO_FILTER and DESTINATION_TO_FILTER in dep["destination"]
        ]

        return filtered_departures

    except Exception as e:
        print(f"Error fetching live data for line {LINE_TO_FILTER}: {e}")
        return []