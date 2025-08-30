import sqlite3

def load_to_db(df, db_path="data/opensky.db"):
    conn = sqlite3.connect(db_path)
    df.to_sql("flights", conn, if_exists="append", index=False)
    conn.close()
