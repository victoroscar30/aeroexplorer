import os
import requests
import time
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

class OpenSkyAuth:
    def __init__(self):
        self.client_id = os.getenv("OPENSKY_USERNAME")
        self.client_secret = os.getenv("OPENSKY_PASSWORD")
        self.token_url = os.getenv("TOKEN_URL")
        self.token = None
        self.expira_em = 0  # timestamp do momento em que o token expira

    def obter_novo_token(self):
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(self.token_url, data=payload, headers=headers)

        if resp.status_code != 200:
            raise Exception(f"Erro ao obter token: {resp.status_code} - {resp.text}")

        data = resp.json()
        self.token = data.get("access_token")
        # armazena timestamp de expiração (60s antes para garantir renovação)
        self.expira_em = time.time() + data.get("expires_in", 1800) - 60
        print("Novo token gerado com sucesso!")
        return self.token

    def get_token(self):
        if self.token is None or time.time() >= self.expira_em:
            return self.obter_novo_token()
        return self.token
