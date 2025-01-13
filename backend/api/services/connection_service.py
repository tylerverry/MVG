from datetime import datetime
import logging

def calculate_connections(northbound_trams, buses):
    """
    Calculate connection possibilities between northbound trams and the 189 bus.
    For each tram, we try to find the earliest bus departing at or after
    tram arrival + walk time, preferring live over scheduled if both are valid.
    """
    try:
        # Minutes from Prinz-Eugen-Park to St. Emmeram
        TRAM_TO_SE_TIME = 4
        # Minutes to walk from the tram stop to the bus stop
        TRAM_TO_BUS_WALK_TIME = 1

        # All bus departures from the 'buses' dictionary
        bus_departures = buses.get('buses', [])

        # Separate them into "live" vs "scheduled" for preference
        live_buses = [b for b in bus_departures if b.get('is_live', False)]
        scheduled_buses = [b for b in bus_departures if not b.get('is_live', False)]

        # Sort them by timestamp just so we can debug in ascending order
        live_buses.sort(key=lambda x: x['timestamp'])
        scheduled_buses.sort(key=lambda x: x['timestamp'])

        logging.debug("=== calculate_connections Debug ===")
        logging.debug("live_buses: %s", live_buses)
        logging.debug("scheduled_buses: %s", scheduled_buses)

        for tram in northbound_trams:
            # The tram arrives at St. Emmeram (SE) in TRAM_TO_SE_TIME minutes
            # from tram['timestamp']
            tram_arrival_at_SE = tram['timestamp'] + (TRAM_TO_SE_TIME * 60)

            # The earliest time the passenger can catch a bus:
            earliest_possible_bus = tram_arrival_at_SE + (TRAM_TO_BUS_WALK_TIME * 60)

            # Filter out LIVE buses that depart at or after earliest_possible_bus
            valid_live_buses = [
                b for b in live_buses
                if b['timestamp'] >= earliest_possible_bus
            ]
            # Filter out SCHEDULED buses that depart at or after earliest_possible_bus
            valid_scheduled_buses = [
                b for b in scheduled_buses
                if b['timestamp'] >= earliest_possible_bus
            ]

            # We'll pick the first valid live bus if any exist
            next_bus = None
            if valid_live_buses:
                next_bus = valid_live_buses[0]  # Already sorted by timestamp
                logging.debug(
                    "Tram %s picking LIVE bus at %s",
                    tram['line'], next_bus['timestamp']
                )
            elif valid_scheduled_buses:
                next_bus = valid_scheduled_buses[0]
                logging.debug(
                    "Tram %s picking SCHEDULED bus at %s",
                    tram['line'], next_bus['timestamp']
                )
            else:
                logging.debug("Tram %s found NO valid bus!", tram['line'])

            if next_bus:
                # Layover = how many minutes from TRAM_ARRIVAL_AT_SE to bus departure
                # minus the walk time. Another approach: next_bus['timestamp'] - earliest_possible_bus
                # but let's keep your style—just be consistent
                layover_minutes = int((next_bus['timestamp'] - tram_arrival_at_SE) / 60) - TRAM_TO_BUS_WALK_TIME

                tram['connection'] = {
                    "next_bus_time": next_bus['timestamp'],
                    "wait_minutes": layover_minutes,
                    "is_live_bus": next_bus.get('is_live', False)
                }
            else:
                # No bus found for this tram
                tram['connection'] = None

        return northbound_trams

    except Exception as e:
        logging.error(f"Error calculating connections: {str(e)}")
        return northbound_trams
