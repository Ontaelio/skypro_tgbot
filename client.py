import logging
from time import sleep

import requests
from requests.exceptions import ConnectionError

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
            sleep(5)
            return None
        else:
            # print(reply.json())
            return GetUpdatesResponse(**reply.json())

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse | None:
        url = self.get_url('sendMessage')
        if len(text) > 4096:
            text = text.split('/bind')[0]
        try:
            reply = requests.get(url, params={'chat_id': chat_id,
                                              'text': text,
                                              'parse_mode': "MarkdownV2"})
        except ConnectionError:
            logging.error('Failed to get a response from TG')
            return None
        else:
            # print('from SendMessageResponse:', reply.json())
            return SendMessageResponse(**reply.json())
