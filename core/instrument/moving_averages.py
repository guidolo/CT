import pandas as pd
import numpy as np

def moving_average(serie, N):
    cumsum, moving_aves = [0], []
    for i, x in enumerate(serie, 1):
        cumsum.append(cumsum[i-1] + x)
        if i>=N:
            moving_ave = (cumsum[i] - cumsum[i-N])/N
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
        #return moving_average(data.loc[:, self.data_column].values, self.period)
        return data.loc[:, self.data_column].rolling(self.period).mean().values
