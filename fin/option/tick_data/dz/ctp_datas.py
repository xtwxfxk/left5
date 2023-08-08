# -*- coding: utf-8 -*-
import os, datetime, json, traceback
import threading
import queue
# from multiprocessing import Process, Queue

import logging
import logging.config
from configparser import ConfigParser, MissingSectionHeaderError

import ctp_api.thostmduserapi as mdapi
import ctp_api.thosttraderapi as api

from utils import load_symbols


logging.config.fileConfig('logging.conf')
logger = logging.getLogger('verbose')

class CFtdcMdSpi(mdapi.CThostFtdcMdSpi):
    tapi=''
    def __init__(self, tapi, broker_id, user_id, password, data_queue):
        mdapi.CThostFtdcMdSpi.__init__(self)
        self.tapi = tapi
        self.BROKERID = broker_id
        self.USERID = user_id
        self.PASSWORD = password
        self.data_queue = data_queue
        self.symbols = load_symbols()

    def OnFrontConnected(self):
        logger.info("OnFrontConnected")
        loginfield = mdapi.CThostFtdcReqUserLoginField()

        loginfield.BrokerID = self.BROKERID
        loginfield.UserID = self.USERID
        loginfield.Password = self.PASSWORD
        loginfield.UserProductInfo = "python dll"
        self.tapi.ReqUserLogin(loginfield, 0)


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


def ctp_process(front_addr, broker_id, user_id, password, data_queue):

    mduserapi = mdapi.CThostFtdcMdApi_CreateFtdcMdApi()
    logger.info("版本号为: %s" % mduserapi.GetApiVersion())
    mduserspi = CFtdcMdSpi(mduserapi, broker_id, user_id, password, data_queue)
    mduserapi.RegisterSpi(mduserspi)
    mduserapi.RegisterFront(front_addr)

    mduserapi.Init()
    mduserapi.Join()

# f.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (field.TradingDay, field.InstrumentID, field.ExchangeID, field.ExchangeInstID, field.LastPrice, field.PreSettlementPrice, field.PreClosePrice, field.PreOpenInterest, field.OpenPrice, field.HighestPrice, field.LowestPrice, field.Volume, field.Turnover, field.OpenInterest, field.ClosePrice, field.SettlementPrice, field.UpperLimitPrice, field.LowerLimitPrice, field.PreDelta, field.CurrDelta, field.UpdateTime, field.UpdateMillisec, field.BidPrice1, field.BidVolume1, field.AskPrice1, field.AskVolume1, field.BidPrice2, field.BidVolume2, field.AskPrice2, field.AskVolume2, field.BidPrice3, field.BidVolume3, field.AskPrice3, field.AskVolume3, field.BidPrice4, field.BidVolume4, field.AskPrice4, field.AskVolume4, field.BidPrice5, field.BidVolume5, field.AskPrice5, field.AskVolume5, field.AveragePrice, field.ActionDay, field.BandingUpperPrice, field.BandingLowerPrice))