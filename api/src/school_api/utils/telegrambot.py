import requests
import json
from django.conf import settings


def send_message(message: str, chat_id: int):
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        response = requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}
