def price_based_gain_adjusted(row):
    return (row.end_price * 0.999 - row.start_price * 1.001) * 100 / row.start_price

def gain_simulation(result, comission = 0.001, debug=False):
    multiplier = 1-comission
    invest = 10000
    print(invest) if debug else None
    for start, end in zip(result.start_price.values, result.end_price.values):
        btcq = invest * multiplier / start
        usdq = btcq * multiplier * end
        invest = usdq
        print(invest) if debug else None
    return ((invest/10000)-1)*100

