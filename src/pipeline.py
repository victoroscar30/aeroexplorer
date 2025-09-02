import schedule
import time
from fetch_data import fetch_opensky
from transform import transform_flights
from load import load_to_csv,load_to_mongo

def job():
    raw = fetch_opensky()
    df = transform_flights(raw)
    load_to_csv(df)
    
    print(df[['time', 'time_position', 'last_contact']].head(10))
    print(df[['time', 'time_position', 'last_contact']].dtypes)
    print(df[['time', 'time_position', 'last_contact']].isna().sum())
    print(df.dtypes)
    print(df.isna().sum())

    print(df[['time_position']].where(df['time_position'].isna()).head(10))

    load_to_mongo(df)
    print(f"Pipeline executado com sucesso. {len(df)} registros salvos.")

if __name__ == "__main__":
    #schedule.every(5).minutes.do(job)  # executa a cada 5 minutos
    job()  # Executa imediatamente para teste
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
