import schedule
import time
from fetch_data import fetch_opensky
from transform import transform_flights
from load import load_to_csv,load_to_mongo

def job():
    raw = fetch_opensky()
    df = transform_flights(raw)
    #load_to_csv(df)
    load_to_mongo(df)
    print(f"Pipeline executado com sucesso. {len(df)} registros salvos.")

if __name__ == "__main__":
    #schedule.every(5).minutes.do(job)  # executa a cada 5 minutos
    job()  # Executa imediatamente para teste
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
