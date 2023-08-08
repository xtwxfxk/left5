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
        code = '000032' # 000032 300142 603636 600519
        ltdxhq = LTdxHq()
        # df = ltdxhq.get_k_data_daily('603636', start='2021-09-01')
        # df = ltdxhq.get_k_data_1min('000032', start='2021-08-31') # 000032 300142 603636 600519
        df = ltdxhq.get_k_data_daily(code, start='2021-01-01')
        df = ltdxhq.to_qfq(code, df)
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
            data.append([index[:10], row.open, row.high, row.low, row.close, row.volume,])

        self.model = PPO.load('ppo_stock')

        for current_step in range(10, df.shape[0]):
            print(current_step)
            obs = np.array([
                df.iloc[current_step - NEXT_OBSERVATION_SIZE: current_step]['open'].values / MAX_SHARE_PRICE,
                df.iloc[current_step - NEXT_OBSERVATION_SIZE: current_step]['high'].values / MAX_SHARE_PRICE,
                df.iloc[current_step - NEXT_OBSERVATION_SIZE: current_step]['low'].values / MAX_SHARE_PRICE,
                df.iloc[current_step - NEXT_OBSERVATION_SIZE: current_step]['close'].values / MAX_SHARE_PRICE,
                df.iloc[current_step - NEXT_OBSERVATION_SIZE: current_step ]['volume'].values / MAX_NUM_SHARES,
                df.iloc[current_step - NEXT_OBSERVATION_SIZE: current_step ]['amount'].values / MAX_NUM_SHARES,
                # df['close'].pct_change().fillna(0)[current_step: current_step + NEXT_OBSERVATION_SIZE],

                df['macd'][current_step - NEXT_OBSERVATION_SIZE: current_step].values,
                df['macdh'][current_step - NEXT_OBSERVATION_SIZE: current_step].values,
                df['macds'][current_step - NEXT_OBSERVATION_SIZE: current_step].values,
                df['kdjk'][current_step - NEXT_OBSERVATION_SIZE: current_step].values,
                df['kdjd'][current_step - NEXT_OBSERVATION_SIZE: current_step].values,
                df['kdjj'][current_step - NEXT_OBSERVATION_SIZE: current_step].values,
                df['rsi_6'][current_step - NEXT_OBSERVATION_SIZE: current_step].fillna(0).values,
                df['rsi_12'][current_step - NEXT_OBSERVATION_SIZE: current_step].fillna(0).values,
            ])

            # df.index.values[current_step][:10]
            self.kline.append([df.index.get_level_values(level=0)[current_step], df.iloc[current_step].open, df.iloc[current_step].high, df.iloc[current_step].low, df.iloc[current_step].close, df.iloc[current_step].volume])

            self.backtest.initialize(self.kline, data)
            self.begin(obs)

        print(self.buy_signal)
        print(self.sell_signal)
        plot_asset()
        plot_signal(self.kline, self.buy_signal, self.sell_signal, df['macd'].values)

    def begin(self, obs):
        if CurrentBar(self.kline) < 30:
            return

        action, state = self.model.predict(obs, state=None, deterministic=True)
        # print(action)
        if Actions.Buy.value == action and self.backtest.long_quantity == 0:
            self.backtest.buy(
                price = self.backtest.close + 0.02,
                amount = self.asset / self.backtest.close,
                long_quantity = self.asset / self.backtest.close,
                long_avg_price = self.backtest.close,
                profit = 0,
                asset = self.asset
            )
            self.buy_signal.append(self.backtest.high)
            # self.sell_signal.append(0)
        elif Actions.Sell.value == action and self.backtest.long_quantity !=0:
            profit = (self.backtest.close - self.backtest.long_avg_price) * self.backtest.long_quantity
            self.asset += profit
            self.backtest.sell(
                price = self.backtest.close - 0.02,
                amount = self.backtest.long_quantity,
                long_quantity = 0,
                long_avg_price = 0,
                profit = profit,
                asset = self.asset
            )
            # self.buy_signal.append(0)
            # self.sell_signal.append(1)
            self.sell_signal.append(self.backtest.low)
        # else:
            # self.buy_signal.append(0)
            # self.sell_signal.append(0)

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