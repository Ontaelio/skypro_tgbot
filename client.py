import requests

from classes import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url('getUpdates')
        reply = requests.get(url, params={'timeout': timeout, 'offset': offset})
        return GetUpdatesResponse(**reply.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url('sendMessage')
        reply = requests.get(url, params={'chat_id': chat_id, 'text': text})
        return SendMessageResponse(**reply.json())
