import datetime

def seconds_to_next_hour(self, plus_seconds=0):
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
    return (next_hour - now).seconds + plus_seconds

