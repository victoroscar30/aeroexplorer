import sqlite3
from pathlib import Path
from datetime import datetime

def load_to_db(df, db_path="data/opensky.db"):
    conn = sqlite3.connect(db_path)
    df.to_sql("flights", conn, if_exists="append", index=False)
    conn.close()

def load_to_csv(df, folder="data/processed"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"{folder}/opensky_data_{timestamp}.csv"
    
    df.to_csv(csv_path, index=False)
    print(f"Arquivo salvo em: {csv_path}")

#def load_to_csv(df, csv_path="data/processed/opensky_data.csv"):
#    df.to_csv(csv_path, index=False)