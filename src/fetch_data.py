import requests
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
from auth_opensky import OpenSkyAuth  # precisa estar no mesmo diretório ou em um pacote


# Estrutura das colunas conforme documentação da API
COLUMN_NAMES = [
    "icao24", "callsign", "origin_country", "time_position",
    "last_contact", "longitude", "latitude", "baro_altitude",
    "on_ground", "velocity", "true_track", "vertical_rate",
    "sensors", "geo_altitude", "squawk", "spi",
    "position_source", "category"
]


def fetch_opensky():
    # Inicializa autenticação
    auth = OpenSkyAuth()
    token_valido = auth.get_token()

    # Requisição com token válido
    headers = {"Authorization": f"Bearer {token_valido}"}
    url = "https://opensky-network.org/api/states/all"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()  # lança exceção se status != 200
    data = resp.json()

    # Salva raw JSON (opcional, bom para auditoria e debug)
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    filename = f"data/raw/opensky_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

    # Normaliza os estados de voo
    flights = []
    for state in data.get("states", []):
        # Preenche com None se vier menos colunas
        state_padded = state + [None] * (len(COLUMN_NAMES) - len(state))
        flights.append(dict(zip(COLUMN_NAMES, state_padded)))

    # Cria DataFrame final
    df = pd.DataFrame(flights)
    df.insert(0, 'time', data.get('time'))

    return df


if __name__ == "__main__":
    df = fetch_opensky()
    print(df.head())
