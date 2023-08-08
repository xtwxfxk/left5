# -*- coding: utf-8 -*-
import os, datetime, json, traceback
import threading
import queue
# from multiprocessing import Process, Queue

import logging
import logging.config
from configparser import ConfigParser, MissingSectionHeaderError

import thostmduserapi as mdapi
import thosttraderapi as api

data_queue = queue.Queue(maxsize=1000)

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

ROOT = os.getcwd()
LOG_DIR = os.path.join(ROOT, 'logs')
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

config = ConfigParser()
try:
    config.read('settings.ini', encoding='utf-8')
except MissingSectionHeaderError:
    config.read('settings.ini', encoding='utf-8-sig')


FrontAddr = config['setting']['FrontAddr'] # "tcp://180.168.146.187:10211" # 行情
# FrontAddr='tcp://180.168.146.187:10130'
#LoginInfo
BROKERID = config['setting']['BROKERID']
USERID = config['setting']['USERID']
PASSWORD = config['setting']['PASSWORD']

AppID = config['setting']['AppID']
AuthCode = config['setting']['AuthCode']


SAVE_DIR = config['setting']['SaveDir']
if not os.path.exists(SAVE_DIR): os.makedirs(SAVE_DIR)

def load_symbols():
    logger.info('开始读取代码文件...')
    symbols = []
    if os.path.exists('symbols.txt'):
        for line in open('symbols.txt', encoding='utf-8'):
            if line.strip():
                ds = line.split('|')
                c = ds[0].encode('utf-8')
                if c not in symbols:
                    symbols.append(c)
    logger.info('订阅数量 %s' % len(symbols))
    return symbols

class CFtdcMdSpi(mdapi.CThostFtdcMdSpi):
    tapi=''
    def __init__(self, tapi, data_queue):
        mdapi.CThostFtdcMdSpi.__init__(self)
        self.tapi = tapi
        self.data_queue = data_queue
        self.symbols = load_symbols()

    def OnFrontConnected(self):
        logger.info("OnFrontConnected")
        loginfield = mdapi.CThostFtdcReqUserLoginField()

        loginfield.BrokerID = BROKERID
        loginfield.UserID = USERID
        loginfield.Password = PASSWORD
        loginfield.UserProductInfo = "python dll"
        self.tapi.ReqUserLogin(loginfield,0)


    def OnRspUserLogin(self, *args):
        logger.info("OnRspUserLogin")
        rsploginfield=args[0]
        rspinfofield=args[1]
        logger.info("SessionID=%s" % rsploginfield.SessionID)
        logger.info("ErrorID=%s" % rspinfofield.ErrorID)
        logger.info("ErrorMsg=%s" % rspinfofield.ErrorMsg)

        ret = self.tapi.SubscribeMarketData(self.symbols, len(self.symbols))
        logger.info('SubscribeMarketData: %s' % ret)

    def OnRtnDepthMarketData(self, *args):
        try:
            # logger.info("OnRtnDepthMarketData")
            field = args[0]
            # logger.info("InstrumentID=%s" % field.InstrumentID)
            # logger.info("LastPrice=%s" % field.LastPrice)

            # logger.info(field)

            tick_data = {
                'TradingDay': field.TradingDay, 
                'InstrumentID': field.InstrumentID, 
                'ExchangeID': field.ExchangeID, 
                'ExchangeInstID': field.ExchangeInstID, 
                'LastPrice': field.LastPrice, 
                'PreSettlementPrice': field.PreSettlementPrice, 
                'PreClosePrice': field.PreClosePrice, 
                'PreOpenInterest': field.PreOpenInterest, 
                'OpenPrice': field.OpenPrice, 
                'HighestPrice': field.HighestPrice, 
                'LowestPrice': field.LowestPrice, 
                'Volume': field.Volume, 
                'Turnover': field.Turnover, 
                'OpenInterest': field.OpenInterest, 
                'ClosePrice': field.ClosePrice, 
                'SettlementPrice': field.SettlementPrice, 
                'UpperLimitPrice': field.UpperLimitPrice, 
                'LowerLimitPrice': field.LowerLimitPrice, 
                'PreDelta': field.PreDelta, 
                'CurrDelta': field.CurrDelta, 
                'UpdateTime': field.UpdateTime, 
                'UpdateMillisec': field.UpdateMillisec, 
                'BidPrice1': field.BidPrice1, 
                'BidVolume1': field.BidVolume1, 
                'AskPrice1': field.AskPrice1, 
                'AskVolume1': field.AskVolume1, 
                'BidPrice2': field.BidPrice2, 
                'BidVolume2': field.BidVolume2, 
                'AskPrice2': field.AskPrice2, 
                'AskVolume2': field.AskVolume2, 
                'BidPrice3': field.BidPrice3, 
                'BidVolume3': field.BidVolume3, 
                'AskPrice3': field.AskPrice3, 
                'AskVolume3': field.AskVolume3, 
                'BidPrice4': field.BidPrice4, 
                'BidVolume4': field.BidVolume4, 
                'AskPrice4': field.AskPrice4, 
                'AskVolume4': field.AskVolume4, 
                'BidPrice5': field.BidPrice5, 
                'BidVolume5': field.BidVolume5, 
                'AskPrice5': field.AskPrice5, 
                'AskVolume5': field.AskVolume5, 
                'AveragePrice': field.AveragePrice, 
                'ActionDay': field.ActionDay, 
                'BandingUpperPrice': field.BandingUpperPrice, 
                'BandingLowerPrice': field.BandingLowerPrice}

            self.data_queue.put(tick_data)

        except Exception as ex:
            logger.error(ex, exc_info=True)


    def OnRspSubMarketData(self, *args):
        logger.info("OnRspSubMarketData")
        field=args[0]
        logger.info("InstrumentID=%s" % field.InstrumentID)
        rspinfofield=args[1]
        logger.info("ErrorID=%s" % rspinfofield.ErrorID)
        logger.info("ErrorMsg=%s" % rspinfofield.ErrorMsg)

    def OnFrontDisconnected(self, nReason):
        logger.info('OnFrontDisconnected %s' % nReason)
        logger.info('Reload Symbols')
        _symbols = load_symbols()
        if len(_symbols) > 0:
            self.symbols = _symbols
        

def ctp_process(data_queue):
    mduserapi = mdapi.CThostFtdcMdApi_CreateFtdcMdApi()
    logger.info("版本号为: %s" % mduserapi.GetApiVersion())
    mduserspi = CFtdcMdSpi(mduserapi, data_queue)
    mduserapi.RegisterSpi(mduserspi)
    mduserapi.RegisterFront(FrontAddr)

    mduserapi.Init()
    mduserapi.Join()

def data_process(data_queue):

    while True:
        try:
            tick_data = data_queue.get()

            today = datetime.date.today().strftime('%Y-%m-%d')
            day_dir = os.path.join(SAVE_DIR, today)
            if not os.path.exists(day_dir):
                os.makedirs(day_dir)
            file_path = os.path.join(day_dir, tick_data['InstrumentID'])

            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write('%s\n' % json.dumps(tick_data))

                # f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (field.TradingDay, field.InstrumentID, field.ExchangeID, field.ExchangeInstID, field.LastPrice, field.PreSettlementPrice, field.PreClosePrice, field.PreOpenInterest, field.OpenPrice, field.HighestPrice, field.LowestPrice, field.Volume, field.Turnover, field.OpenInterest, field.ClosePrice, field.SettlementPrice, field.UpperLimitPrice, field.LowerLimitPrice, field.PreDelta, field.CurrDelta, field.UpdateTime, field.UpdateMillisec, field.BidPrice1, field.BidVolume1, field.AskPrice1, field.AskVolume1, field.BidPrice2, field.BidVolume2, field.AskPrice2, field.AskVolume2, field.BidPrice3, field.BidVolume3, field.AskPrice3, field.AskVolume3, field.BidPrice4, field.BidVolume4, field.AskPrice4, field.AskVolume4, field.BidPrice5, field.BidVolume5, field.AskPrice5, field.AskVolume5, field.AveragePrice, field.ActionDay, field.BandingUpperPrice, field.BandingLowerPrice))

        except Exception as ex:
            logger.error(ex, exc_info=True)

def main():
    ctp_thread = threading.Thread(target=ctp_process, args=(data_queue,)) #, daemon=True)
    data_thread = threading.Thread(target=data_process, args=(data_queue,)) #, daemon=True)

    # ctp_thread = Process(target=ctp_process, args=(data_queue,))
    # data_thread = Process(target=data_process, args=(data_queue,))
    
    ctp_thread.start()
    data_thread.start()

    ctp_thread.join()
    logger.info('ctp_thread over')
    data_thread.join()
    logger.info('data_thread over')



if __name__ == '__main__':
    main()
