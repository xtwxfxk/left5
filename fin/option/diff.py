# -*- coding: utf-8 -*-

import os, re, datetime, gc
import pandas as pd
import numpy as np
import mplfinance as mpf
import matplotlib.pyplot as plt
import seaborn as sn

import plotly.graph_objects as go
from lutils.fin.data_loader import load, load_ohlc

QT_TICK_ROOT = 'Z:/tq_data/ticks'

symbols_keep = ['SHFE.rb', 'SHFE.al', 'DCE.v', 'DCE.pp', 'DCE.m', 'DCE.c', 'DCE.b', 'DCE.a', 'CZCE.ma']

# FUTURE_RE = '[A-Z]+\.[a-zA-Z]+(\d+)\.h5' #'[A-Z]+\.[a-zA-Z]+[0-9]+\.h5'


all_files = os.listdir(QT_TICK_ROOT)
all_files.sort()

def filter_futures():
    futures = []
    for file_name in all_files:
        match = re.findall(r'[A-Z]+\.[a-zA-Z]+(\d+)\.h5', file_name)
        if match and file_name.startswith('SHFE.rb'):
            year = match[0]
            if len(year) == 3:
                year = '2%s' % year
            year = int(year)
            if year > 2305 or year < 2105:
                pass
            else:
                futures.append(file_name)
    return futures



def filter_options():
    futures = filter_futures()
    future_options = {}
    for future in futures:
        print(future)
        option_call_re = '%s\-?C\-?[0-9]+\.h5' % future[:-3]
        option_put_re = '%s\-?P\-?[0-9]+\.h5' % future[:-3]

        option_calls = []
        option_puts = []

        for file_name in all_files:
            match = re.findall(r'\S(\d+)\-?[C|P]\-?(\d+).h5', file_name)

            if match:
                [(year, price)] = match
                if len(year) == 3:
                    year = '2%s' % year
                year = int(year)
                price = int(price)

                match = re.match(option_call_re, file_name)
                if match:
                    exchange, symbol = file_name.split('.')[:2]
                    option_calls.append([exchange, symbol, year, price])

                match = re.match(option_put_re, file_name)
                if match:
                    exchange, symbol = file_name.split('.')[:2]
                    option_puts.append([exchange, symbol, year, price])

        option_calls.sort()
        option_puts.sort()

        future_options[future] = [option_calls, option_puts]
    return future_options


# mpf.plot(df,type='candle',style='yahoo',savefig=filename)
class Diff():

    def __init__(self, future, call_options, put_options, start_days=30):
        self.future = future
        self.call_options = call_options
        self.put_options = put_options

        self.exchange, self.symbol = self.future.split('.')[:2]
        self.start_days = start_days

        # self.underlying = None
        # self.calls = {}
        # self.puts = {}

        # self.load_data()

        self.hl_mean = 0

        self.load_data()
        self.sublect_hl_mean()
        self.iter_options()

    def sublect_hl_mean(self):

        self.underlying['hl'] = (self.underlying.high + self.underlying.low) / 2
        self.underlying['hl_mean'] = self.underlying.hl.rolling(self.start_days, min_periods=1).mean()

        start_time = self.underlying.iloc[-1].name - datetime.timedelta(days=(self.start_days - 10))

        self.hl_mean = self.underlying[self.underlying.index >= start_time].iloc[0].hl_mean
        self.hl_mean = self.hl_mean * 0.9


    def load_data(self):
        self.load_underlying()
        self.load_calls()
        # self.load_puts()


    def load_underlying(self):
        self.underlying = self.load_df(self.exchange, self.symbol)

    def load_calls(self):
        self.calls = {}
        for exchange, symbol, year, price in self.call_options:
            self.calls['%s.%s' % (exchange, symbol)] = self.load_df(exchange, symbol)

    def load_puts(self):
        self.puts = {}
        for exchange, symbol, year, price in self.put_options:
            self.puts['%s.%s' % (exchange, symbol)] = self.load_df(exchange, symbol)



    def load_df(self, exchange, symbol):
        df = load(exchange, symbol)
        df.index = df.datetime
        resample_ohlc_min = df['last_price'].resample('1Min', closed='left', label='right').ohlc(_method='ohlc')
        resample_volume_min = df['volume'].resample('1Min', closed='left', label='right').sum()
        resample_amount_min = df['amount'].resample('1Min', closed='left', label='right').sum()
        df_min = pd.concat([resample_ohlc_min, resample_volume_min, resample_amount_min], axis=1).dropna()

        return df_min


    def iter_options(self):

        for i, (exchange1, symbol1, year1, price1) in enumerate(self.call_options):
            if self.hl_mean and self.hl_mean > 0 and price1 > self.hl_mean:
                for (exchange2, symbol2, year2, price2) in self.call_options[i + 1:]:

                    print('%s.%s - %s.%s' % (exchange1, symbol1, exchange2, symbol2))

                    df1 = self.calls['%s.%s' % (exchange1, symbol1)]
                    df2 = self.calls['%s.%s' % (exchange2, symbol2)]

                    diff_df = df1.sub(df2).dropna() # 贵的 - 便宜的
                    if not diff_df.empty and diff_df.shape[0] > 12000:
                        self.saveflg(self.underlying, diff_df, '%s.%s' % (self.exchange, self.symbol), '%s.%s - %s.%s' % (exchange1, symbol1, exchange2, symbol2))


    
    def saveflg(self, df1, df2, df1_name, df2_name):
        c = df2.shape[0]
        fig = mpf.figure(style='yahoo', figsize=(12,9))
        # ax1 = fig.add_subplot(2, 1, 1)
        # ax2 = fig.add_subplot(2, 1, 2)

        ax1 = fig.add_subplot(3, 1, 1)
        ax2 = fig.add_subplot(3, 1, 2)
        ax3 = fig.add_subplot(3, 3, 7)
        ax4 = fig.add_subplot(3, 3, 8)
        ax5 = fig.add_subplot(3, 3, 9)

        end_time = df2.iloc[-1].name
        start_time = df2.iloc[-1].name - datetime.timedelta(days=35)

        _df1 = df1.loc[(df1.index > start_time) & (df1.index <= end_time)]
        _df2 = df2.loc[(df2.index > start_time) & (df2.index <= end_time)]

        _df1, _df2 = _df1.align(_df2, join="outer", axis=0)

        _df1 = _df1.ffill().bfill()
        _df2 = _df2.ffill().bfill()

        mpf.plot(_df1, ax=ax1, type='line', axtitle='%s %.02f %s %s' % (c, self.hl_mean, df1_name, df2_name), volume=False, mav=(3,6,9), figratio=(3,1), style='yahoo', datetime_format='%Y-%m-%d %H:%M')
        mpf.plot(_df2, ax=ax2, type='line', axtitle='', volume=False, mav=(3,6,9), figratio=(3,1), style='yahoo', datetime_format='%Y-%m-%d %H:%M')
        sn.distplot(_df2.close.diff(1), ax=ax3)
        sn.distplot(_df2.close.diff(1).iloc[int(_df2.shape[0] * .6):int(_df2.shape[0] * .9)], ax=ax4)
        sn.distplot(_df2.close.diff(1).iloc[int(_df2.shape[0] * .9):], ax=ax5)

        fig.savefig('D:/code/python/left5/fin/option/pic/%s %s+%s.png' % (c, df1_name, df2_name))

        fig.clear()
        plt.close()
        plt.cla()
        plt.clf()


def do():
    i = 0
    future_options = filter_options()
    for future, [option_calls, option_puts] in future_options.items():
        print('============== %s' % future)
        # print(option_calls)
        # print(option_puts)

        if len(option_calls) > 0 and len(option_puts) > 0:
            print('start option %s' % future)
            # print(option_calls, option_puts)
            di = Diff(future, option_calls, option_puts, start_days=30)

            gc.collect()
        else:
            print('not option %s' % future)


# mc = mpf.make_marketcolors(
#     up='tab:red',down='tab:green',
#     edge='inherit',
#     wick={'up':'red','down':'green'},
#     volume={'up':'red','down':'green'},
# )

# style = mpf.make_mpf_style(base_mpl_style="seaborn", marketcolors=mc)

mc = mpf.make_marketcolors(
    up='tab:red',down='tab:green',
    edge='inherit',
    wick={'up':'red','down':'green'},
    volume={'up':'red','down':'green'},#'tab:green',
)

s = mpf.make_mpf_style(base_mpl_style="seaborn", marketcolors=mc, mavcolors=['red', 'green', 'blue'])

class LastOhlc():
    def __init__(self):

        self.ohlc = [0, 0, 0, 0, 0]
        self.inc = True

    def merge_ohlc(self, row): # [open, high, low, close, count]
        
        if row.open >= row.close:
            if self.inc:
                self.inc = False
                self.ohlc = [row.open, row.high, row.low, row.close, 1]
            else:
                if self.ohlc[1] < row.high:
                    self.ohlc[1] < row.high
                if self.ohlc[2] > row.low:
                    self.ohlc[2] = row.low
                self.ohlc[4] += 1
        else:
            if not self.inc:
                self.inc = True
                self.ohlc = [row.open, row.high, row.low, row.close, 1]
            else:
                if self.ohlc[1] < row.high:
                    self.ohlc[1] < row.high
                if self.ohlc[2] > row.low:
                    self.ohlc[2] = row.low
                self.ohlc[4] += 1

        return self.ohlc






def trade1(df, step=5, inc=0.0001, dec=-0.0001): # '2023-07-20'

    between_times = [['09:00', '10:15'], ['10:30', '11:30'], ['13:30', '15:00'], ['21:00', '23:00']]
    
    datas = []

    for day in np.unique(df.index.date):
        df_day = df[df.index.date == day]
        for (start, end) in between_times:
            df_hour = df_day.between_time(start, end)

            # df_hour['close_open'] = df_hour.close - df_hour.open
            # df_hour['x1'] = df_hour.close - df_hour['close_open'] / 2
            # df_hour = df_hour.fillna(0)
            # df_hour['range'] = df_hour['x1'].diff(1) / df_hour['x1'].shift(1)

            df_hour.insert(0, column='close_open', value=(df_hour.close - df_hour.open))
            df_hour.insert(0, column='x1', value=(df_hour.close - df_hour['close_open'] / 2))
            df_hour = df_hour.fillna(0)
            df_hour.insert(0, column='range', value=(df_hour['x1'].diff(1) / df_hour['x1'].shift(1)))

            is_start = False
            _step = 0
            inc_step = 0
            inc_last = None
            inc_last_index = None

            combine_ohlc = []
            last_ohlc = LastOhlc()

            for index, row in df_hour.iterrows():
                ohlc = last_ohlc.merge_ohlc(row)

                if inc_step > 0:
                    inc_step -= 1
                    if False and not last_ohlc.inc and ohlc[4] > 2:
                        inc_step = 0
                        inc_last = None
                        inc_last_index = None
                    elif row.close > inc_last.high and row.close > row.open and row.close > df_hour.loc[:index].iloc[-30:-10].close.max(): #  and row.open < inc_last.close
                            datas.append(index)
                            inc_step = 0
                            inc_last = None
                            inc_last_index = None

                    if inc_step <= 0:
                        inc_step = 0
                        inc_last = None
                        inc_last_index = None


                if row.range > inc: # open close 是否相等
                    if is_start:
                        _step += 1
                    else:
                        is_start = True
                        _step = 1
                else:
                    if _step > step and row.range < dec and row.open > row.close:
                        # for j, rn in df_hour.loc[index:].iloc[1:5].iterrows():
                        # df_hour.loc[index:].iloc[0]
                        # datas.append(index)
                        inc_step = 3
                        inc_last = row
                        inc_last_index = index

                    is_start = False
                    _step = 0

                
    return datas



def trade_do(exchange, symbol, start_day):
    df = load_ohlc(exchange, symbol, start_day)

    datas = trade1(df, step=4)

    for index in datas:
        print(index)
        start = index - datetime.timedelta(minutes=60)
        end = index + datetime.timedelta(minutes=60)

        dd = df.loc[start:end]
        ddd = df.loc[:index][-30:]
        std = ddd.close.std()
        mean = ddd.close.mean()

        d_str = datetime.datetime.strftime(index, '%Y-%m-%d %H-%M')

        mpf.plot(dd, title='std: %.02f, mean: %.02f' % (std, mean), type='candle', style=style, volume=True, scale_width_adjustment=dict(volume=0.4, candle=1), savefig=os.path.join('D:/option/xxxxxxx', '%s.png' % (d_str)))
        plt.close()

if __name__ == '__main__':
    # do()
    trade_do('SHFE', 'rb2310', '2023-06-01')


