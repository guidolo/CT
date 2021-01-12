from core.trade_service.traders.base import BaseTrader


class HODL_trader(BaseTrader):
    def restart(self):
        if self.mode != 'sim':
            print('Param mode should be sim')
            self.mode = 'sim'
        self.on_investment = False

    def evaluate_buy(self, data):
        return True

    def evaluate_sell(self, data):
        return self.data_mgr.end_data


