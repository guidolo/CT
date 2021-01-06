from core.trade_service.data_manager.data_manager import Data_Manager
from datetime import datetime, timedelta


def test_test_mode():
    dm = Data_Manager(mode='test', symbol='BTCUSDT', interval_source='1h', interval_group='1h')
    return len(dm.get_data()) > 0


def test_length_sim_mode():
    """testea que el datamanager devuelva data"""
    dm = Data_Manager(mode='sim', symbol='BTCUSDT', interval_source='1h', interval_group='1h')
    lengths = []
    for hour in range(1, 25):
        current_datetime = datetime.fromisoformat('2020-01-01 00:00:00') + timedelta(hours=hour)
        temp_data = dm.get_data_to(current_datetime)
        lengths.append(len(temp_data))
    return lengths == [13, 25, 37, 49, 61, 73, 85, 97, 109, 121, 133, 145, 157, 169, 181, 193, 205, 217, 229, 241, 253,
                       265, 277, 289]


def test_close_sim_mode():
    """testea que el datamanager devuelva data correcta"""
    dm = Data_Manager(mode='sim', symbol='BTCUSDT',  interval_source='1h', interval_group='1h')
    close_total = 0
    for hour in range(1, 25):
        current_datetime = datetime.fromisoformat('2020-01-01 00:00:00') + timedelta(hours=hour)
        temp_data = dm.get_data_to(current_datetime)
        close_total += temp_data.close.sum()
    return close_total == 26150233.04
