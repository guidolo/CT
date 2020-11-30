import pandas as pd
from datetime import timedelta
import time
#from sklearn.base import BaseEstimator, ClassifierMixin
import logging
from core.trade_service.data_manager.data_manager import Data_Manager
from core.connectors.binance_connector import Binance_Connector
from core.utils.time_utils import seconds_to_next_hour

class BaseTrader():
    def __init__(self,
                 mode='test',
                 symbol='BTCUSDT',
                 interval_source='5m',
                 interval_group='1h',
                 on_investment=False, #TODO, recuperar automaticamente
                 ):
        assert mode in ['PROD', 'test', 'sim'], 'mode should be PROD, test or sim'  # TODO pasar a un exception general
        self.mode = mode
        self.symbol = symbol
        self.interval_source = interval_source
        self.interval_group = interval_group
        self.data_mgr = Data_Manager(mode,
                                     symbol,
                                     interval_source=interval_source,
                                     interval_group=interval_group)
        if mode in ['PRD', 'test']:
            self.con = Binance_Connector(mode, symbol)
        else:
            self.con = []

        self.on_investment = on_investment
        self.trade_num = 0
        self.trade_record = {}
        self.last_timestamp = self.data_mgr.start_time
        self.current_time = self.data_mgr.start_time
        if on_investment:
            trace_data = {self.trade_num: {'start_datetime': self.current_time,
                                           'start_price': self.con.get_current_price()
                                           }
                          }
            self.trade_record.update(trace_data)

    def restart(self):
        pass

    def evaluate_buy(self, data) -> bool:
        NotImplemented

    def evaluate_sell(self, data) -> bool:
        NotImplemented

    def get_data(self):
        if self.mode in ['PROD', 'test']:
            data = self.data_mgr.get_data()
            try_num = 0
            while self.last_timestamp == data.index.max():
                logging.info('get_data: WARNING Nothing to get')
                try_num += 1
                self.wait(1)
                data = self.data_mgr.get_data()
            self.last_timestamp = data.index.max()
            logging.info('get_data: OK')
            return data
        else:
            return self.data_mgr.get_data(self.current_time)

    def evaluate(self):
        logging.info('trade evaluate: Start Evaluation')
        while not self.data_mgr.end_data:
            data = self.get_data()
            if self.on_investment:
                if self.evaluate_sell(data):
                    self.con.sell()
                    self.on_investment = False
                    self.trace('sell', data)
                else:
                    logging.info('trade evaluation: Selling Evaluation = False')
            else:
                if self.evaluate_buy(data):
                    self.con.buy()
                    self.on_investment = True
                    self.trace('buy', data)
                else:
                    logging.info('trade evaluation: Buying Evaluation: False')
            self.wait(seconds_to_next_hour(60)/60)

    def trace(self, transaction_type: str, data):
        if transaction_type == 'buy':
            trace_data = {self.trade_num: {'start_datetime': self.current_time,
                                           'start_price': data.close.iloc[-1]
                                           }
                          }
            self.trade_record.update(trace_data)
        elif transaction_type == 'sell':
            trace_data = {'end_datetime': self.current_time,
                          'end_price': data.close.iloc[-1]
                          }
            self.trade_record.get(self.trade_num).update(trace_data)
            self.trade_num += 1
        else:
            trace_data = {}
        logging.info('trade trace: {}'.format(trace_data))

    def fit(self, X, y):
        self.data_mgr.restart()
        self.trade_record = {}
        self.restart()
        self.evaluate()
        return self

    def score(self, X, y):
        result_pd = pd.DataFrame(self.trade_record).T
        if len(result_pd) > 0:
            result_pd.loc[:, 'gan'] = result_pd.apply(
                lambda row: (row.end_price - row.start_price) * 100 / row.start_price,
                axis=1)
            result_pd.dropna(inplace=True)
            return result_pd.gan.sum()
        else:
            return 0

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self

    def wait(self, minutes):
        """
        Time to wait until next event
        :param minutes:
        :return:
        """
        if self.mode == 'sim':
            self.current_time = self.current_time + timedelta(minutes=minutes)
        else:
            logging.info('env - step: waiting for {} minutes'.format(minutes))
            time.sleep(minutes*60)