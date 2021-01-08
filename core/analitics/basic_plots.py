import matplotlib.pylab as pl
import pandas as pd
from core.trade_service.traders.base import BaseTrader
from core.trade_service.instruments.scores import price_based_gain_adjusted


def to_pandas(trade_record, gain_function=price_based_gain_adjusted):
    result_pd = pd.DataFrame(trade_record).T
    result_pd.loc[:, 'gain'] = gain_function(result_pd)
    result_pd.dropna(inplace=True)
    return result_pd


def plot_line_buysell(trader: BaseTrader):
    result_pd = to_pandas(trader.trade_record)
    trader.get_data().close.plot(figsize=(12, 5))
    for init, end in zip(result_pd.start_datetime, result_pd.end_datetime):
        pl.axvline(init, color='y')
        pl.axvline(end, color='r')
