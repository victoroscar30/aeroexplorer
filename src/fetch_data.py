import requests
import json
from datetime import datetime
from pathlib import Path

def fetch_opensky():
    url = "https://opensky-network.org/api/states/all"
    resp = requests.get(url)
    data = resp.json()

    # salva uma cópia bruta em disco
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    filename = f"data/raw/opensky_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

    return data

if __name__ == "__main__":
    fetch_opensky()