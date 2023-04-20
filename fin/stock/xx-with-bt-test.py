import datetime, time
import scipy.stats as stats
import pandas as pd
import numpy as np
import seaborn as sns
########


from lutils.stock import LTdxHq


# stock_datas = {}
# def get_stock(code, start):
#     if code not in stock_datas.keys():
#         print('----------- fetch stock data %s' % code)
#         ltdxhq = LTdxHq()
#         df = ltdxhq.get_k_data_daily(code, start=start)
#         stock_datas[code] = df

#     return stock_datas.get(code)



date_first = datetime.datetime.strptime('2019-01-01', '%Y-%m-%d')
date_start = datetime.datetime.strptime('2022-10-25', '%Y-%m-%d')
trade_end = datetime.datetime.strptime('2022-11-25', '%Y-%m-%d')


keep_day = 3
date_span = 90
stock_count = 4

buy_money = 5000 * stock_count


ddf = pd.read_pickle('d:/ddf_1127.pkl').dropna()
ddf = ddf.sort_values(['date','tic'], ignore_index=True)
ddf.index = ddf.date.factorize()[0]
days = ddf.date.unique()


i = 0

ltdxhq = LTdxHq()
while date_start < trade_end:
    date_start_end = np.where(days==np.datetime64(date_start.strftime('%Y-%m-%d')))[0][0]
    date_start_start = date_start_end - date_span

    dl = ddf[(ddf['date'] > days[date_start_start]) & (ddf['date'] < days[date_start_end])]
    dd = dl.pivot_table(index = 'date',columns = 'tic', values = 'close').pct_change().dropna()
    corr = dd.cov().corr()

    _stock_codes = list(corr.unstack().sort_values().index.get_level_values(0)[:stock_count * 2])
    stock_codes = []
    while len(stock_codes) < stock_count:
        sc = _stock_codes.pop(0)
        if sc not in stock_codes:
            stock_codes.append(sc)

    print(stock_codes)

    pers = [1 / len(stock_codes)] * len(stock_codes)
    
    indexs = None
    dfs = []

    left_money = 0
    after_money = 0
    keeps = []
    
    _date_start = date_start
    date_start = date_start + datetime.timedelta(days=keep_day)

    data_span = keep_day + 1
    if date_start.weekday() == 5:
        date_start = date_start + datetime.timedelta(days=2)
        data_span += 2
    elif date_start.weekday() == 6:
        date_start = date_start + datetime.timedelta(days=1)
        data_span += 1

    for code, per in zip(stock_codes, pers):
        df = ltdxhq.get_k_data_daily(code, start=_date_start.strftime('%Y-%m-%d'), end=(_date_start + datetime.timedelta(days=data_span)).strftime('%Y-%m-%d'))
        #, end=trade_end) # 2014-01-01
        keep = (buy_money * per / (df.iloc[0].close * 100))
        keeps.append(keep)
        
        left_money += buy_money * per - keep * df.iloc[0].close * 100
        
        after_money += df.iloc[-1].close * 100 * keep
        
    after_money += left_money
    buy_money = after_money

    
    print('stock list: %s %s' % (date_start.strftime('%Y-%m-%d'), buy_money))


print('last money %s' % buy_money)