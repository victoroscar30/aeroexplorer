import requests
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

COLUMN_NAMES = [
    "icao24", "callsign", "origin_country", "time_position",
    "last_contact", "longitude", "latitude", "baro_altitude",
    "on_ground", "velocity", "true_track", "vertical_rate",
    "sensors", "geo_altitude", "squawk", "spi",
    "position_source", "category"
]

def fetch_opensky():
    url = "https://opensky-network.org/api/states/all"
    resp = requests.get(url)
    data = resp.json()

    # Salva raw JSON (opcional)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    filename = f"data/raw/opensky_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

    flights = []
    for state in data.get("states", []):
        state_padded = state + [None]*(18 - len(state))
        flights.append(dict(zip(COLUMN_NAMES, state_padded)))

    # Cria DataFrame final
    df = pd.DataFrame(flights)
    df.insert(0, 'time', data['time'])
    
    return df

if __name__ == "__main__":
    df = fetch_opensky()
    print(df.head())
