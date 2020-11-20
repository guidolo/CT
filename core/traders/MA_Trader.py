import numpy as np
from .base import BaseTrader
from ..instrument.moving_averages import MA

class MA_Trader(BaseTrader):
    def __init__(self,
                 environment = None,
                 column_name: str = 'close',
                 period_short: int= 3,
                 period_long: int = 10,
                 panic = -0.01,
                 **kwargs
                 ):
        super().__init__(environment)
        self.period_short = period_short
        self.period_long = period_long
        self.column_name = column_name
        self.ma_short = []
        self.ma_long = []
        self.restart()
        self.panic = panic

    def restart(self):
        self.ma_short = MA(self.column_name, self.period_short)
        self.ma_long = MA(self.column_name, self.period_long)
        return self

    def evaluate_buy(self, data):
        if len(data) > self.period_long:
            return self.ma_short.evaluate(data)[-1] > self.ma_long.evaluate(data)[-1]
        else:
            return False

    def evaluate_sell(self, data):
        #evaluate panic
        buy_price = self.trade_record[np.max(list(self.trade_record.keys()))]['start_price']
        current_price = data.close.values[-1]
        if (buy_price - current_price)/buy_price < self.panic:
            return True
        else:
            return self.ma_short.evaluate(data)[-1] < self.ma_long.evaluate(data)[-1]

    def get_params(self, deep=True):
        return {'period_short': self.period_short,
                'period_long': self.period_long,
                'environment': self.env,
                'column_name': self.column_name,
                'panic': self.panic
                }