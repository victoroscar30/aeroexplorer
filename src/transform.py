import pandas as pd

def transform_data(raw_data):
    cols = [
        "icao24", "callsign", "origin_country", "time_position", 
        "last_contact", "longitude", "latitude", "baro_altitude", 
        "on_ground", "velocity", "heading", "vertical_rate"
    ]

    df = pd.DataFrame(raw_data["states"], columns=cols)
    
    # Limpeza
    df["callsign"] = df["callsign"].str.strip()
    df["time_position"] = pd.to_datetime(df["time_position"], unit="s", errors="coerce")
    df["last_contact"] = pd.to_datetime(df["last_contact"], unit="s", errors="coerce")
    
    return df
