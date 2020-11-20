from datetime import timedelta, datetime
import pandas as pd
import os 
from pathlib import Path

class Environment():
    def __init__(self, 
                 mode='sim', 
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

        if self.mode == 'sim':
            rootpath = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent
            self.filename = str(rootpath)+'/data/{}-{}-data.csv'.format(self.symbol, self.time_delta)
            self.all_data = self.load_all_data()
            
    def load_all_data(self):
        data = pd.read_csv(self.filename)
        data.loc[:, 'timestamp'] = pd.to_datetime(data.timestamp)
        data = data.sort_values('timestamp')
        self.last_timestamp = data.timestamp.max()
        return data.set_index('timestamp')
        
    def get_data(self):
        return self.all_data.loc[self.start_time:self.current_time, ]

    def step(self):
        self.current_time = self.current_time + timedelta(hours=1)
        if self.current_time >= self.last_timestamp:
            self.end = True
        
    def buy(self):
        pass
    
    def sell(self):
        pass