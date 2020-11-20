from .base import BaseTrader

class UpperLower_trader():
    def __init__(self, 
                 environment,
                 num_to_buy=3,
                 num_to_sell=1,
                ):
        self.on_investment = False
        self.env = environment
        self.num_to_buy = num_to_buy
        self.num_to_sell = num_to_sell
        self.trade_num=0
        self.trade_record={}
    
    def evaluate_buy(self, data):
        return ~((data.close[-self.num_to_buy:].diff()>0)[1:]==False).any()
        
    def evaluate_sell(self, data):
        return ~((data.close[-self.num_to_sell:].diff()<0)[1:]==False).any()
        
    def evaluate(self):        
        while self.env.end == False:
            data = self.env.get_data()
            if self.on_investment:
                if self.evaluate_sell(data):
                    self.env.sell()
                    self.on_investment = False
                    self.trace('sell', data)
            else:
                if self.evaluate_buy(data):
                    self.env.buy()
                    self.on_investment = True
                    self.trace('buy', data)
            self.env.step()
            
    def trace(self, mode, data):
        if mode == 'buy':
            self.trade_record.update({self.trade_num:{'start_datetime':self.env.current_time,
                                                 'start_price':data.close.iloc[-1]
                                                }
                                     })
        elif mode=='sell':
            self.trade_record.get(self.trade_num).update({'end_datetime':self.env.current_time,
                                                     'end_price':data.close.iloc[-1]
                                                    })
            self.trade_num +=1
            
class Point2Point_trader(BaseTrader):
    def __init__(self, 
                 environment,
                ):
        self.on_investment = False
        self.env = environment
        self.trade_num=0
        self.trade_record={}
    
    def evaluate_buy(self, data):
        return ~self.on_investment
        
    def evaluate_sell(self, data):
        return False

    def evaluate(self):
        while self.env.end == False:
            data = self.env.get_data()
            if self.on_investment:
                if self.evaluate_sell(data):
                    self.env.sell()
                    self.on_investment = False
                    self.trace('sell', data)
            else:
                if self.evaluate_buy(data):
                    self.env.buy()
                    self.on_investment = True
                    self.trace('buy', data)
            self.env.step()
        self.trace('sell', data)

            
class Percentage_trader():
    def __init__(self, 
                 environment,
                 perc_to_buy=0.1,
                 window_to_buy=3,
                 perc_to_sell=-0.1,
                 window_to_sell=1
                ):
        self.on_investment = False
        self.env = environment
        self.perc_to_buy = perc_to_buy
        self.window_to_buy = window_to_buy
        self.perc_to_sell = perc_to_sell
        self.window_to_sell = window_to_sell
        self.trade_num=0
        self.trade_record={}
    
    def evaluate_buy(self, data):
        if len(data) >= self.window_to_buy:
            temp_data = self.env.get_data().close
            return (temp_data[-1] - temp_data[-self.window_to_buy]) / temp_data[-self.window_to_buy] >= self.perc_to_buy
        
    def evaluate_sell(self, data):
        temp_data = self.env.get_data().close
        return (temp_data[-1] - temp_data[-self.window_to_sell]) / temp_data[-self.window_to_sell] <= self.perc_to_sell
        
    def evaluate(self):        
        while self.env.end == False:
            data = self.env.get_data()
            if self.on_investment:
                if self.evaluate_sell(data):
                    self.env.sell()
                    self.on_investment = False
                    self.trace('sell', data)
            else:
                if self.evaluate_buy(data):
                    self.env.buy()
                    self.on_investment = True
                    self.trace('buy', data)
            self.env.step()
            
    def trace(self, mode, data):
        if mode == 'buy':
            self.trade_record.update({self.trade_num:{'start_datetime':self.env.current_time,
                                                 'start_price':data.close.iloc[-1]
                                                }
                                     })
        elif mode=='sell':
            self.trade_record.get(self.trade_num).update({'end_datetime':self.env.current_time,
                                                     'end_price':data.close.iloc[-1]
                                                    })
            self.trade_num +=1