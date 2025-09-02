from pathlib import Path
from datetime import datetime
import pandas as pd

def load_to_csv(df, folder="data/processed"):
    Path(folder).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = f"{folder}/opensky_data_{timestamp}.csv"
    
    df.to_csv(csv_path, index=False)
    print(f"Arquivo salvo em: {csv_path}")

def load_to_mongo(df, mongo_uri="mongodb://localhost:27017/", db_name="flightdeck", collection_name="air_traffic"):
    from pymongo import MongoClient
    from pymongo.errors import BulkWriteError
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]
    
    records = df.to_dict(orient='records')
    try:
        for record in records:
            for col, val in record.items():
                if isinstance(val, pd._libs.tslibs.nattype.NaTType):
                    record[col] = None
        if records:
            collection.insert_many(records, ordered=False)
            print(f"{len(records)} documents inserted in {db_name}.{collection_name}")
        else:
            print("No records to insert.")
    except BulkWriteError as bwe:
        print("Errors inserting in bulk", bwe.details)
    finally:
        client.close()