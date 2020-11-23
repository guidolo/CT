from datetime import timedelta, datetime
import pandas as pd
import os 
from pathlib import Path
import time
import logging
from binance.client import Client
import json
import numpy as np
import requests

class Environment:
    def __init__(self, 
                 mode='test',
                 start_time = datetime.fromisoformat('2020-01-01 00:00:00'), 
                 symbol='BTCUSDT',
                 time_delta='1h',
                 percentage_trade=0.5
                ):
        self.mode = mode
        self.symbol=symbol
        self.time_delta=time_delta
        self.start_time = start_time
        self.current_time = start_time
        self.last_timestamp = None
        self.end = False
        self.percentage_trade=percentage_trade
        rootpath = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent
        self.filename = str(rootpath)+'/data/{}-{}-data.csv'.format(self.symbol, self.time_delta)
        assert mode in ['PROD', 'test'], 'mode should be PROD or test'
        assert Path(self.filename).exists(), 'Datasource must exists'
        self.all_data = self.load_all_data()
        self.binance_client = Client

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
                self.step(1)
        return self

    def load_all_data(self):
        data = pd.read_csv(self.filename)
        data.loc[:, 'timestamp'] = pd.to_datetime(data.timestamp)
        data = data.sort_values('timestamp')
        self.last_timestamp = data.timestamp.max()
        return data.set_index('timestamp')
        
    def get_data(self):
        if self.mode == 'test':
            return self.all_data.loc[self.start_time:self.current_time, ]
        else:
            return self.load_all_data().loc[self.start_time:]

    def step(self, minutes):
        if self.mode == 'test':
            self.current_time = self.current_time + timedelta(minutes=minutes)
            if self.current_time >= self.last_timestamp:
                self.end = True
        else:
            logging.info('env - step: waiting for {} minutes'.format(minutes))
            time.sleep(minutes*60)

    def restart(self):
        if self.mode == 'test':
            self.current_time = self.start_time
            self.last_timestamp = self.all_data.index.max()
            self.end = False
        else:
            print('Warning!! PROD mode can`t restart')
        return self

    def buy(self):
        if self.mode == 'PROD':
            logging.info('env buy: Buying')
            self.init_client()
            coin_symbol = 'USDT'
            account = self.binance_client.get_account()
            balance = account['balances'][np.argmax([x['asset'] == coin_symbol for x in account['balances']])]['free']
            logging.info('env buy: {} balance: {}'.format(coin_symbol, balance))
            depth = self.binance_client.get_order_book(symbol=self.symbol)
            current_price = np.mean([float(x[0]) for x in depth['bids']])
            logging.info('env buy: {} mean bids price: {}'.format(self.symbol, current_price))
            quantity = balance / current_price
            logging.info('env buy: {} quantity: {}'.format(self.symbol, quantity))
            quantity_trade = quantity * self.percentage_trade
            logging.info('env buy: {} quantity to trade: {}'.format(self.symbol, quantity_trade))
            order = self.binance_client.create_test_order(
                                                symbol=self.symbol,
                                                side=Client.SIDE_BUY,
                                                type=Client.ORDER_TYPE_MARKET,
                                                quantity=quantity_trade)
            logging.info(order)
            return True
        else:
            return False
    
    def sell(self):
        if self.mode == 'PROD':
            logging.info('env: Selling')
            self.init_client()
            coin_symbol = 'BTC'
            account = self.binance_client.get_account()
            quantity = account['balances'][np.argmax([x['asset'] == coin_symbol for x in account['balances']])]['free']
            logging.info('env sell: {} quantity: {}'.format(self.symbol, quantity))
            order = self.binance_client.create_test_order(
                                                symbol=self.symbol,
                                                side=Client.SIDE_SELL,
                                                type=Client.ORDER_TYPE_MARKET,
                                                quantity=quantity)
            logging.info(order)
            return True
        else:
            return False

    def get_current_price(self):
        self.init_client()
        depth = self.binance_client.get_order_book(symbol=self.symbol)
        return np.mean([float(x[0]) for x in depth['bids']])