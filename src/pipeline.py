import schedule
import time
from src.fetch_data import fetch_opensky
from src.transform import transform_data
from src.load import load_to_csv

def job():
    raw = fetch_opensky()
    df = transform_data(raw)
    load_to_csv(df)
    print(f"Pipeline executado com sucesso. {len(df)} registros salvos em CSV.")

if __name__ == "__main__":
    schedule.every(5).minutes.do(job)  # executa a cada 5 minutos

    while True:
        schedule.run_pending()
        time.sleep(1)
