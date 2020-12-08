from core.trade_service.traders.MA_Trader import MA_Trader
from datetime import datetime

def test_MA_trader():
    trader = MA_Trader(mode='sim',
                       symbol='BTCUSDT',
                       interval_source='1h',
                       interval_group='1h',
                       period_short=10,
                       period_long=25,
                       panic=-0.03)

    trader.data_mgr.last_timestamp = datetime.fromisoformat('2020-11-04 17:00:00')
    trader.data_mgr.start_time = datetime.fromisoformat('2020-02-01 00:00:00')
    trader.evaluate()
    assert trader.score(1, 1) == 91.63032079837829