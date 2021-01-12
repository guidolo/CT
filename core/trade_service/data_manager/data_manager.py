from datetime import datetime, timedelta
import pandas as pd
import os
from pathlib import Path
from core.utils.time_utils import get_minutes_from_interval


class Data_Manager:
    """
    La funcion del Data_Manager es la de proveer data.

    Parameters
    ----------

    regroup_data: bool (default False)
        If True, regroup dataset on interval_group time delta, based on interval_source piece of data
        If False, last piece of data could be incomplete. For example if interval_group is 1h and
        interval_source in 5m, and the current time is 00:17, the last record will contain information
        until 00:15.

    """

    def __init__(self,
                 mode='test',
                 symbol='BTCUSDT',
                 start_time=datetime.fromisoformat('2020-01-01 00:00:00'),
                 end_time=None,
                 interval_minor='5m',
                 interval_major='1h',
                 regroup_data=False
                 ):
        self.mode = mode
        self.symbol = symbol
        self.interval_minor = interval_minor
        self.interval_major = interval_major
        self.regroup_data = regroup_data
        self.minutes_minor = get_minutes_from_interval(interval_minor)
        self.minutes_major = get_minutes_from_interval(interval_major)
        self.start_time = start_time
        self.end_time = end_time
        self.last_timestamp = None
        self.end_data = False
        # TODO pasar todo esta parte de la carga del archivo a un metodo
        rootpath = Path(os.path.dirname(os.path.realpath(__file__))).parent.parent.parent  # TODO crear un setting con los paths
        self.filename_minor = str(rootpath) + '/data/{}-{}-data.csv'.format(self.symbol, self.interval_minor)
        self.filename_major = str(rootpath) + '/data/{}-{}-data.csv'.format(self.symbol, self.interval_major)
        assert self.minutes_minor <= self.minutes_major, 'interval_minor should be lower than interval_mayor'
        assert Path(self.filename_minor).exists(), 'Datasource must exists. Run Data_service to update it'
        assert Path(self.filename_major).exists(), 'Datasource must exists. Run Data_service to update it'
        assert mode in ['PROD', 'test', 'sim'], 'mode should be PROD, test or sim'  # TODO pasar a un exception general
        self._set_data()

    def read_data(self, filename):
        """
            Read data from file
        """
        data = pd.read_csv(filename)
        data.loc[:, 'timestamp'] = pd.to_datetime(data.timestamp)
        data = data.sort_values('timestamp')
        return data.set_index('timestamp')

    def filter_data(self):
        """
            Filters data in case it is necessary
        """
        if self.mode == 'sim' and self.end_time:
            self.data_major = self.data_major.loc[:self.end_time]
            if len(self.data_minor) > 0:
                self.data_minor = self.data_minor.loc[:self.end_time]

    def _set_data(self):
        """
            Set internal dataframes
        """
        if self.interval_major != self.interval_minor:
            self.data_minor = self.read_data(self.filename_minor).loc[self.start_time:]
        else:
            self.data_minor = pd.DataFrame([])
        self.data_major = self.read_data(self.filename_major).loc[self.start_time:]
        self.filter_data()
        self.last_timestamp = self.data_major.index.max()

    def get_data(self):
        """
            return all data available
        """
        if self.mode in ['test', 'PROD']:
            self._set_data()
        return self._manage_data(self.data_minor, self.data_major)

    def get_data_until(self, current_time):
        """
            return data until current_time
        """
        if self.mode in ['test', 'PROD']:
            self._set_data()
        if self.mode == 'sim':
            self._evaluate_EOF(current_time)
        data_minor = self.data_minor.loc[:current_time, ]
        data_major = self.data_major.loc[:current_time, ]
        return self._manage_data(data_minor, data_major)

    def _manage_data(self, data_minor, data_major):
        if self.interval_minor == self.interval_major:
            return data_major
        else:
            if self.regroup_data:
                return self._data_grouped(data_minor, self.minutes_major, self.minutes_minor)
            else:
                if data_minor.index.max() > data_major.index.max():
                    return data_major.append(data_minor.iloc[-1, ])
                else:
                    return data_major

    def _evaluate_EOF(self, current_time):
        if current_time == self.last_timestamp:
            self.end_data = True

    def _data_grouped(self, data, minutes_group, minutes_source, max_records=None):
        data_grouped = []
        window = minutes_group - minutes_source
        end_datetime = data.index.max()
        start_datetime = end_datetime - timedelta(minutes=window)
        data_chunk = data.loc[start_datetime:end_datetime, ]
        max_records = 999_999 if not max_records else max_records
        i = 0
        while len(data_chunk) > 0 and i < max_records:
            data_grouped.append(self._aggregator(data_chunk))
            end_datetime = start_datetime - timedelta(minutes=minutes_source)
            start_datetime = end_datetime - timedelta(minutes=window)
            data_chunk = data.loc[start_datetime:end_datetime, ]
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
