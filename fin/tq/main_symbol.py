import tqsdk
# import numpy as np
import time
import json


api = tqsdk.TqApi(auth=tqsdk.TqAuth('ahaha', '330300'))

symbol_start = "SHFE.rb"
main_symbol = 'KQ.m@' + symbol_start

#获取全部历史相关合约
symbol_all =  [x for x in api._data.quotes if symbol_start == x[:len(symbol_start)]]
#获取主连行情
main_symbol_kline = api.get_kline_serial(main_symbol, 60*60*24, 8000)
#得到主连,时间:成交量字典
d={ main_symbol_kline.datetime.iloc[x] :main_symbol_kline.volume.iloc[x] for x in range(8000) if main_symbol_kline.datetime.iloc[x]>0}
#获取全部历史相关合约的行情
all_kline = [api.get_kline_serial(x, 60*60*24, 8000) for x in symbol_all]
#得到全部合约的,时间:(成交量,合约名字)字典
l=[]
for x in all_kline:
    d1={}
    for y in range(8000):
        if x.datetime.iloc[y]>0:
            d1[x.datetime.iloc[y]]=(x.volume.iloc[y],x.symbol.iloc[y])
    l.append(d1)

#遍历对比相同时间,成交量相同,就把合约名字和时间形成新字典
newd={}
for x in d:
    for y in l:
        if x in y :
            if d[x]==y[x][0]:
                newd[x]=y[x][1]
#寻找相同值,但索引最小的
d={}
for x in newd:
    if newd[x] not in d:
        d[newd[x]]=x
    else:
        if x<d[newd[x]]:
            d[newd[x]]=x

#讲时间为建,合约名为字典,写入记事本
fd={}
for x in d:
    a=time.localtime(d[x]/1e9)
    b=time.strftime('%Y-%m-%d',a)
    fd[b]=x
f = open(symbol_start + "_change.txt",'w')
f.write(str(fd))
f.close()

#讲每日是哪个品种写入记事本,改成日期为年月日了,不用时间戳了
d={}
for x in newd:
    a=time.localtime(x/1e9)
    b=time.strftime('%Y-%m-%d',a)
    d[b]=newd[x]
f = open(symbol_start+ "_days.txt",'w')
f.write(json.dumps(d))
f.close()    
api.close()



