import matplotlib.pylab as pl
import pandas as pd

def to_pandas(model):
    result_pd = pd.DataFrame(model.trade_record).T
    result_pd.loc[:, 'gan'] = result_pd.apply(lambda row: (row.end_price - row.start_price) * 100 / row.start_price, axis=1)
    result_pd.dropna(inplace=True)
    return result_pd

def plot_line_buysell(model):
    result_pd = to_pandas(model)
    model.env.get_data().close.plot(figsize=(12,5))
    for init, end in zip(result_pd.start_datetime, result_pd.end_datetime):
        pl.axvline(init, color='y')
        pl.axvline(end, color='r')