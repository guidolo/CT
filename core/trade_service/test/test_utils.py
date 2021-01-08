from core.utils.time_utils import seconds_to_next_event
from datetime import datetime


def test_seconds_to_next_event():
    now = datetime.fromisoformat('2021-01-01 00:00:00')
    assert seconds_to_next_event('5m', 0, now) == 60 * 5
    now = datetime.fromisoformat('2021-01-01 00:03:00')
    assert seconds_to_next_event('5m', 0, now) == 60 * 2
    now = datetime.fromisoformat('2021-01-01 00:33:00')
    assert seconds_to_next_event('5m', 0, now) == 60 * 2
    now = datetime.fromisoformat('2021-01-01 00:57:00')
    assert seconds_to_next_event('5m', 0, now) == 60 * 3
    now = datetime.fromisoformat('2021-01-01 00:57:00')
    assert seconds_to_next_event('10m', 0, now) == 60 * 3
    now = datetime.fromisoformat('2021-01-01 00:01:00')
    assert seconds_to_next_event('15m', 0, now) == 60 * 14