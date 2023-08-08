# -*- coding: utf-8 -*-
import thosttraderapi as api
import time
import json

#Addr
FrontAddr='tcp://180.168.146.187:10201' # tcp://180.168.146.187:10201 tcp://218.202.237.33:10213
# FrontAddr='tcp://180.168.146.187:10130' # 7*24

#LoginInfo
BROKERID="9999"
USERID='208571' # "086644"
PASSWORD='abc#2dAde654' # "123456"

DIRECTION=api.THOST_FTDC_D_Sell
AppID="simnow_client_test"
AuthCode="0000000000000000"
#DIRECTION=api.THOST_FTDC_D_Buy
#open
OFFSET="0"
#close
#OFFSET="1"

def ReqorderfieldInsert(tradeapi):
    print ("ReqOrderInsert Start")
    orderfield=api.CThostFtdcInputOrderField()
    orderfield.BrokerID=BROKERID
    orderfield.InstrumentID=INSTRUMENTID
    orderfield.UserID=USERID
    orderfield.InvestorID=USERID
    orderfield.Direction=DIRECTION
    orderfield.LimitPrice=PRICE
    orderfield.VolumeTotalOriginal=VOLUME
    orderfield.OrderPriceType=api.THOST_FTDC_OPT_LimitPrice
    orderfield.ContingentCondition = api.THOST_FTDC_CC_Immediately
    orderfield.TimeCondition = api.THOST_FTDC_TC_GFD
    orderfield.VolumeCondition = api.THOST_FTDC_VC_AV
    orderfield.CombHedgeFlag="1"
    orderfield.CombOffsetFlag=OFFSET
    orderfield.GTDDate=""
    orderfield.OrderRef="1"
    orderfield.MinVolume = 0
    orderfield.ForceCloseReason = api.THOST_FTDC_FCC_NotForceClose
    orderfield.IsAutoSuspend = 0
    tradeapi.ReqOrderInsert(orderfield,0)
    print ("ReqOrderInsert End")
    

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
        self.tapi.ReqAuthenticate(authfield,0)

        print ("send login ok")
    def OnRspAuthenticate(self, pRspAuthenticateField: 'CThostFtdcRspAuthenticateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void": 
        print ("BrokerID=",pRspAuthenticateField.BrokerID)
        print ("UserID=",pRspAuthenticateField.UserID)
        #print ("AppID=",pRspAuthenticateField.AppID)
        #print ("AppType=",pRspAuthenticateField.AppType)       
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
        with open('option_codes.txt', 'a+', encoding='utf-8') as f:
            # f.write('%s|%s|%s|%s|%s|%s|%s\n' % (pInstrument.InstrumentID, pInstrument.ExchangeInstID, pInstrument.ProductID, pInstrument.UnderlyingInstrID, pInstrument.ExchangeID, pInstrument.InstrumentName, pInstrument.ProductClass))
            f.write('%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pInstrument.InstrumentID, pInstrument.ExchangeInstID, pInstrument.ProductID, pInstrument.UnderlyingInstrID, pInstrument.ExchangeID, pInstrument.InstrumentName, pInstrument.ProductClass, pInstrument.StrikePrice, pInstrument.CombinationType))
            # f.write('%s\n' % json.dumps(pInstrument))

    #     qryinfofield = api.CThostFtdcQrySettlementInfoField()
    #     qryinfofield.BrokerID=BROKERID
    #     qryinfofield.InvestorID=USERID
    #     qryinfofield.TradingDay=pRspUserLogin.TradingDay
    #     self.tapi.ReqQrySettlementInfo(qryinfofield,0)
    #     print ("send ReqQrySettlementInfo ok")
        

    # def OnRspQrySettlementInfo(self, pSettlementInfo: 'CThostFtdcSettlementInfoField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
    #     print ("OnRspQrySettlementInfo")
    #     if  pSettlementInfo is not None :
    #         print ("content:",pSettlementInfo.Content)
    #     else :
    #         print ("content null")
    #     if bIsLast :
    #         pSettlementInfoConfirm=api.CThostFtdcSettlementInfoConfirmField()
    #         pSettlementInfoConfirm.BrokerID=BROKERID
    #         pSettlementInfoConfirm.InvestorID=USERID
    #         self.tapi.ReqSettlementInfoConfirm(pSettlementInfoConfirm,0)
    #         print ("send ReqSettlementInfoConfirm ok")
        
    # def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: 'CThostFtdcSettlementInfoConfirmField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
    #     print ("OnRspSettlementInfoConfirm")
    #     print ("ErrorID=",pRspInfo.ErrorID)
    #     print ("ErrorMsg=",pRspInfo.ErrorMsg)

    #     ReqorderfieldInsert(self.tapi)
    #     print ("send ReqorderfieldInsert ok")


    # def OnRtnOrder(self, pOrder: 'CThostFtdcOrderField') -> "void":
    #     print ("OnRtnOrder")
    #     print ("OrderStatus=",pOrder.OrderStatus)
    #     print ("StatusMsg=",pOrder.StatusMsg)
    #     print ("LimitPrice=",pOrder.LimitPrice)
        
    # def OnRspOrderInsert(self, pInputOrder: 'CThostFtdcInputOrderField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
    #     print ("OnRspOrderInsert")
    #     print ("ErrorID=",pRspInfo.ErrorID)
    #     print ("ErrorMsg=",pRspInfo.ErrorMsg)
        
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
