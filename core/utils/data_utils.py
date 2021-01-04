import pandas as pd

binanaceklines_column_names = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                               'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore']


def binanceklines_2_pandas(binance_response):
    data = pd.DataFrame(binance_response, columns=binanaceklines_column_names)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms').astype(str)
    #data.set_index('timestamp', inplace=True)
    return data


