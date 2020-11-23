import pandas as pd
import datetime
#from sklearn.base import BaseEstimator, ClassifierMixin
import logging
from  core.environment.environment import Environment

class BaseTrader():
    def __init__(self,
                 environment: Environment,
                 on_investment=False,
                 ):
        self.on_investment = on_investment
        self.env = environment
        self.trade_num = 0
        self.trade_record = {}
        self.binsizes = {"1m": 1, "15m": 15, "5m": 5, "1h": 60, "1d": 1440}
        self.last_timestamp = self.env.start_time
        if on_investment:
            trace_data = {self.trade_num: {'start_datetime': self.env.current_time,
                                           'start_price': self.env.get_current_price()
                                           }
                          }
            self.trade_record.update(trace_data)

    def restart(self):
        pass

    def evaluate_buy(self, data) -> bool:
        NotImplemented

    def evaluate_sell(self, data) -> bool:
        NotImplemented

    def seconds_to_next_hour(self, plus=0):
        delta = datetime.timedelta(hours=1)
        now = datetime.datetime.now()
        next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
        return (next_hour - now).seconds + plus

    def get_data(self):
        if self.env.mode == 'PROD':
            data = self.env.get_data()
            try_num = 0
            while self.last_timestamp == data.index.max():
                logging.info('get_data: WARNING Nothing to get')
                try_num += 1
                self.env.step(1)
                data = self.env.get_data()
            self.last_timestamp = data.index.max()
            logging.info('get_data: OK')
            return data
        else:
            return self.env.get_data()

    def evaluate(self):
        logging.info('trade evaluate: Start Evaluation')
        while not self.env.end:
            data = self.get_data()
            print(len(data))
            if self.on_investment:
                if self.evaluate_sell(data):
                    self.env.sell()
                    self.on_investment = False
                    self.trace('sell', data)
                else:
                    logging.info('trade evaluation: Selling Evaluation = False')
            else:
                if self.evaluate_buy(data):
                    self.env.buy()
                    self.on_investment = True
                    self.trace('buy', data)
                else:
                    logging.info('trade evaluation: Buying Evaluation: False')
            self.env.step(self.seconds_to_next_hour(60)/60)

    def trace(self, mode, data):
        if mode == 'buy':
            trace_data = {self.trade_num: {'start_datetime': self.env.current_time,
                                           'start_price': data.close.iloc[-1]
                                           }
                          }
            self.trade_record.update(trace_data)
        elif mode == 'sell':
            trace_data = {'end_datetime': self.env.current_time,
                          'end_price': data.close.iloc[-1]
                          }
            self.trade_record.get(self.trade_num).update(trace_data)
            self.trade_num += 1
        else:
            trace_data = {}
        logging.info('trade trace: {}'.format(trace_data))

    def fit(self, X, y):
        self.env.restart()
        self.trade_record = {}
        self.restart()
        self.evaluate()
        return self

    def score(self, X, y):
        result_pd = pd.DataFrame(self.trade_record).T
        if len(result_pd) > 0:
            result_pd.loc[:, 'gan'] = result_pd.apply(lambda row: (row.end_price - row.start_price) * 100 / row.start_price, axis=1)
            result_pd.dropna(inplace=True)
            return result_pd.gan.sum()
        else:
            return 0

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self