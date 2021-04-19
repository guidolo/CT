import numpy as np


def moving_average(serie, N):
    cumsum, moving_aves = [0], []
    for i, x in enumerate(serie, 1):
        cumsum.append(cumsum[i - 1] + x)
        if i >= N:
            moving_ave = (cumsum[i] - cumsum[i - N]) / N
            moving_aves.append(moving_ave)
    return moving_aves


class MA:
    def __init__(self,
                 data_column: str,
                 period=3
                 ):
        self.data_column = data_column,
        self.period = period

    def evaluate(self, data):
        return data.loc[:, self.data_column].rolling(self.period).mean().values


def WMA(data, column, tf):
    """
        Wilder's Smoothing Technique

        WMAi = WMAi-1 + (Pricei - WMAi-1) / N

        where:
        WMAi - is the WMA value of the current period.
        WMAi-1 - is the value of the period immediately preceding the period being calculated,
        Pricei - is the source (Close or other) price of the current period.
        N - is the number of periods, over which the indicator is calculated.

    """
    moving_values = data.loc[:, column].values
    # counting initial NA
    count_na = 0
    for value in moving_values:
        if np.isnan(value):
            count_na += 1
        else:
            break

    wma = [np.NaN] * (count_na + tf - 1)
    wma.append(np.mean(moving_values[count_na:count_na + tf]))  # First value simply sum of the first tf periods
    i = count_na + tf
    while i < len(moving_values):
        wma.append(wma[-1] + (moving_values[i] - wma[-1]) / tf)
        i += 1
    return np.array(wma)


def EMA(data, column, tf):
    """
    Exponential Moving Averages
    """
    return data.loc[:, column].ewm(span=tf).mean()


def SMA(data, column, tf):
    """
    Simple Moving averages
    """
    return data.loc[:, column].rolling(window=tf).mean()
