import datetime
import json
import os
from pprint import pprint
import asyncio

import requests

from ..db import create_engine, get_db_hostname, start_session, insert
from ..models import FugleOverSold, FugleOverBought
from ..utils import get_api_token

class Fugle():

    def __init__(self, type, symbol):
        self.model = None
        if type == 'overbought':
            self.model = FugleOverBought
        elif type == 'oversold':
            self.model = FugleOverSold
        else:
            raise Exception(f'unknown type: {type}')
        self.symbol = symbol
        self.api_token = get_api_token()
        self.url = f'https://api.fugle.tw/realtime/v0/intraday/quote?symbolId={self.symbol}&apiToken={self.api_token}'
        self.tick = 30 # call API every 30 seconds
        self.quotes = []
        self.transactions = []
        self.bought_quantity = 0
        self.sold_quantity = 0
        self.total_quantity = 0
        self.total_units_from_api = 0
        self.normalized_quantity = 0
        self.on_time = datetime.time(8, 55)
        self.off_time = datetime.time(13, 35)
        self.is_closed = False
        self.date = None

    def is_active(self):
        now = datetime.datetime.now().time()
        if now > self.on_time and now < self.off_time:
            return True
        else:
            return False

    async def exec(self):
        while self.is_active() and not self.is_closed:
            self.quote()
            self.diff()
            #time.sleep(self.tick)
            await asyncio.sleep(self.tick)
        print(f'{self.symbol} self.is_close = {self.is_closed}')
        print(f'{self.symbol} self.total_units_from_api = {self.total_units_from_api}')
        print(f'{self.symbol} overall = {self.bought_quantity + self.sold_quantity}')
        print(f'{self.symbol} self.total_quantity = {self.total_quantity}')

        self.date = datetime.datetime.strptime(self.quotes[-1]['at'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        print(f'{self.symbol} self.date = {self.date}')

        self.normalized_quantity = int(self.total_quantity * self.total_units_from_api / (self.bought_quantity + self.sold_quantity))

    def quote(self):
        resp = requests.get(self.url)
        json = resp.json()
        self.is_closed = json['data']['quote']['isClosed']
        self.total_units_from_api = json['data']['quote']['total']['unit']
        #print(f'self.is_close = {self.is_closed}')
        #print(f'self.total_units_from_api = {self.total_units_from_api}')
        self.quotes.append(json['data']['quote']['order'])
        self.quotes[-1]['trade'] = json['data']['quote']['trade']
        print(self.symbol + " : ")
        pprint(self.quotes[-1])
        #pprint(json)

    def diff(self):
        trade_price = self.quotes[-1]['trade']['price']
        trade_quantity = self.quotes[-1]['trade']['unit']
        ask_diff = abs(self.quotes[-1]['bestAsks'][0]['price'] - trade_price)
        bid_diff = abs(trade_price - self.quotes[-1]['bestBids'][-1]['price'])
        if ask_diff < bid_diff:
            self.sold_quantity += trade_quantity
        elif ask_diff > bid_diff:
            self.bought_quantity += trade_quantity
        else:
            self.sold_quantity += trade_quantity / 2
            self.bought_quantity += trade_quantity / 2
        self.total_quantity = self.bought_quantity - self.sold_quantity
        #print(f'{self.bought_quantity} {self.sold_quantity} {self.total_quantity}')

    def dump_to_file(self):
        if self.quotes is None or len(self.quotes) == 0:
            pass
        else:

            print(f'==> dump to file')

            filename = f'./dump-{self.symbol}.txt'
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            with open(filename, 'w+', encoding='utf-8') as f:
                json.dump(self.quotes, f, ensure_ascii=False, indent=4)

    def save_to_db(self):
        engine = create_engine('mysql+pymysql', 'root', 'admin', get_db_hostname(), '3306', 'mydb')
        session = start_session(engine)

        _dict = {
            'symbol': self.symbol,
            'date': self.date,
            'quantity': self.normalized_quantity
        }
        try:
            insert(session, self.model, _dict)
        except Exception as e:
            print(f'insert entry error: {e}')
        session.commit()
        session.close()
