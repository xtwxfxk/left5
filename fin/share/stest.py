from stockquant.quant import *

from lutils.stock import LTdxHq

config.loads('config.json')


symbol = 'sh603636'

# print(Market.tick(symbol))

class Strategy:

    def __init__(self):
        config.loads('config.json')
        self.asset = 10000
        self.backtest = BackTest()

        # data = Market.kline('sh600519', '1d')
        # print(data)
        ltdxhq = LTdxHq()
        df = ltdxhq.get_k_data_daily('600519', start='2018-01-01') # 000032 300142 603636 600519
        ltdxhq.close()
        # print(df.head())

        self.kline = []

        # 2005-08-11 15:00 
        # open            46.01
        # close           47.37
        # high            47.40
        # low             46.01
        # vol        1359360.00
        # amount    63589532.00
        data = []
        for index, row in df.iterrows():
            data.append([index[:10], row.open, row.high, row.low, row.close, row.vol,])

        for k in data:
            self.kline.append(k)
            self.backtest.initialize(self.kline, data)
            self.begin()
        plot_asset()

    def begin(self):
        if CurrentBar(self.kline) < 30:
            return

        ma20 = MA(20, self.kline)
        ma30 = MA(30, self.kline)
        cross_over = ma20[-1] > ma30[-1] and ma20[-2] <= ma30[-2]
        cross_down = ma20[-1] < ma30[-1] and ma20[-2] >= ma30[-2]

        if cross_over and self.backtest.long_quantity == 0:
            self.backtest.buy(
                price = self.backtest.close,
                amount = self.asset / self.backtest.close,
                long_quantity = self.asset / self.backtest.close,
                long_avg_price = self.backtest.close,
                profit = 0,
                asset = self.asset
            )
        elif cross_down and self.backtest.long_quantity !=0:
            profit = (self.backtest.close - self.backtest.long_avg_price) * self.backtest.long_quantity
            self.asset += profit
            self.backtest.sell(
                price = self.backtest.close,
                amount = self.backtest.long_quantity,
                long_quantity = 0,
                long_avg_price = 0,
                profit = profit,
                asset = self.asset
            )

        if self.backtest.long_quantity > 0 and self.backtest.low <= self.backtest.long_avg_price * .9:
            profit = (self.backtest.low - self.backtest.long_avg_price) * self.backtest.long_quantity
            self.asset += profit
            self.backtest.sell(
                price = self.backtest.long_avg_price * .9,
                amount = self.backtest.long_quantity,
                long_quantity = 0,
                long_avg_price = 0,
                profit = profit,
                asset = self.asset
            )

if __name__ == '__main__':
    strategy = Strategy();