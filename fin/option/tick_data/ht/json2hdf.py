# -*- coding: utf-8 -*-
import os, datetime, json, traceback
import pandas as pd
import numpy as np
import h5py

import warnings
from tables import NaturalNameWarning
warnings.filterwarnings('ignore', category=NaturalNameWarning)

OLD_PATH = 'D:/option_data/ht/2023-06-17'
NEW_PATH = 'D:/option_data/ht/h5'


for file_name in os.listdir(OLD_PATH):
    new_file = os.path.join(NEW_PATH, '%s.h5' % file_name)
    # new_file = os.path.join(NEW_PATH, '2023-04-24.h5')
    file_path = os.path.join(OLD_PATH, file_name)

    print(file_name)
    # with h5py.File(new_file, 'a') as f:
    #     f.create_dataset(file_name, (46,))

    # store = pd.HDFStore(new_file)
    datas = []
    for line in open(file_path):
        if line.strip():
    #         # datas.append(json.loads(line.strip()))
    #         # d = pd.read_json(json.loads(line.strip()))
    #         d = pd.DataFrame(json.loads(line.strip()), index=[0])
    #         # d = pd.DataFrame.from_dict(json.loads(line.strip()), orient='index')
    #         # d = pd.Series(json.loads(line.strip()))
    #         print(d)
    #         # store.append(file_name, d, format='table', data_columns=True)
            datas.append(json.loads(line.strip()))
    # break
    # print(datas)
    df = pd.DataFrame.from_dict(datas)
    # print(df)
    df.to_hdf(new_file, file_name, mode='w', format='table', complevel=7, data_columns=True)
    # print(array)
    # break
