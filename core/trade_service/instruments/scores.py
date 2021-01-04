def price_based_gain_adjusted(row):
    return (row.end_price * 0.999 - row.start_price * 1.001) * 100 / row.end_price


