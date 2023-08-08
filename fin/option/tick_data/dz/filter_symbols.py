# -*- coding: utf-8 -*-
import thosttraderapi as api
import time
import json

#Addr
FrontAddr='tcp://114.80.55.177:41207' # tcp://180.168.146.187:10201 tcp://218.202.237.33:10213
#FrontAddr="tcp://180.168.146.187:10130"
#LoginInfo
BROKERID= '3010' # "1022"
USERID= '16105655' #'00186' # "086644"
PASSWORD= 'xt289269' # "123456"

AppID="client_llcc888_1.0"
AuthCode="M98GJZ1SHC6A23T8"

# 只过滤需要的
symbols_keep = ['SHFE.rb', 'SHFE.al', 'DCE.v', 'DCE.pp', 'DCE.m', 'DCE.c', 'DCE.b', 'DCE.a', 'CZCE.ma']

class CTradeSpi(api.CThostFtdcTraderSpi):
    tapi=''
    def __init__(self,tapi):
        api.CThostFtdcTraderSpi.__init__(self)
        self.tapi=tapi
        
    def OnFrontConnected(self) -> "void":
        print ("OnFrontConnected")
        authfield = api.CThostFtdcReqAuthenticateField()
        authfield.BrokerID=BROKERID
        authfield.UserID=USERID
        authfield.AppID=AppID
        authfield.AuthCode=AuthCode
        # 客户端认证请求  需要填入用户名和穿透appid 和穿透认证码
        self.tapi.ReqAuthenticate(authfield, 0)

        print ("send login ok")
    def OnRspAuthenticate(self, pRspAuthenticateField: 'CThostFtdcRspAuthenticateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void": 
        print ("BrokerID=",pRspAuthenticateField.BrokerID)
        print ("UserID=",pRspAuthenticateField.UserID)
        print ("AppID=",pRspAuthenticateField.AppID)
        print ("AppType=",pRspAuthenticateField.AppType)
        print ("ErrorID=",pRspInfo.ErrorID)
        print ("ErrorMsg=",pRspInfo.ErrorMsg)
        if not pRspInfo.ErrorID :
            print("验证穿透已完成,开始登录")
            loginfield = api.CThostFtdcReqUserLoginField()
            loginfield.BrokerID=BROKERID
            loginfield.UserID=USERID
            loginfield.Password=PASSWORD

            loginfield.UserProductInfo="python dll"
            # 请求账户登录
            time.sleep(2)
            self.tapi.ReqUserLogin(loginfield,0)
            print ("send login ok")
    def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
        print ("OnRspUserLogin")
        print ("TradingDay=",pRspUserLogin.TradingDay)
        print ("SessionID=",pRspUserLogin.SessionID)
        print ("ErrorID=",pRspInfo.ErrorID)
        print ("ErrorMsg=",pRspInfo.ErrorMsg)

        try:
            req = api.CThostFtdcQryInstrumentField()
            # ctypes.memset(id(req), 0, ctypes.sizeof(req))
            req = self.tapi.ReqQryInstrument(req, 0)
            print ("send ReqQryInstrument ok")
        except Exception as ex:
            print(ex)

    def OnRspQryInstrument(self, pInstrument: 'CThostFtdcInstrumentField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> 'void':
        # print('##################')
        # print(pInstrument)
        # print(pRspInfo)
        print(pInstrument.InstrumentID) # pInstrument.InstrumentName, 

        symbol = '%s.%s' % (pInstrument.ExchangeID, pInstrument.ExchangeInstID.lower())
        for s in symbols_keep:
            if s in symbol:
                with open('symbols.txt', 'a+', encoding='utf-8') as f:
                # f.write('%s|%s|%s|%s|%s|%s|%s\n' % (pInstrument.InstrumentID, pInstrument.ExchangeInstID, pInstrument.ProductID, pInstrument.UnderlyingInstrID, pInstrument.ExchangeID, pInstrument.InstrumentName, pInstrument.ProductClass))
                    f.write('%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pInstrument.InstrumentID, pInstrument.ExchangeInstID, pInstrument.ProductID, pInstrument.UnderlyingInstrID, pInstrument.ExchangeID, pInstrument.InstrumentName, pInstrument.ProductClass, pInstrument.StrikePrice, pInstrument.CombinationType))
                break

        

def main():
    tradeapi=api.CThostFtdcTraderApi_CreateFtdcTraderApi()
    tradespi=CTradeSpi(tradeapi)
    tradeapi.RegisterSpi(tradespi)
    tradeapi.SubscribePrivateTopic(api.THOST_TERT_QUICK)
    tradeapi.SubscribePublicTopic(api.THOST_TERT_QUICK)
    tradeapi.RegisterFront(FrontAddr)
    tradeapi.Init()
    tradeapi.Join()
    
if __name__ == '__main__':
    main()
