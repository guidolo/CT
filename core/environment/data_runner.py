from core.environment.data_updater import Data_Updater
import time
import logging
from core.utils.time_utils import seconds_to_next_hour

logging.basicConfig(filename='data_runner.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)


if __name__ == '__main__':
    logging.info('Start Data Runner')
    data_mgr = Data_Updater(symbol='BTCUSDT', time_interval='1h')
    logging.info('Init while')
    while True:
        if data_mgr.update_data():
            logging.info('Success update. See you in aprox one hour')
            time.sleep(seconds_to_next_hour(10))
        else:
            logging.info('Fail to update. Waiting 1 minute.')
            time.sleep(60)
