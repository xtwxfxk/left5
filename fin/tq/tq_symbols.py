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

symbol_file = 'symbols.txt'

all_symbols = []
# if os.path.exists(symbol_file):
#     all_symbols = [line.strip() for line in open(symbol_file, encoding='utf-8').readlines()]
# else:
exchanges = ["SHFE", "CFFEX", "DCE", "CZCE", "INE"]

for exchange in exchanges:
    # symbol = api.query_quotes(ins_class='FUTURE', exchange_id=exchange, expired=True)
    # all_symbols.extend(symbol)

    # symbol = api.query_quotes(ins_class='FUTURE', exchange_id=exchange, expired=False)
    # all_symbols.extend(symbol)

    # symbol = api.query_quotes(ins_class='OPTION', exchange_id=exchange, expired=True)
    # all_symbols.extend(symbol)

    symbol = api.query_quotes(ins_class='OPTION', exchange_id=exchange, expired=False)
    all_symbols.extend(symbol)

open(symbol_file, 'w', encoding='utf-8').write('\n'.join(all_symbols))