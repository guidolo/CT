import logging
from core.traders.MA_Trader import MA_Trader
from core.environment.environment import  Environment
from datetime import datetime

logging.basicConfig(filename='trade_runner.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

env = Environment(mode='test',
                  start_time=datetime.fromisoformat('2020-02-01 00:00:00'),
                  symbol='BTCUSDT',
                  time_delta='1h')

model = MA_Trader(environment=env,
                  on_investment=False,
                  column_name='close',
                  period_long=25,
                  period_short=14,
                  panic=-0.03)

if __name__ == '__main__':
    model.evaluate()
