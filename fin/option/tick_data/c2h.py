# -*- coding: utf-8 -*-
import os, datetime, json, traceback
import pandas as pd
import numpy as np
import h5py


OLD_PATH = 'D:/option_data/dz/2023-04-24'
NEW_PATH = 'D:/option_data/dz/h5'


# for file_name in os.listdir(OLD_PATH):
#     new_file = os.path.join(NEW_PATH, '%s.h5' % file_name)
#     # new_file = os.path.join(NEW_PATH, '2023-04-24.h5')
#     file_path = os.path.join(OLD_PATH, file_name)

#     print(file_name)
#     # with h5py.File(new_file, 'a') as f:
#     #     f.create_dataset(file_name, (46,))

#     store = pd.HDFStore(new_file)
#     # datas = []
#     for line in open(file_path):
#         if line.strip():
#             # datas.append(json.loads(line.strip()))
#             # d = pd.read_json(json.loads(line.strip()))
#             d = pd.DataFrame(json.loads(line.strip()), index=[0])
#             # d = pd.DataFrame.from_dict(json.loads(line.strip()), orient='index')
#             # d = pd.Series(json.loads(line.strip()))
#             print(d)
#             # store.append(file_name, d, format='table', data_columns=True)

#     break

        # df = pd.json_normalize(datas)
    # array = df.to_numpy()
    # df.to_hdf(new_file, file_name, mode='a', format='table', data_columns=True)
    # print(array)
    # break

aaa = [
    ('TradingDay', 'a8'), 
    ('InstrumentID', 'a20'), 
    ('ExchangeID', 'a'), 
    ('ExchangeInstID', 'a'), 
    ('LastPrice', 'f8'), 
    ('PreSettlementPrice', 'f8'), 
    ('PreClosePrice', 'f8'), 
    ('PreOpenInterest', 'f8'), 
    ('OpenPrice', 'f8'), 
    ('HighestPrice', 'f8'), 
    ('LowestPrice', 'f8'), 
    ('Volume', 'f'), 
    ('Turnover', 'f'), 
    ('OpenInterest', 'f8'), 
    ('ClosePrice', 'f8'), 
    ('SettlementPrice', 'f8'), 
    ('UpperLimitPrice', 'f8'), 
    ('LowerLimitPrice', 'f8'), 
    ('PreDelta', 'f'), 
    ('CurrDelta', 'f'), 
    ('UpdateTime', 'a8'), 
    ('UpdateMillisec', 'i'), 
    ('BidPrice1', 'f8'), 
    ('BidVolume1', 'i'), 
    ('AskPrice1', 'f8'), 
    ('AskVolume1', 'i'), 
    ('BidPrice2', 'f8'), 
    ('BidVolume2', 'i'), 
    ('AskPrice2', 'f8'), 
    ('AskVolume2', 'i'), 
    ('BidPrice3', 'f8'), 
    ('BidVolume3', 'i'), 
    ('AskPrice3', 'f8'), 
    ('AskVolume3', 'i'), 
    ('BidPrice4', 'f8'), 
    ('BidVolume4', 'i'), 
    ('AskPrice4', 'f8'), 
    ('AskVolume4', 'i'), 
    ('BidPrice5', 'f8'), 
    ('BidVolume5', 'i'), 
    ('AskPrice5', 'f8'), 
    ('AskVolume5', 'i'), 
    ('AveragePrice', 'f8'), 
    ('ActionDay', 'a8'), 
    ('BandingUpperPrice', 'f'), 
    ('BandingLowerPrice', 'f')]

# for i in aaa:
#     print("'%s, '" % i[0])
# for i in aaa:
#     print("'%s, '" % i[1])

dtype = np.dtype([
    ('TradingDay', 'a8'), 
    ('InstrumentID', 'a20'), 
    ('ExchangeID', 'a'), 
    ('ExchangeInstID', 'a'), 
    ('LastPrice', 'f8'), 
    ('PreSettlementPrice', 'f8'), 
    ('PreClosePrice', 'f8'), 
    ('PreOpenInterest', 'f8'), 
    ('OpenPrice', 'f8'), 
    ('HighestPrice', 'f8'), 
    ('LowestPrice', 'f8'), 
    ('Volume', 'f'), 
    ('Turnover', 'f'), 
    ('OpenInterest', 'f8'), 
    ('ClosePrice', 'f8'), 
    ('SettlementPrice', 'f8'), 
    ('UpperLimitPrice', 'f8'), 
    ('LowerLimitPrice', 'f8'), 
    ('PreDelta', 'f'), 
    ('CurrDelta', 'f'), 
    ('UpdateTime', 'a8'), 
    ('UpdateMillisec', 'i'), 
    ('BidPrice1', 'f8'), 
    ('BidVolume1', 'i'), 
    ('AskPrice1', 'f8'), 
    ('AskVolume1', 'i'), 
    ('BidPrice2', 'f8'), 
    ('BidVolume2', 'i'), 
    ('AskPrice2', 'f8'), 
    ('AskVolume2', 'i'), 
    ('BidPrice3', 'f8'), 
    ('BidVolume3', 'i'), 
    ('AskPrice3', 'f8'), 
    ('AskVolume3', 'i'), 
    ('BidPrice4', 'f8'), 
    ('BidVolume4', 'i'), 
    ('AskPrice4', 'f8'), 
    ('AskVolume4', 'i'), 
    ('BidPrice5', 'f8'), 
    ('BidVolume5', 'i'), 
    ('AskPrice5', 'f8'), 
    ('AskVolume5', 'i'), 
    ('AveragePrice', 'f8'), 
    ('ActionDay', 'a8'), 
    ('BandingUpperPrice', 'f'), 
    ('BandingLowerPrice', 'f')])

dt = {'names':['TradingDay', 
'InstrumentID', 
'ExchangeID', 
'ExchangeInstID', 
'LastPrice', 
'PreSettlementPrice', 
'PreClosePrice', 
'PreOpenInterest', 
'OpenPrice', 
'HighestPrice', 
'LowestPrice', 
'Volume', 
'Turnover', 
'OpenInterest', 
'ClosePrice', 
'SettlementPrice', 
'UpperLimitPrice', 
'LowerLimitPrice', 
'PreDelta', 
'CurrDelta', 
'UpdateTime', 
'UpdateMillisec', 
'BidPrice1', 
'BidVolume1', 
'AskPrice1', 
'AskVolume1', 
'BidPrice2', 
'BidVolume2', 
'AskPrice2', 
'AskVolume2', 
'BidPrice3', 
'BidVolume3', 
'AskPrice3', 
'AskVolume3', 
'BidPrice4', 
'BidVolume4', 
'AskPrice4', 
'AskVolume4', 
'BidPrice5', 
'BidVolume5', 
'AskPrice5', 
'AskVolume5', 
'AveragePrice', 
'ActionDay', 
'BandingUpperPrice', 
'BandingLowerPrice,'], 'formats':['a8', 
'a20', 
'a', 
'a', 
'f8', 
'f8', 
'f8', 
'f8', 
'f8', 
'f8', 
'f8', 
'f', 
'f', 
'f8', 
'f8', 
'f8', 
'f8', 
'f8', 
'f', 
'f', 
'a8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'i', 
'f8', 
'a8', 
'f', 
'f', ]}

l = ['20230424', 'a2305', '', '', 5010.0, 5001.0, 4968.0, 13090.0, 4968.0, 5030.0, 4968.0, 3880, 194148210.0, 10963.0, 5010.0, 5003.0, 5401.0, 4601.0, 0.0, 0.0, '15:01:21', 152, 5003.0, 1, 5015.0, 19, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 50038.198453608245, '20230424', 0.0, 0.0]
ds = np.array(l)
ds.dtype = dt
print(ds.dtype)
# print(len(dtype))
# print(len(l))

# ds = np.array([tuple(l)], dtype=dtype)
print(ds)


print('############################')


for file_name in os.listdir(OLD_PATH):
    new_file = os.path.join(NEW_PATH, '%s.h5' % file_name)
    # new_file = os.path.join(NEW_PATH, '2023-04-24.h5')
    file_path = os.path.join(OLD_PATH, file_name)

    print(file_name)
    with h5py.File(new_file, 'a') as f:
        ds = f.get(file_name) or f.create_dataset(file_name, shape=(0, 46), maxshape = (None, 46))

        for line in open(file_path):
            if line.strip():
                # s = json.loads(line.strip())
                # print(json.loads(line.strip()).values())
                # print('sssssssssssss')
                # print(dtype)
                # print(list(json.loads(line.strip()).values()))
                d = np.array([tuple((json.loads(line.strip()).values()))], dtype=dtype)
                print(d[0])
                print(d[0].shape)
                ds.resize(ds.shape[0] + 1, axis = 0)
                ds[-1:] = d
                # ds[-1] =  np.asarray(json.loads(line.strip()).values())


                # datas.append(json.loads(line.strip()))
                # d = pd.read_json(json.loads(line.strip()))
                # d = pd.DataFrame.from_dict(json.loads(line.strip()), orient='index')
                # d = pd.Series(json.loads(line.strip()))
                print(d)

    break