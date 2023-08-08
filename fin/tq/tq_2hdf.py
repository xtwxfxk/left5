
import os, traceback
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

CSV_ROOT = 'Y:/tq_data/ticks'
HDF_ROOT = 'Z:/tq_data/ticks'

symbols_keep = ['SHFE.rb', 'SHFE.al', 'DCE.v', 'DCE.pp', 'DCE.m', 'DCE.c', 'DCE.b', 'DCE.a', 'CZCE.ma']
symbols_keep = [s.lower() for s in symbols_keep]

# executor = ThreadPoolExecutor(max_workers=4)

# def do_convert(file_path, save_path, symbol):
#     try:
#         df = pd.read_csv(file_path)
#         df.to_hdf(save_path, symbol, mode='w', format='table', complevel=7, data_columns=True)
#     except Exception as ex:
#         print(file_path)
#         traceback.print_exc()

futures = []
for file_name in tqdm(os.listdir(CSV_ROOT)):
    symbol = file_name[:-4]
    hdf_file_name = '%s.h5' % symbol
    save_path = os.path.join(HDF_ROOT, hdf_file_name)

    is_save = False
    for symbol_pre in symbols_keep:
        if symbol_pre in file_name.lower():
            if not os.path.exists(save_path):
                print(file_name)

                # futures.append(executor.submit(do_convert, os.path.join(CSV_ROOT, file_name), save_path, symbol))
                df = pd.read_csv(os.path.join(CSV_ROOT, file_name))
                df.to_hdf(save_path, symbol, mode='w', format='table', complevel=7, data_columns=True)
            else:
                print('pass %s' % file_name)
            is_save = True
            break
    if not is_save:
        print('pass symbol %s' % file_name)

# as_completed(futures)

# nohup /path/to/tq_2hdf.py > output.log &




# fig, ax = plt.subplots()

# candlestick_ohlc(ax, df.iloc[2000].values, width=0.6, colorup='green', colordown='red', alpha=0.8)

# # Setting labels & titles
# ax.set_xlabel('Date')
# ax.set_ylabel('Price')
# fig.suptitle('al2111C21400')

# # Formatting Date
# date_format = mpl_dates.DateFormatter('%d-%m-%Y')
# ax.xaxis.set_major_formatter(date_format)
# fig.autofmt_xdate()

# fig.tight_layout()

# plt.show()


# fig, ax = plt.subplots()

# candlestick_ohlc(ax, df.iloc[-2000:].values, width=0.6, colorup='green', colordown='red', alpha=0.8)

# # Setting labels & titles
# ax.set_xlabel('Date')
# ax.set_ylabel('Price')
# fig.suptitle('al2111C21400')

# # Formatting Date
# date_format = mpl_dates.DateFormatter('%d-%m-%Y')
# ax.xaxis.set_major_formatter(date_format)
# fig.autofmt_xdate()

# fig.tight_layout()

# plt.show()

# ddd.to_hdf('Z:/tq_data/ticks/SHFE.al2206.h5', 'SHFE.al2206', mode='w', format='table', complevel=7, data_columns=True)

