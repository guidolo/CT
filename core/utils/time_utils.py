import datetime
import numpy as np

binsizes = {"1m": 1, "15m": 15, "5m": 5, "1h": 60, "1d": 1440}


def seconds_to_next_event(self, interval, plus_seconds=0):
    assert interval in ['5m', '1h'], 'Interval not defined'
    now = datetime.datetime.now()
    if interval == '1h':
        delta = datetime.timedelta(hours=1)
        next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
        sec2next = (next_hour - now).seconds + plus_seconds
    elif interval == '5m':
        delta = datetime.timedelta(minutes=5)
        rangos = np.arange(0, 61, 5)
        min_truncate = np.min(rangos[rangos > now.minute])
        min_truncate = min_truncate if min_truncate != 60 else 0
        next_event = (now + delta).replace(microsecond=0, second=0, minute=min_truncate)
        sec2next = (next_event - now).seconds + plus_seconds
    return sec2next


def get_minutes_from_interval(interval: str):
    return binsizes[interval]
