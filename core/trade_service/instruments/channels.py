import numpy as np
from core.trade_service.instruments.moving_averages import EMA

def TR_single(row):
    """
    True value
    """
    return max(
        np.abs(row.high - row.low),
        np.abs(row.high - row.close_lag1),
        np.abs(row.close_lag1 - row.low)
    )


def TR(data):
    """True Value for N values"""
    data.loc[:, 'close_lag1'] = data.close.shift()
    return data.apply(TR_single, axis=1)


def ATR(data, atr_tf=10):
    """
    Average True Value
    https://en.wikipedia.org/wiki/Average_true_range

    """
    data = data.copy()
    atr = [np.NaN] * (atr_tf - 1)
    tr = TR(data)
    atr.append(np.mean(tr[:atr_tf]))  # first values is the median of the first tf values
    i = atr_tf
    while i < len(data):
        atr.append(((atr[-1] * (atr_tf - 1)) + tr[i]) / atr_tf)
        i += 1
    return np.array(atr)

def KELT(data, atr_tf=20, ema_tf=14, band_width=1):
    """
    Keltner Channel
        https://en.wikipedia.org/wiki/Keltner_channel
        https://www.youtube.com/watch?v=7PDUdm7inRk
    """
    data = data.copy()
    atr = ATR(data, atr_tf)
    data.loc[:, 'ATR'] = atr
    ema = np.array(EMA(data, 'close', tf=ema_tf))
    return ema + band_width*atr, ema, ema - band_width*atr