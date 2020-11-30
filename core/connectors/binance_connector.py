from binance.client import Client
import json
import time
import requests
import logging
import numpy as np

# TODO mover a algun lugar comun
logging.basicConfig(filename='trader_service.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


class Binance_Connector:
    def __init__(self,
                 mode='test',
                 symbol='BTCUSDT'
                 ):
        self.mode = mode
        self.symbol = symbol
        self.binance_client = Client
        self.precision = 8  # TODO get from binance_client.get_symbol_info('BTCUSDT')
        self.step_size = 0.00000100  # TODO get from binance_client.get_symbol_info('BTCUSDT') LOT_SIZE
        assert mode in ['PROD', 'test', 'sim'], 'mode should be PROD, test or sim'  # TODO pasar a un exception general
        self.base_asset = 'BTC' #TODO get from get_symbol_info
        self.quoted_asset = 'USDT' #TODO get from get_symbol_info

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

    def buy(self, percentage_trade=0.5):
        if self.mode in ['PROD', 'test']:
            logging.info('env buy: Buying')
            self.init_client()
            account = self.binance_client.get_account()
            balance = float(
                account['balances'][np.argmax([x['asset'] == self.quoted_asset for x in account['balances']])]['free'])
            logging.info('env buy: {} balance: {}'.format(self.quoted_asset, balance))
            depth = self.binance_client.get_order_book(symbol=self.symbol)
            current_price = np.mean([float(x[0]) for x in depth['bids']])
            logging.info('env buy: {} mean bids price: {}'.format(self.symbol, current_price))
            quantity = balance / current_price
            logging.info('env buy: {} quantity: {}'.format(self.symbol, quantity))
            quantity_trade = np.floor((quantity * percentage_trade) * 10 ** 6) / 10 ** 6  #TODO ver esta division hardcodeada
            logging.info('env buy: {} quantity to trade: {}'.format(self.symbol, quantity_trade))
            if self.mode == 'PROD':
                order = self.binance_client.create_order(
                    symbol=self.symbol,
                    side=Client.SIDE_BUY,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity_trade)
            else:
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
        if self.mode in ['PROD', 'test']:
            logging.info('env: Selling')
            self.init_client()
            account = self.binance_client.get_account()
            quantity = float(
                account['balances'][np.argmax([x['asset'] == self.base_asset for x in account['balances']])]['free'])
            quantity = np.floor(quantity * 10 ** 6) / 10 ** 6 #TODO ver esta division hardcodeada
            logging.info('env sell: {} quantity: {}'.format(self.symbol, quantity))
            if self.mode == 'PROD':
                order = self.binance_client.create_order(
                    symbol=self.symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity)
            else:
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
