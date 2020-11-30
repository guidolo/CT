from core.data_service.data_updater import Data_Updater
import time
import logging
from core.utils.time_utils import seconds_to_next_event
import argparse

logging.basicConfig(filename='data_service.log',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols",
                        default=["BTCUSDT"],
                        help="List of crypto symbols. defualt(['BTCUSDT'])",
                        nargs="+")
    parser.add_argument("--interval",
                        default="1h",
                        help="Interval of time to refresh",
                        type=str)
    args = parser.parse_args()


    logging.info('Start Data Runner')
    interval = args.interval
    assert len(args.symbols) == 1, 'Only 1 symbol is accepted so far' ##TODO make multi symbol
    for symbol in args.symbols:
        logging.info('Lunching {} with time interval {}'.format(symbol, interval))
        data_updater = Data_Updater(symbol=symbol, time_interval=interval)
        logging.info('Init while')
        while True:
            if data_updater.update_data():
                logging.info('Success update.')
                logging.info('Sleep aprox {}'.format(interval))
                time.sleep(seconds_to_next_event(interval, plus_seconds=10))
            else:
                logging.info('Fail to update. Waiting 1 minute.')
                time.sleep(60)
