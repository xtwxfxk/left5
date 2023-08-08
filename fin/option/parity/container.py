# -*- coding: utf-8 -*-

import pandas as pd

from utils import target_call_put, split_future_symbol

class FutureOptionContaner():

    def __init__(self, target_name, calls, puts):

        self.target_name = target_name
        self.calls = calls
        self.puts = puts

        if calls[0].lower().find('-c-') > -1:
            self.call_sep = '-C-'
            self.put_sep = '-P-'
        else:
            self.call_sep = 'C'
            self.put_sep = 'P'

        self.columns = [target_name]
        self.columns.extend(calls)
        self.columns.extend(puts)

        call_prices = []
        for call_symbol in calls:
            self.columns.append('%s_bid_price1' % call_symbol)
            self.columns.append('%s_ask_price1' % call_symbol)

            t, price = split_future_symbol(call_symbol)
            call_prices.append(price)

        prices = []
        for put_symbol in puts:
            self.columns.append('%s_bid_price1' % put_symbol)
            self.columns.append('%s_ask_price1' % put_symbol)

            t, price = split_future_symbol(put_symbol)

            if price in call_prices:
                prices.append(price)

                self.columns.append('%s_%s' % (target_name, price))
                self.columns.append('%s_%s_positive' % (target_name, price))
                self.columns.append('%s_%s_negative' % (target_name, price))

        self.prices = prices


        self.df = pd.DataFrame(columns=self.columns)


class FutureOptionContainerManager():

    def __init__(self):
        self.containers = {}

    def get(self, target_name):
        return self.containers.get(target_name, None)

    def append(self, target_name, container):
        self.containers[target_name] = container

    def get_df(self, target_name):
        return self.containers.get(target_name, None).df

    def set_df(self, target_name, df):
        self.containers.get(target_name).df = df


tcp = target_call_put()
manager = FutureOptionContainerManager()

# for columns in symbol_columns:
#     target_name = columns[0]
#     container = FutureOptionContaner(target_name, columns)
#     manager.append(target_name, container)

for target_name, v in tcp.items():
    container = FutureOptionContaner(target_name, v['call'], v['put'])
    manager.append(target_name, container)
