# -*- coding: utf-8 -*-
import os, datetime, json, traceback, re, time

import numpy as np
import pandas as pd

import logging
import logging.config

from queues import data_queue
from utils import split_future_symbol
from container import manager, FutureOptionContaner

logger = logging.getLogger('verbose')


# {"TradingDay": "20230712", "InstrumentID": "rb2402", "ExchangeID": "", "ExchangeInstID": "", "LastPrice": 3594.0000000000005, "PreSettlementPrice": 3589.0, "PreClosePrice": 3591.0, "PreOpenInterest": 31396.0, "OpenPrice": 3591.0, "HighestPrice": 3611.0000000000005, "LowestPrice": 3591.0, "Volume": 493, "Turnover": 17705930.0, "OpenInterest": 30919.0, "ClosePrice": 1.7976931348623157e+308, "SettlementPrice": 1.7976931348623157e+308, "UpperLimitPrice": 3983.0, "LowerLimitPrice": 3194.0, "PreDelta": 1.7976931348623157e+308, "CurrDelta": 1.7976931348623157e+308, "UpdateTime": "23:00:00", "UpdateMillisec": 500, "BidPrice1": 3597.0000000000005, "BidVolume1": 1, "AskPrice1": 3654.0000000000005, "AskVolume1": 1, "BidPrice2": 1.7976931348623157e+308, "BidVolume2": 0, "AskPrice2": 1.7976931348623157e+308, "AskVolume2": 0, "BidPrice3": 1.7976931348623157e+308, "BidVolume3": 0, "AskPrice3": 1.7976931348623157e+308, "AskVolume3": 0, "BidPrice4": 1.7976931348623157e+308, "BidVolume4": 0, "AskPrice4": 1.7976931348623157e+308, "AskVolume4": 0, "BidPrice5": 1.7976931348623157e+308, "BidVolume5": 0, "AskPrice5": 1.7976931348623157e+308, "AskVolume5": 0, "AveragePrice": 35914.66531440162, "ActionDay": "20230711", "BandingUpperPrice": 0.0, "BandingLowerPrice": 0.0}

dfs = {}


def tick(tick_data):
    df = pd.DataFrame.from_dict([tick_data])
    df['datetime'] = df['ActionDay'] + ' ' + df['UpdateTime'] #  + '.' + df['UpdateMillisec'].astype(str)
    df = df[['datetime', 'LastPrice', 'BidPrice1', 'AskPrice1']].rename(columns={'datetime': 'datetime', 
        'LastPrice': tick_data['InstrumentID'],
        'BidPrice1': '%s_bid_price1' % tick_data['InstrumentID'],
        # 'BidVolume1': '%s_bid_volume1' % tick_data['InstrumentID'],
        'AskPrice1': '%s_ask_price1' % tick_data['InstrumentID'],
        # 'AskVolume1': '%s_ask_volume1' % tick_data['InstrumentID'],
        })

    # df['datetime'] = pd.to_datetime(df.datetime, format='%Y%m%d %H:%M:%S.%f')
    df['datetime'] = pd.to_datetime(df.datetime, format='%Y%m%d %H:%M:%S')
    df.index = df.datetime

    return df

# def data_process():

#     while True:
#         try:
#             tick_data = data_queue.get()

#             df = dfs.get(tick_data['InstrumentID'])
#             if df is None:
#                 df = pd.DataFrame()

#             df = pd.concat([df, tick(tick_data)])
#             df = pd.concat([df.iloc[:-2], df.iloc[-2:].resample('1S').last().fillna(method="ffill")])

#             dfs[tick_data['InstrumentID']] = df

#         except KeyboardInterrupt:
#             logger.info('Exit KeyboardInterrupt save')
#             return
#         except Exception as ex:
#             logger.error(ex, exc_info=True)


def data_process():

    while True:
        try:
            tick_data = data_queue.get()

            symbol_name = tick_data['InstrumentID']
            target_name, price = split_future_symbol(symbol_name)

            container = manager.get(target_name)
            df = container.df
            if df is not None:
                iter_item = tick(tick_data)
                # logger.info(iter_item)
                _columns = [symbol_name,'%s_bid_price1' % symbol_name, '%s_ask_price1' % symbol_name]

                if iter_item.index[0] in df.index:
                    df.loc[iter_item.index[0],_columns] = iter_item.loc[iter_item.index[0],_columns] # [symbol_name][0]
                else:
                    df = df.append(pd.DataFrame(index=iter_item.index), ignore_index=False)
                    df.loc[iter_item.index[0],_columns] = iter_item.loc[iter_item.index[0],_columns] # iter_item[symbol_name][0]

                df = df.fillna(method="ffill")

                if price is not None and price in container.prices:
                    column_name = '%s_%s' % (target_name, price)
                    # todo
                    call_symbol = '%s%s%s' % (target_name, container.call_sep, price)
                    put_symbol = '%s%s%s' % (target_name, container.put_sep, price)

                    positive_symbol = '%s_%s_positive' % (target_name, price)
                    negative_symbol = '%s_%s_negative' % (target_name, price)

                    call_symbol_bid_price = '%s_bid_price1' % call_symbol
                    call_symbol_ask_price = '%s_ask_price1' % call_symbol
                    put_symbol_bid_price = '%s_bid_price1' % put_symbol
                    put_symbol_ask_price = '%s_ask_price1' % put_symbol

                    # logger.info(df.loc[iter_item.index[0],call_symbol])
                    # logger.info(df.loc[iter_item.index[0],put_symbol])

                    # 最后报价
                    if not np.isnan(df.loc[iter_item.index[0],call_symbol]) and not np.isnan(df.loc[iter_item.index[0],put_symbol]):
                        df.loc[iter_item.index[0],column_name] = price + df.loc[iter_item.index[0],call_symbol] - df.loc[iter_item.index[0],put_symbol]

                    # 正向套利价格
                    if not np.isnan(df.loc[iter_item.index[0],call_symbol_bid_price]) and not np.isnan(df.loc[iter_item.index[0],put_symbol_ask_price]):
                        df.loc[iter_item.index[0],positive_symbol] = price + df.loc[iter_item.index[0],call_symbol_bid_price] - df.loc[iter_item.index[0],put_symbol_ask_price]

                    # 反向套利价格
                    if not np.isnan(df.loc[iter_item.index[0],call_symbol_ask_price]) and not np.isnan(df.loc[iter_item.index[0],put_symbol_bid_price]):
                        df.loc[iter_item.index[0],negative_symbol] = price + df.loc[iter_item.index[0],put_symbol_bid_price] - df.loc[iter_item.index[0],call_symbol_ask_price]


            manager.set_df(target_name, df)


        except KeyboardInterrupt:
            logger.info('Exit KeyboardInterrupt save')
            return
        except Exception as ex:
            logger.error(ex, exc_info=True)



def data_strategy():

    t = time.time()

    while True:
        try:
            time.sleep(1)

            # dfs['rb2309']
            # dfs['rb2309C3800']
            # dfs['rb2309P3800']


            for target_name in manager.containers.keys():
                if target_name == 'rb2308':
                    container = manager.get(target_name)
                    print(container.df[['rb2308', 'rb2308_3700_positive', 'rb2308_3750_positive','rb2308_3800_positive']].tail(20)) # rb2308_3700

                # if target_name == 'al2308':
                #     container = manager.get(target_name)
                #     print(container.df[['al2308', 'al2308_18200_positive', 'al2308_18300_positive','al2308_18400_positive']].tail(20)) # rb2308_3700

                    # container.columns
                # print(manager.get_df(target_name))




            # if time.time() - t > 120:
            now = datetime.datetime.now()
            if now.hour == 23 and now.minute >= 5:
                now_str = datetime.datetime.strftime(now, '%Y-%m-%d %H%M')
                for target_name in manager.containers.keys():
                    manager.get(target_name).df.to_pickle(os.path.join('D:/code/python/left5/fin/option/parity/xx', '%s_%s' % (now_str, target_name)))

                print('over------------------------')
                return
        except KeyboardInterrupt:
            return
        except Exception as ex:
            logger.error(ex, exc_info=True)






