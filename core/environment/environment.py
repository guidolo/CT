from datetime import timedelta, datetime
import pandas as pd
import os 
from pathlib import Path
import time
import logging


class Environment:
    def __init__(self, 
                 mode='test',
                 start_time = datetime.fromisoformat('2020-01-01 00:00:00'), 
                 symbol='BTCUSDT',
                 time_delta='1h'
                ):
        self.mode = mode
        self.symbol=symbol
        self.time_delta=time_delta
        self.start_time = start_time
        self.current_time = start_time
        self.last_timestamp = None
        self.end = False
        rootpath = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent
        self.filename = str(rootpath)+'/data/{}-{}-data.csv'.format(self.symbol, self.time_delta)
        assert mode in ['PROD', 'test'], 'mode should be PROD or test'
        assert Path(self.filename).exists(), 'Datasource must exists'
        self.all_data = self.load_all_data()
            
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
            logging.info('env - step: waiting for {} minutes'.format(minutes*60))
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
            logging.info('env: Buying')
            return True
        else:
            return False
    
    def sell(self):
        if self.mode == 'PROD':
            logging.info('env: Selling')
            return True
        else:
            return False

