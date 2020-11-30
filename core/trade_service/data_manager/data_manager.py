from datetime import datetime
import pandas as pd
import os
from pathlib import Path


class Data_Manager:
    """
    La funcion del Data_Manager es la de proveer data.
    """

    def __init__(self,
                 mode='test',
                 symbol='BTCUSDT',
                 start_time=datetime.fromisoformat('2020-01-01 00:00:00'),
                 interval_source='5m',
                 interval_group='1h',
                 ):
        self.mode = mode
        self.symbol = symbol
        self.interval_source = interval_source
        self.interval_group = interval_group
        self.start_time = start_time
        self.last_timestamp = None
        self.end_data = False
        #TODO pasar todo esta parte de la carga del archivo a un metodo
        rootpath = Path(
            os.path.dirname(os.path.realpath(__file__))).parent.parent  # TODO crear un setting con los paths
        self.filename = str(rootpath) + '/data/{}-{}-data.csv'.format(self.symbol, self.interval_source)
        assert Path(self.filename).exists(), 'Datasource must exists. Run Data_service to update it'
        self.all_data = self.load_all_data()
        assert mode in ['PROD', 'test', 'sim'], 'mode should be PROD, test or sim'  # TODO pasar a un exception general

    def load_all_data(self):
        data = pd.read_csv(self.filename)
        data.loc[:, 'timestamp'] = pd.to_datetime(data.timestamp)
        data = data.sort_values('timestamp')
        self.last_timestamp = data.timestamp.max()
        return data.set_index('timestamp')

    def get_data(self, current_time=None):
        if self.mode == 'sim':
            if not current_time:
                raise ValueError
            else:
                if current_time == self.last_timestamp:
                    self.end_data = True
                    return self.all_data.loc[self.start_time:current_time, ]
        else:
            return self.load_all_data().loc[self.start_time:]

    def restart(self):
        if self.mode == 'sim':
            self.end_data = False
        else:
            print('Warning!! PROD mode can`t restart')
        return self
