
import os
from datetime import datetime
import backtrader as bt

import pandas as pd
from lutils.stock import LTdxHq

import matplotlib.pyplot as plt

import traceback
import numpy as np
import tushare as ts
import pandas as pd

from mpl_toolkits.mplot3d import Axes3D  #绘制三D图形

from sklearn.cluster import KMeans, AffinityPropagation
from sklearn.cluster import SpectralClustering
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction import FeatureHasher, DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import Binarizer
from sklearn.feature_extraction.text import TfidfVectorizer



# 获取股票基本信息，包括 PE、PB 值
ts.set_token('42731ca565c5d019007ef5cd7db7808757b2ea3fdbfb31d4f7b6144b')
pro = ts.pro_api()


if os.path.exists('df_todays.pkl'):
    df_base = pd.read_pickle('df_base.pkl')
else:
    df_base = pro.stock_basic() # ts.get_stock_basics()
    # df_base['code'] = df_base.index
    df_base.to_pickle('df_base.pkl')


if os.path.exists('df_todays.pkl'):
    df_todays = pd.read_pickle('df_todays.pkl')
else:
    # 获取股票当天数据，包括当前股价
    df_todays = ts.get_today_all()
    # df_todays['code'] = df_todays.index
    df_todays.to_pickle('df_todays.pkl')

if os.path.exists('df_roe.pkl'):
    df_roe = pd.read_pickle('df_roe.pkl')
else:
    df_roe = ts.get_report_data(2022, 3)
    df_roe.to_pickle('df_roe.pkl')
# df_roe['code'] = df_roe.index




df_base['code'] = df_base['ts_code'].str.slice(stop=-3)
df_roe = df_roe.drop_duplicates()



df = pd.merge(df_todays, df_base, how='left', on=['code'])
df = pd.merge(df, df_roe, how='left', on=['code'])
roe_describe = df['roe'].describe() # ?

df.dropna()
result = df[(0 < df['pb']) 
            & (df['pb'] < 8)
            & (-20 < df['roe']) 
            & (df['roe'] < 30) 
            & (0 < df['trade']) 
            & (df['trade'] < 70)
            & (-100<df['per']) 
            & (df['per']<200)]



columns = ['pb', 'roe', 'trade']


scaler = MinMaxScaler()
scaler.fit(result[columns])
X = pd.DataFrame(scaler.transform(result[columns]), columns=columns)


model = SpectralClustering(n_clusters=7, affinity='nearest_neighbors', assign_labels='kmeans')
# model = DBSCAN(eps=0.6, min_samples=10)
# model = AffinityPropagation(random_state=5)
y_kmeans = model.fit_predict(X[columns])



fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# X = result['pb'].tolist() # X 轴为 PB 数据 
# Y = result['roe'].tolist()
# Z = result['trade'].tolist() # Z 轴为 股价数据 

ax.set_xlabel('PB', color='g')
ax.set_ylabel('roe', color='g')
# ax.set_zlabel('trade', color='b') # 给三个坐标轴注明
ax.set_zlabel('PER', color='b') # 给三个坐标轴注明

# ax.scatter(X['pb'], X['roe'], X['trade'], c=y_kmeans==5)
ax.scatter(X['pb'], X['roe'], X['trade'], c=y_kmeans)
# ax.scatter(X['pb'], X['roe'], X['per'], c=y_kmeans)

plt.show()