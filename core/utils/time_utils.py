import datetime

binsizes = {"1m": 1, "15m": 15, "5m": 5, "1h": 60, "1d": 1440}

def seconds_to_next_hour(self, plus_seconds=0):
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
    return (next_hour - now).seconds + plus_seconds

def get_minutes_from_interval(interval: str):
    return binsizes[interval]