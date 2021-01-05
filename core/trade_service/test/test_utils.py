from core.utils.time_utils import seconds_to_next_event
from datetime import datetime


def test_seconds_to_next_event():
    now = datetime.fromisoformat('2021-01-01 00:00:0000')
    assert seconds_to_next_event('5m', 0, now) == 60 * 5
