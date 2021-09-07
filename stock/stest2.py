from stockquant.quant import *

from enum import Enum
from stockstats import StockDataFrame
from stable_baselines3 import PPO
import numpy as np
import pandas as pd

from lutils.stock import LTdxHq

config.loads('config.json')


symbol = 'sh603636'

# print(Market.tick(symbol))


MAX_ACCOUNT_BALANCE = 2147483647
MAX_NUM_SHARES = 2147483647
MAX_NUM_AMOUNTS = 2147483647
MAX_SHARE_PRICE = 5000
MAX_OPEN_POSITIONS = 60
MAX_STEPS = 240 # 40000
NEXT_OBSERVATION_SIZE = 10

class Actions(Enum):
    Hold = 0
    Sell = 1
    Buy = 2

class Strategy:

    def __init__(self):
        config.loads('config.json')
        self.asset = 10000
        self.backtest = BackTest()

        # data = Market.kline('sh600519', '1d')
        # print(data)
        ltdxhq = LTdxHq()
        df = ltdxhq.get_k_data_daily('300142', start='2019-01-01') # 000032 300142 603636 600519
        df = StockDataFrame(df)
        ltdxhq.close()
        # print(df.head())

        self.kline = []
        self.buy_signal = []
        self.sell_signal = []

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

        self.model = PPO.load('ppo_stock')

        for current_step in range(0, df.shape[0] - NEXT_OBSERVATION_SIZE):
            obs = np.array([
                df.iloc[current_step: current_step + NEXT_OBSERVATION_SIZE]['open'].values / MAX_SHARE_PRICE,
                df.iloc[current_step: current_step + NEXT_OBSERVATION_SIZE]['high'].values / MAX_SHARE_PRICE,
                df.iloc[current_step: current_step + NEXT_OBSERVATION_SIZE]['low'].values / MAX_SHARE_PRICE,
                df.iloc[current_step: current_step + NEXT_OBSERVATION_SIZE]['close'].values / MAX_SHARE_PRICE,
                df.iloc[current_step: current_step + NEXT_OBSERVATION_SIZE]['vol'].values / MAX_NUM_SHARES,

                df['macd'][current_step: current_step + NEXT_OBSERVATION_SIZE].values,
                df['macdh'][current_step: current_step + NEXT_OBSERVATION_SIZE].values,
                df['macds'][current_step: current_step + NEXT_OBSERVATION_SIZE].values,
                df['kdjk'][current_step: current_step + NEXT_OBSERVATION_SIZE].values,
                df['kdjd'][current_step: current_step + NEXT_OBSERVATION_SIZE].values,
                df['kdjj'][current_step: current_step + NEXT_OBSERVATION_SIZE].values,
                df['rsi_6'][current_step: current_step + NEXT_OBSERVATION_SIZE].fillna(0).values,
                df['rsi_12'][current_step: current_step + NEXT_OBSERVATION_SIZE].fillna(0).values,
            ])

            self.kline.append([df.index.values[current_step][:10], df.iloc[current_step].open, df.iloc[current_step].high, df.iloc[current_step].low, df.iloc[current_step].close, df.iloc[current_step].vol])

            self.backtest.initialize(self.kline, data)
            self.begin(obs)
        plot_asset()
        plot_signal(self.kline, self.buy_signal, self.sell_signal, df['macd'].values)

    def begin(self, obs):
        if CurrentBar(self.kline) < 30:
            return

        action, state = self.model.predict(obs, state=None, deterministic=True)
        if Actions.Buy.value == action and self.backtest.long_quantity == 0:
            self.backtest.buy(
                price = self.backtest.close,
                amount = self.asset / self.backtest.close,
                long_quantity = self.asset / self.backtest.close,
                long_avg_price = self.backtest.close,
                profit = 0,
                asset = self.asset
            )
            self.buy_signal.append(1)
            self.sell_signal.append(0)
        elif Actions.Sell.value == action and self.backtest.long_quantity !=0:
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
            self.buy_signal.append(0)
            self.sell_signal.append(1)
        else:
            self.buy_signal.append(0)
            self.sell_signal.append(0)

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