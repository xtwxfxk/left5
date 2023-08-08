from datetime import datetime
import backtrader as bt

import pandas as pd
from lutils.stock import LTdxHq


class SmaCross(bt.SignalStrategy):
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
        crossover = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

cerebro = bt.Cerebro()
cerebro.addstrategy(SmaCross)

# data0 = bt.feeds.YahooFinanceData(dataname='MSFT', fromdate=datetime(2011, 1, 1), todate=datetime(2012, 12, 31))

from lutils.stock import LTdxHq
code = '603636'
ltdxhq = LTdxHq()
df = ltdxhq.get_k_data_daily(code, end='2021-01-01')
ltdxhq.close()

df = df.rename(columns={'vol': 'volume'})

df.index = pd.to_datetime(df.index)
print(df)
data = bt.feeds.PandasData(dataname=df)


cerebro.adddata(data)

cerebro.run()
cerebro.plot()


