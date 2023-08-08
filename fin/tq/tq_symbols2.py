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
PASSWORD = 'xxxx'

api = TqApi(auth=TqAuth('ahaha', 'xxxx'))

# executor = ThreadPoolExecutor(max_workers=4)

symbol_file = 'symbols2.txt'

all_symbols = []
# exchanges = ["SHFE", "DCE", "CZCE"] # , "CFFEX", "INE"
exchanges = {'SHFE': ['rb', 'al'], 'DCE': ['v', 'pp', 'm', 'c', 'b', 'a'], 'CZCE': ['ma']}


for exchange, syms in exchanges.items():
    symbols = []
    _symbols = []
    _symbols.extend(api.query_quotes(ins_class='FUTURE', exchange_id=exchange, expired=True))

    _symbols.extend(api.query_quotes(ins_class='FUTURE', exchange_id=exchange, expired=False))

    for _symbol in _symbols:
        _symbol_lower = _symbol.lower()
        # print(_symbol_lower)
        for _sym in syms:
            _s = '%s.%s' % (exchange.lower(), _sym.lower())
            if _s in _symbol_lower:
                symbols.append(_symbol)

    all_symbols.extend(symbols)


for exchange, syms in exchanges.items():
    symbols = []
    _symbols = []

    _symbols.extend(api.query_quotes(ins_class='OPTION', exchange_id=exchange, expired=True))

    _symbols.extend(api.query_quotes(ins_class='OPTION', exchange_id=exchange, expired=False))

    for _symbol in _symbols:
        _symbol_lower = _symbol.lower()
        # print(_symbol_lower)
        for _sym in syms:
            _s = '%s.%s' % (exchange.lower(), _sym.lower())
            if _s in _symbol_lower:
                symbols.append(_symbol)

    all_symbols.extend(symbols)

open(symbol_file, 'w', encoding='utf-8').write('\n'.join(all_symbols))