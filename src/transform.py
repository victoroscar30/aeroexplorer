import pandas as pd

def transform_flights(df: pd.DataFrame) -> pd.DataFrame:
    df['callsign'] = df['callsign'].str.strip()
    df['baro_altitude'] = df['baro_altitude'].apply(lambda x: max(x, 0) if pd.notnull(x) else x)
    df['geo_altitude'] = df['geo_altitude'].apply(lambda x: max(x, 0) if pd.notnull(x) else x)

    df['vertical_rate'] = df['vertical_rate'].apply(lambda x: x if pd.notnull(x) and -30 <= x <= 30 else None)

    df['velocity_anomaly'] = df['velocity'].apply(lambda x: True if pd.notnull(x) and x > 320 else False)
    #df['velocity'] = df['velocity'].apply(lambda x: x if pd.notnull(x) and x <= 320 else None)
    
    df.drop(['category', 'sensors','squawk'], axis=1, inplace=True)

    df['time'] = pd.to_datetime(df['time'], unit='s', errors='coerce')
    df['time_position'] = pd.to_datetime(df['time_position'], unit='s', errors='coerce')
    df['last_contact'] = pd.to_datetime(df['last_contact'], unit='s', errors='coerce')
    
    for col in ['time', 'time_position', 'last_contact']:
        df[col] = df[col].apply(lambda x: x.to_pydatetime() if pd.notnull(x) else None)    
    return df
