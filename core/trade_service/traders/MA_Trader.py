import numpy as np
from datetime import datetime
from core.trade_service.traders.base import BaseTrader
from core.trade_service.instruments.moving_averages import MA


class MA_Trader(BaseTrader):
    def __init__(self,
                 mode='test',
                 symbol='BTCUSDT',
                 interval_source='5m',
                 interval_group='1h',
                 on_investment: bool = False,
                 column_name: str = 'close',
                 period_short: int = 3,
                 period_long: int = 10,
                 panic=-0.01,
                 start_time=datetime.fromisoformat('2020-01-01 00:00:00')
                 ):
        super().__init__(mode, symbol, interval_source, interval_group, start_time, on_investment)
        self.period_short = period_short
        self.period_long = period_long
        self.column_name = column_name
        self.ma_short: MA
        self.ma_long: MA
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
        # evaluate panic
        buy_price = self.trade_record[np.max(list(self.trade_record.keys()))]['start_price']
        current_price = data.close.values[-1]
        gain = (current_price - buy_price) / buy_price
        if gain < self.panic:
            #print(str(data.index[-1]) + ' TRUE ' +f'buy_price {buy_price}, current_price {current_price}, gain {gain}')
            return True
        else:
            #print(str(data.index[-1]) + ' FALSE ' + f'buy_price {buy_price}, current_price {current_price}, gain {gain}')
            return self.ma_short.evaluate(data)[-1] < self.ma_long.evaluate(data)[-1]

    def get_params(self, deep=True):
        return {'mode': self.mode,
                'symbol': self.symbol,
                'interval_source': self.interval_source,
                'interval_group': self.interval_group,
                'on_investment': self.on_investment,
                'period_short': self.period_short,
                'period_long': self.period_long,
                'column_name': self.column_name,
                'panic': self.panic
                }
