import requests
from decouple import config


EVOLUTION_API_URL = config("EVOLUTION_API_URL")
EVOLUTION_INSTANCE_NAME = config("EVOLUTION_INSTANCE_NAME")
EVOLUTION_AUTHENTICATION_API_KEY = config("AUTHENTICATION_API_KEY")


def send_whatsapp_message(number, text):
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"
    headers = {
        "apikey": EVOLUTION_AUTHENTICATION_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "number": number,
        "text": text,
        "delay": 2000,
    }
    requests.post(
        url=url,
        json=payload,
        headers=headers,
    )
