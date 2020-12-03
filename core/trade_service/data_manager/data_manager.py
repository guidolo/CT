from datetime import datetime, timedelta
import pandas as pd
import os
from pathlib import Path
from core.utils.time_utils import get_minutes_from_interval


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
        self.minutes_source = get_minutes_from_interval(interval_source)
        self.minutes_group = get_minutes_from_interval(interval_group)
        self.start_time = start_time
        self.last_timestamp = None
        self.end_data = False
        # TODO pasar todo esta parte de la carga del archivo a un metodo
        rootpath = Path(
            os.path.dirname(os.path.realpath(__file__))).parent.parent.parent  # TODO crear un setting con los paths
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
                data = self.all_data.loc[self.start_time:current_time, ]
        else:
            print('Warning!, Current time param is not used') if current_time else None
            data = self.load_all_data().loc[self.start_time:]
        if self.interval_source == self.interval_group:
            return data
        else:
            return self._data_grouped(data, self.minutes_group, self.minutes_source)

    def _data_grouped(self, data, minutes_group, minutes_source, max_records=None):
        data_grouped = []
        minutes_diff = minutes_group - minutes_source
        end_datetime = data.index.max()
        start_datetime = end_datetime - timedelta(minutes=minutes_diff)
        data_chunk = data.loc[start_datetime:end_datetime, ]
        max_records = 999_999 if not max_records else max_records
        i = 0
        while len(data_chunk) > 0 and i < max_records:
            start_datetime = end_datetime - timedelta(minutes=minutes_diff)
            data_chunk = data.loc[start_datetime:end_datetime, ]
            data_grouped.append(self._aggregator(data_chunk))
            end_datetime = start_datetime - timedelta(minutes=minutes_source)
            i += 1
        return pd.concat(data_grouped)

    def _aggregator(self, data_chunk):
        return pd.DataFrame({data_chunk.index[-1]: data_chunk.agg({'open': lambda x: x[0],
                                                                   'high': max,
                                                                   'low': min,
                                                                   'close': lambda x: x[-1],
                                                                   'volume': sum,
                                                                   'close_time': lambda x: x[-1],
                                                                   'quote_av': sum,
                                                                   'trades': sum,
                                                                   'tb_base_av': sum,
                                                                   'tb_quote_av': sum
                                                                   }
                                                                  )}).T

    def restart(self):
        if self.mode == 'sim':
            self.end_data = False
        else:
            print('Warning!! PROD mode can`t restart')
        return self
