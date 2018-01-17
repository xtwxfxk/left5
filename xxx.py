# -*- coding: utf-8 -*-
__author__ = 'xtwxfxk'

import os
import datetime

import numpy as np
import pandas as pd

file_root = '/mnt/disk/weather_train/month_data_2017/01'

BOUND_12 = np.asarray([0.1, 5.0, 15.0, 30.0, 70.0, 140.0, ])
BOUND_24 = np.asarray([0.1, 10.0, 25.0, 50.0, 100.0, 250.0, ])

class Detection(object):
    def __init__(self, file_path):

        self.file_path = file_path

        self.ns = []

    def calc_ts(self, na, nc, nb):

        return np.column_stack([self.ns['na'] / np.sum(self.ns.iloc[:, :3], axis=1) * 100, self.ns['datetime']])

    def calc_po(self):

        return np.column_stack([self.ns['nc'] / np.sum(self.ns[['na', 'nc']], axis=1) * 100, self.ns['datetime']])

    def calc_far(self):

        return np.column_stack([self.ns['nb'] / np.sum(self.ns[['na', 'nb']], axis=1) * 100, self.ns['datetime']])

    def filter_data(self, files):
        for i, f in enumerate(files):
            files[i] = os.path.join(self.file_path, f)

        dfs = []
        for _file in files:
            dfs.append(pd.read_csv(_file))

        data = pd.concat(dfs)

        grouped = data.groupby('id')
        d = grouped['id'].count()
        ids = d[d == len(files)].index

        check_data = data[data['id'].isin(ids)]
        grouped = check_data.groupby('id')

        actual_data_sum = grouped['actual_data'].sum()
        forecast_sum = grouped['forecast'].sum()
        latitude = grouped['latitude'].first()
        longitude = grouped['longitude'].first()

        df = pd.concat([actual_data_sum, forecast_sum, latitude, longitude], axis=1)
        data_sum = df.values
        data_sum_level = np.zeros([data_sum.shape[0], 3])

        bound = BOUND_12 if len(files) == 4 else BOUND_24
        for i, level in enumerate(bound):
            data_sum_level[:, 0][np.all([data_sum[:, 0] < level, data_sum_level[:, 0] == 0], axis=0)] = i + 1
            data_sum_level[:, 1][np.all([data_sum[:, 1] < level, data_sum_level[:, 1] == 0], axis=0)] = i + 1
        data_sum_level[data_sum_level == 0] = len(bound) + 1

        data_sum_level[:, 2] = np.max(data_sum_level[:, :2], axis=1)

        df['weather_level'] = np.max(data_sum_level[:, :2], axis=1)
        df['type'] = 0

        df['type'][data_sum_level[:, 0] == data_sum_level[:, 1]] = 1
        df['type'][data_sum_level[:, 0] > data_sum_level[:, 1]] = 2
        df['type'][data_sum_level[:, 0] < data_sum_level[:, 1]] = 3

        return df

    def filter_file_by_time(self, calc_date, start_hour=0, end_hour=12, interval=3):
        self.ns = []

        files = []
        start_time = calc_date + datetime.timedelta(hours=start_hour)
        for i in range(int((end_hour - start_hour) / interval)):
            start_time = start_time + datetime.timedelta(hours=i * interval)
            file_name = '%s.000.csv' % start_time.strftime('%y%m%d%H')
            file_path = os.path.join(self.file_path, file_name)
            if os.path.exists(file_path):
                files.append(file_name)
            else:
                break

        if len(files) == (end_hour - start_hour) / interval:
            return self.filter_data(files)

        return None

    def calc_point(self, save_path, start_time, end_time=None):  # 17010108

        start_date = datetime.datetime.strptime(str(start_time), '%y%m%d%H')
        calc_date = start_date

        result = []
        count = 1
        while (count > 0 or (end_time is not None and calc_date.strftime('%y%m%d%H') <= end_time)):
            count -= 1
            calc_date = calc_date + datetime.timedelta(hours=12)

            dfs = []
            for i, [start_hour, end_hour] in enumerate([[0, 12], [12, 24], [0, 24], [24, 48], [48, 72]]):
                df = self.filter_file_by_time(calc_date, start_hour=start_hour, end_hour=end_hour)
                if df is None:
                    continue
                df['time_level'] = i + 1
                dfs.append(df)

            if len(dfs) < 1:
                continue
            data = pd.concat(dfs)
            print("Save Data: %s" % calc_date.strftime('%y%m%d%H'))
            data.to_csv(os.path.join(save_path, '%s.csv' % calc_date.strftime('%y%m%d%H')))



det = Detection(file_root)
det.calc_point('/mnt/disk/weather_project/xxx', '17010108', '17013020')  # '17013020'


