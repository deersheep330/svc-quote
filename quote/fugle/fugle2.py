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

        self.ask_units = 0
        self.bid_units = 0
        self.diff_units = 0

        self.prev_ask = {
            'price': 0,
            'unit': 0
        }
        self.prev_bid = {
            'price': 0,
            'unit': 0
        }

        self.on_time = datetime.time(9, 1)
        self.off_time = datetime.time(13, 32)

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
            await asyncio.sleep(self.tick)

        self.date = datetime.datetime.strptime(self.quotes[-1]['at'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
        self.diff_units = int(self.ask_units - self.bid_units)
        print(f'=== {self.symbol} information {self.date} ===')
        print(f'is_close = {self.is_closed}')
        print(f'ask = {self.ask_units}, bid = {self.bid_units}')
        print(f'diff = {self.diff_units}')

    def quote(self):
        resp = requests.get(self.url)
        json = resp.json()
        self.is_closed = json['data']['quote']['isClosed']
        self.quotes.append(json['data']['quote']['order'])
        self.quotes[-1]['trade'] = json['data']['quote']['trade']
        print(f"{self.symbol} / {self.quotes[-1]['trade']['price']} / {self.quotes[-1]['at']}")

    def diff(self):
        try:
            record = self.quotes[-1]
            # no transaction
            if len(record['bestAsks']) == 0 or len(record['bestBids']) == 0:
                pass
            cur_ask = record['bestAsks'][0]
            cur_bid = record['bestBids'][-1]
            # broken data
            if cur_ask['price'] == 0 or cur_bid['price'] == 0:
                pass
            # initialize
            if self.prev_ask['price'] == 0 and self.prev_bid['price'] == 0 \
                    and self.prev_ask['unit'] == 0 and self.prev_bid['unit'] == 0:
                self.prev_ask['price'] = cur_ask['price']
                self.prev_ask['unit'] = cur_ask['unit']
                self.prev_bid['price'] = cur_bid['price']
                self.prev_bid['unit'] = cur_bid['unit']
            else:
                # ask side
                if cur_ask['price'] == self.prev_ask['price']:
                    if cur_ask['unit'] < self.prev_ask['unit']:
                        self.ask_units += self.prev_ask['unit'] - cur_ask['unit']
                elif cur_ask['price'] > self.prev_ask['price']:
                    self.ask_units += self.prev_ask['unit']

                self.prev_ask['price'] = cur_ask['price']
                self.prev_ask['unit'] = cur_ask['unit']

                # bid side
                if cur_bid['price'] == self.prev_bid['price']:
                    if cur_bid['unit'] < self.prev_bid['unit']:
                        self.bid_units += self.prev_bid['unit'] - cur_bid['unit']
                elif cur_bid['price'] < self.prev_bid['price']:
                    self.bid_units += self.prev_bid['unit']

                self.prev_bid['price'] = cur_bid['price']
                self.prev_bid['unit'] = cur_bid['unit']

            self.diff_units = self.ask_units - self.bid_units
        except Exception as e:
            print(f'diff for symbol {self.symbol} exception: {e}')

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
            'quantity': self.diff_units
        }
        try:
            insert(session, self.model, _dict)
        except Exception as e:
            print(f'insert entry error: {e}')
        session.commit()
        session.close()
