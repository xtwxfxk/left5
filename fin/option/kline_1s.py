# -*- coding: utf-8 -*-

import os, re, datetime, gc
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import seaborn as sn

from lutils.fin.data_loader import load, load_ctp

import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

QT_TICK_ROOT = 'Z:/tq_data/ticks'
FIN_TICK_ROOT= 'Y:/fin_data'

KLINES_1S_ROOT = 'Z:/klines/1m'


finish_symbol = []
if os.path.exists('finish_symbol.txt'):
    for i in open('finish_symbol.txt', 'r', encoding='utf-8').readlines():
        if i.strip():
            finish_symbol.append(i.strip())


def make_1m(df, symbol):

    df.index = df.datetime

    resample_ohlc_min = df['last_price'].resample('1Min', closed='left', label='right').ohlc(_method='ohlc')
    _volume = df['volume'].diff(1).fillna(0)
    _volume[_volume < 0] = 0
    resample_volume_min =_volume.resample('1Min', closed='left', label='right').sum()
    _amount = df['amount'].diff(1).fillna(0)
    _amount[_amount < 0] = 0
    resample_amount_min = _amount.resample('1Min', closed='left', label='right').sum()
    df_min = pd.concat([resample_ohlc_min, resample_volume_min, resample_amount_min], axis=1)
    df_min = df_min.dropna()

    if df_min.shape[0] > 0:
        file_path = os.path.join(KLINES_1S_ROOT, '%s.h5' % symbol)
        df_min.to_hdf(file_path, symbol, mode='w', format='table', complevel=8, data_columns=True)
        print('over %s' % symbol)
    else:
        print('empty %s' % symbol)

    finish_symbol.append(symbol)
    with open('finish_symbol.txt', 'a+', encoding='utf-8') as f:
        f.write('%s\n' % symbol)


for file_name in os.listdir(QT_TICK_ROOT):
    exchange, symbol, _ = file_name.split('.')
    if symbol not in finish_symbol:
        print(symbol)
        df = load(exchange, symbol)

        # df.index = df.datetime

        # resample_ohlc_min = df['last_price'].resample('1Min', closed='left', label='right').ohlc(_method='ohlc')
        # _volume = df['volume'].diff(1).fillna(0)
        # _volume[_volume < 0] = 0
        # resample_volume_min =_volume.resample('1Min', closed='left', label='right').sum()
        # _amount = df['amount'].diff(1).fillna(0)
        # _amount[_amount < 0] = 0
        # resample_amount_min = _amount.resample('1Min', closed='left', label='right').sum()
        # df_min = pd.concat([resample_ohlc_min, resample_volume_min, resample_amount_min], axis=1)
        # df_min = df_min.dropna()

        # if df_min.shape[0] > 0:
        #     file_path = os.path.join(KLINES_1S_ROOT, '%s.h5' % symbol)
        #     df_min.to_hdf(file_path, symbol, mode='w', format='table', complevel=8, data_columns=True)
        #     print('over %s' % symbol)
        # else:
        #     print('empty %s' % symbol)
        # with open('finish_symbol.txt', 'a+', encoding='utf-8') as f:
        #     f.write('%s\n' % symbol)

        make_1m(df, symbol)

    else:
        print('pass %s' % symbol)





lists = os.listdir(FIN_TICK_ROOT)
lists.sort()
for p in lists:
    data_path = os.path.join(FIN_TICK_ROOT, p)
    if os.path.isdir(data_path):
        for file_name in os.listdir(data_path):
            symbol, _ = file_name.split('.')
            if symbol not in finish_symbol:
                df = load_ctp(symbol, p)

                make_1m(df, symbol)
    else:
        print('pass %s' % symbol)
