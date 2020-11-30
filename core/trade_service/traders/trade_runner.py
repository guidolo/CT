import logging
from core.trade_service.traders.MA_Trader import MA_Trader
from core.trade_service.data_manager.data_manager import Data_Manager
from datetime import datetime

# TODO mover a algun lugar comun
logging.basicConfig(filename='trade_service.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

env = Data_Manager(mode='PROD',
                   start_time=datetime.fromisoformat('2020-02-01 00:00:00'),
                   symbol='BTCUSDT',
                   interval_source='5m',
                   interval_group='1h')

model = MA_Trader(environment=env,
                  on_investment=True,
                  column_name='close',
                  period_long=25,
                  period_short=14,
                  panic=-0.03)

if __name__ == '__main__':
    model.evaluate()
