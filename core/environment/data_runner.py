from core.environment.data_updater import Data_Updater
import time
import datetime
import logging



def seconds_to_next_hour(self, plus=0):
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    next_hour = (now + delta).replace(microsecond=0, second=0, minute=2)
    return (next_hour - now).seconds + plus


if __name__ == '__main__':
    logging.info('Start Data Runner')
    data_mgr = Data_Updater(symbol='BTCUSDT', time_interval='1h')
    logging.info('First update: {}'.format(data_mgr.update_data()))
    logging.info('Sleep for {} minutes'.format(seconds_to_next_hour(2)/60))
    time.sleep(seconds_to_next_hour(2))
    logging.info('Init while')
    while True:
        if data_mgr.update_data():
            logging.info('Success update. See you in aprox one hour')
            time.sleep(seconds_to_next_hour(2))
        else:
            logging.info('Fail to update')
            time.sleep(60)
