import logging, time
import os
from datetime import datetime, timedelta
from typing import Union
# from concurrent.futures import ThreadPoolExecutor
# import concurrent.futures

import ray
import pandas as pd
from contextlib import closing
from pandas import Series, Timestamp, DataFrame

from tqsdk import TqApi, TqAuth
from tqsdk.tools import DataDownloader

USERNAME = 'ahaha'
PASSWORD = 'xxx'

api = TqApi(auth=TqAuth('ahaha', 'xxx'))


# executor = ThreadPoolExecutor(max_workers=4)


# all_symbols = []
# if os.path.exists('future_symbols.txt'):
#     all_symbols = [line.strip() for line in open('future_symbols.txt', encoding='utf-8').readlines()]
# else:
#     exchanges = ["SHFE", "CFFEX", "DCE", "CZCE", "INE"]

#     for exchange in exchanges:
#         symbol = api.query_quotes(ins_class='FUTURE', exchange_id=exchange, expired=True)
#         all_symbols.extend(symbol)

#         symbol = api.query_quotes(ins_class='FUTURE', exchange_id=exchange, expired=False)
#         all_symbols.extend(symbol)
#     open('future_symbols.txt', 'w', encoding='utf-8').write('\n'.join(all_symbols))

all_symbols = [line.strip() for line in open('future_symbols.txt', encoding='utf-8').readlines()]

# class Download():

#     def __init__(self):
#         self.api = TqApi(auth=TqAuth(USERNAME, PASSWORD))

# def do(symbol, save_path):
#     api = TqApi(auth=TqAuth(USERNAME, PASSWORD))

#     dataDownloader = DataDownloader(api, symbol_list = [symbol], dur_sec = 0, start_dt = datetime(2021, 1, 1), end_dt = datetime(2023, 5, 1), csv_file_name=save_path)

#     while not dataDownloader.is_finished():
#         print('progress: %s %.2f%%' % (symbol, dataDownloader.get_progress()))
#         api.wait_update()

#     return symbol


# it = iter(all_symbols)
# for symbols in zip(it, it, it, it):

# tasks = []
# for symbol in all_symbols:
#     save_path = os.path.join('Y:/tq_data/ticks/', '%s.csv' % symbol)
#     if not os.path.exists(save_path):
#         tasks.append(executor.submit(do, symbol, save_path))

#     # Wait for all tasks to complete
#     for task in concurrent.futures.as_completed(tasks):
#         print(task.result())

#     else:
#         print('pass %s' % symbol)

# for task in concurrent.futures.as_completed(tasks):
#     print('over: %s' % tasks.result())
#     open('over_symbol.txt', 'a').write('%s\n' % tasks.result())
    


download_tasks = {}
for symbol in all_symbols:
    # for symbol in symbols:
    # print(symbol)
    save_path = os.path.join('Y:/tq_data/ticks/', '%s.csv' % symbol)
    if not os.path.exists(save_path):
        download_tasks[symbol] = DataDownloader(api, symbol_list = [symbol], dur_sec = 0, start_dt = datetime(2021, 1, 1), end_dt = datetime(2023, 5, 1), csv_file_name=save_path)

        while len(download_tasks.keys()) >= 4:
            print('progress: ', {k: ('%.2f%%' % v.get_progress()) for k, v in download_tasks.items() })
            for k, v in list(download_tasks.items()):
                # print('progress: %s %.2f%%' % (k, v.get_progress()))
                if v.is_finished():
                    open('over_symbol.txt', 'a').write('%s\n' % k)
                    del download_tasks[k]

            api.wait_update()
    else:
        print('pass %s' % symbol)
        # time.sleep(1)

while len(download_tasks.keys()) > 0:
    print('progress last: ', {k: ('%.2f%%' % v.get_progress()) for k, v in download_tasks.items() })
    for k, v in list(download_tasks.items()):
        # print('progress: %s %.2f%%' % (k, v.get_progress()))
        if v.is_finished():
            open('over_symbol.txt', 'a').write('%s\n' % k)
            del download_tasks[k]

    api.wait_update()
    # time.sleep(1)
    
    # while not all([v.is_finished() for v in download_tasks.values()]):
    #     api.wait_update()
    #     print('progress: ', {k: ('%.2f%%' % v.get_progress()) for k, v in download_tasks.items() })



# ticks = api.get_tick_serial("SHFE.cu2306")
# klines = api.get_kline_serial("SHFE.cu2306", 10)
# klines = api.get_kline_data_series("SHFE.cu2206", 10)
