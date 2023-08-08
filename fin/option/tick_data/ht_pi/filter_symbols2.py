#!/usr/bin/env python3
# encoding:utf-8

"""
(Copyright) 2018, Winton Wang <365504029@qq.com>

ctpwrapper is free software: you can redistribute it and/or modify
it under the terms of the GNU LGPLv3 as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ctpwrapper.  If not, see <http://www.gnu.org/licenses/>.

"""
import json
import socket
import urllib.parse
from contextlib import closing
import time
from ctpwrapper import ApiStructure
from ctpwrapper import TraderApiPy

symbols_keep = ['^SHFE.rb\d+$', '^SHFE.al\d+$', '^DCE.v\d+$', '^DCE.pp\d+$', '^DCE.m\d+$', '^DCE.c\d+$', '^DCE.b\d+$', '^DCE.a\d+$', '^CZCE.ma\d+$']

def check_address_port(tcp):
    """
    :param tcp:
    :return:
    """
    host_schema = urllib.parse.urlparse(tcp)

    ip = host_schema.hostname
    port = host_schema.port

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((ip, port)) == 0:
            return True  # OPEN
        else:
            return False  # closed


class Trader(TraderApiPy):

    def __init__(self, app_id, auth_code, broker_id, investor_id, password, request_id=100):
        self.app_id = app_id
        self.auth_code = auth_code
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.password = password
        self._request_id = request_id
        self.login = False

    @property
    def request_id(self):
        self._request_id += 1
        return self._request_id

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        print("OnRspError:")
        print("requestID:", nRequestID)
        print(pRspInfo)
        print(bIsLast)

    def OnHeartBeatWarning(self, nTimeLapse):
        """心跳超时警告。当长时间未收到报文时，该方法被调用。
        @param nTimeLapse 距离上次接收报文的时间
        """
        print("OnHeartBeatWarning time: ", nTimeLapse)

    def OnFrontDisconnected(self, nReason):
        print("OnFrontConnected:", nReason)

    def OnFrontConnected(self):
        print("OnFrontConnected")
        authenticate = ApiStructure.ReqAuthenticateField(BrokerID=self.broker_id,
                                                         UserID=self.investor_id,
                                                         AppID=self.app_id,
                                                         AuthCode=self.auth_code)

        self.ReqAuthenticate(authenticate, self.request_id)

    def OnRspAuthenticate(self, pRspAuthenticateField, pRspInfo, nRequestID, bIsLast):

        print("OnRspAuthenticate")
        print("pRspInfo:", pRspInfo)
        print("nRequestID:", nRequestID)
        print("bIsLast:", bIsLast)

        if pRspInfo.ErrorID == 0:
            req = ApiStructure.ReqUserLoginField(BrokerID=self.broker_id,
                                                 UserID=self.investor_id,
                                                 Password=self.password)
            self.ReqUserLogin(req, self.request_id)
        else:
            print("auth failed")

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        print("OnRspUserLogin")
        print("nRequestID:", nRequestID)
        print("bIsLast:", bIsLast)
        print("pRspInfo:", pRspInfo)

        # if pRspInfo.ErrorID != 0:
        #     print("RspInfo:", pRspInfo)
        # else:
        #     print("trader user login successfully")
        #     self.login = True
        #     print("pRspUserLogin:", pRspUserLogin)

        if pRspInfo.ErrorID != 0:
            print("RspInfo:", pRspInfo)
        else:
            print("trader user login successfully")
            self.login = True
            print("pRspUserLogin:", pRspUserLogin)

        if self.login:
            try:
                req = api.CThostFtdcQryInstrumentField()
                # ctypes.memset(id(req), 0, ctypes.sizeof(req))
                req = self.tapi.ReqQryInstrument(req, 0)
                print ("send ReqQryInstrument ok")
            except Exception as ex:
                print(ex)

    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        """
        """
        print("OnRspSettlementInfoConfirm")
        print("nRequestID:", nRequestID)
        print("bIsLast:", bIsLast)
        print("pRspInfo:", pRspInfo)

        print(pSettlementInfoConfirm)

    def OnRspQryInvestor(self, pInvestor, pRspInfo, nRequestID, bIsLast):
        """
        """
        print("OnRspQryInvestor")
        print("nRequestID:", nRequestID)
        print("bIsLast:", bIsLast)
        print("pRspInfo:", pRspInfo)
        print("pInvestor:", pInvestor)

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        print("OnRspQryInvestorPosition")
        print("nRequestID:", nRequestID)
        print("bIsLast:", bIsLast)
        print("pRspInfo:", pRspInfo)
        print("pInvestorPosition:", pInvestorPosition)

    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        print("OnRspQryTradingAccount")
        print("nRequestID:", nRequestID)
        print("bIsLast:", bIsLast)
        print("pRspInfo:", pRspInfo)
        print("pTradingAccount:", pTradingAccount)

    def OnRspQryInstrument(self, pInstrument: 'CThostFtdcInstrumentField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> 'void':
        # print('##################')
        # print(pInstrument)
        # print(pRspInfo)
        print(pInstrument.InstrumentID) # pInstrument.InstrumentName, 

        symbol = '%s.%s' % (pInstrument.ExchangeID, pInstrument.ExchangeInstID.lower())
        for s in symbols_keep:
            # if s in symbol:
            # if re.search(s, symbol):
            if re.match(s, symbol):
                with open('symbols.txt', 'a+', encoding='utf-8') as f:
                # f.write('%s|%s|%s|%s|%s|%s|%s\n' % (pInstrument.InstrumentID, pInstrument.ExchangeInstID, pInstrument.ProductID, pInstrument.UnderlyingInstrID, pInstrument.ExchangeID, pInstrument.InstrumentName, pInstrument.ProductClass))
                    f.write('%s|%s|%s|%s|%s|%s|%s|%s|%s\n' % (pInstrument.InstrumentID, pInstrument.ExchangeInstID, pInstrument.ProductID, pInstrument.UnderlyingInstrID, pInstrument.ExchangeID, pInstrument.InstrumentName, pInstrument.ProductClass, pInstrument.StrikePrice, pInstrument.CombinationType))
                break


def main():
    json_file = open("config.json")
    config = json.load(json_file)
    json_file.close()

    print(config)

    investor_id = config["investor_id"]
    broker_id = config["broker_id"]
    password = config["password"]
    server = config["trader_server"]
    app_id = config["app_id"]
    auth_code = config["auth_code"]

    if check_address_port(server):

        user_trader = Trader(broker_id=broker_id, app_id=app_id, auth_code=auth_code,
                             investor_id=investor_id, password=password)

        user_trader.Create()
        user_trader.RegisterFront(server)
        user_trader.SubscribePrivateTopic(2)  # 只传送登录后的流内容

        user_trader.Init()

        print("trader api started")
        print("trading day:", user_trader.GetTradingDay())

        if user_trader.login:
            investor = ApiStructure.QryInvestorField(broker_id, investor_id)

            user_trader.ReqQryInvestor(investor, user_trader.request_id)

            # position = ApiStructure.QryInvestorPositionField.from_dict({"BrokerID": broker_id,
            #                                                             "InvestorID": investor_id})
            # user_trader.ReqQryInvestorPosition(position, user_trader.request_id)

            settlement_info = ApiStructure.SettlementInfoConfirmField.from_dict({"BrokerID": broker_id,
                                                                                 "InvestorID": investor_id})

            user_trader.ReqSettlementInfoConfirm(settlement_info, user_trader.request_id)

            trader_account = ApiStructure.QryTradingAccountField(BrokerID=broker_id, InvestorID=investor_id, BizType="1")
            user_trader.ReqQryTradingAccount(trader_account, user_trader.request_id)

            user_trader.Join()

    else:
        print("trader server down")


if __name__ == "__main__":
    main()
