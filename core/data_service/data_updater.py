
from pathlib import Path
import pandas as pd
from datetime import timedelta, datetime
from dateutil import parser
from binance.client import Client
from core.utils import data_utils, time_utils
import json
import requests
import logging
import time

class Data_Updater():
    def __init__(self,
                 symbol='BTCUSDT',
                 time_interval='1h'):
        self.symbol = symbol
        self.time_interval = time_interval
        self.data_path = 'data/{}-{}-data.csv'.format(symbol, time_interval)
        self.data = []
        self.binance_client = Client
        self.last_timestamp = datetime.strptime('1 Jan 2019', '%d %b %Y')
        self.get_initial_data()

    def init_client(self):
        with open('secrets/binance.secrets', 'r') as f:
            secrets = json.loads(f.read())
        status = False
        while not status:
            try:
                self.binance_client = Client(api_key=secrets['api_key'], api_secret=secrets['api_secret'])
                status = True
            except requests.exceptions.Timeout:
                logging.info('init_client: Connection TimeOut')
                time.sleep(60)
        return self

    def get_initial_data(self):
        if Path(self.data_path).exists():
            self.data = pd.read_csv(self.data_path)
            self.last_timestamp = self.data.timestamp.iloc[-1]
        return self

    def get_old_new_timestamp(self):
        if len(self.data) > 0:
            oldest_point = parser.parse(self.data["timestamp"].iloc[-1])
        else:
            oldest_point = datetime.strptime('1 Jan 2019', '%d %b %Y')

        newest_point = pd.to_datetime(
            self.binance_client.get_klines(symbol=self.symbol,
                                           interval=self.time_interval
                                           )[-1][0], unit='ms')
        return oldest_point, newest_point

    def get_new_data(self):
        self.init_client()
        oldest_point, newest_point = self.get_old_new_timestamp()
        from_point = oldest_point + timedelta(minutes=time_utils.get_minutes_from_interval(self.time_interval))
        if from_point <= newest_point:
            binance_response = self.binance_client.get_historical_klines(self.symbol,
                                                                        self.time_interval,
                                                                        from_point.strftime("%d %b %Y %H:%M:%S"),
                                                                        newest_point.strftime("%d %b %Y %H:%M:%S")
                                                                         )
            data_new = data_utils.binanceklines_2_pandas(binance_response)
        else:
            data_new = []
        return data_new

    def update_data(self):
        data_new = self.get_new_data()
        if len(data_new) > 0:
            if len(self.data) > 0:
                self.data = self.data.append(data_new)
            else:
                self.data = data_new
            self.save_data()
            self.last_timestamp = data_new.timestamp.iloc[-1]
        return len(data_new) > 0

    def save_data(self):
        self.data.to_csv(self.data_path, index=False)
        return self

    def get_data(self):
        return self.data
