import datetime
from pprint import pprint

import requests

from ..utils import get_api_token

class Fugle():

    def __init__(self, symbol):
        self.symbol = symbol
        self.api_token = get_api_token()
        self.url = f'https://api.fugle.tw/realtime/v0/intraday/quote?symbolId={self.symbol}&apiToken={self.api_token}'
        self.tick = 30 # call API every 30 seconds
        self.quotes = []
        self.transactions = []
        self.quantity = 0
        self.on_time = datetime.time(8, 58)
        self.off_time = datetime.time(13, 30)
        self.is_closed = False

    def is_active(self):
        now = datetime.datetime.now().time()
        if now > self.on_time and now < self.off_time:
            return True
        else:
            return False

    def exec(self):
        while self.is_active() and not self.is_closed:
            self.quote()
            self.__diff()

    def quote(self):
        resp = requests.get(self.url)
        json = resp.json()
        self.is_closed = json['data']['quote']['isClosed']
        print(f'self.is_close = {self.is_closed}')
        self.quotes.append(json['data']['quote']['order'])
        pprint(self.quotes[-1])
        #pprint(json)

    def __diff(self):
        pass

    def get_transactions(self):
        pass

    def get_quantity(self):
        pass
