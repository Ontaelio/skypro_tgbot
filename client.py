import logging

import requests

from classes import GetUpdatesResponse, SendMessageResponse


class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse | None:
        url = self.get_url('getUpdates')
        try:
            reply = requests.get(url, params={'timeout': timeout, 'offset': offset})
        except ConnectionError:
            logging.error('Failed to get a response from TG')
            return None
        else:
            return GetUpdatesResponse(**reply.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse | None:
        url = self.get_url('sendMessage')
        print('Text:', text)
        try:
            reply = requests.get(url, params={'chat_id': chat_id,
                                              'text': text,
                                              'parse_mode': "MarkdownV2"})
        except ConnectionError:
            logging.error('Failed to get a response from TG')
            return None
        else:
            print('from SendMessageResponse:', reply.json())
            return SendMessageResponse(**reply.json())
