var firstCmmdty = {};
var recommendProductInfo = "";
var version = "";
var shoppingCartUrl = "";
var b2c_fc_authid = "";
var dfpToken_str = "";
var regionInfo1;
var sa = sa || {};
sa.maxLength = 100;
sa.openAPI = true;
var cart = cart || {};
var jigsawObj;
cart.normal = (function ($) {
    var addToCart = function (jsonObj, callback) {
        if (typeof (callback) != "function") {
            alert("鏈紶鍏ュ弬鏁帮細鍥炶皟鍑芥暟callback锛�");
            return
        }
        var cmmdtyVOList = jsonObj.cmmdtyVOList;
        if (typeof (cmmdtyVOList) == "undefined" || cmmdtyVOList == null || cmmdtyVOList.length == 0) {
            alert("鏈紶鍏ュ弬鏁帮細鍟嗗搧淇℃伅cmmdtyVOList锛�");
            return
        }
        firstCmmdty = cmmdtyVOList[0];
        cmmdtyVOList[0].activityType = cmmdtyVOList[0].activityType || "01";
        cmmdtyVOList[0].activityId = cmmdtyVOList[0].activityId || "";
        cmmdtyVOList[0].shopCode = cmmdtyVOList[0].shopCode || "";
        var verifyCode = "";
        if (cart.security.getNeedVerifyCodeVal()) {
            var tempVerifyCode = cart.security.getVerifyCodeVal();
            var tempDefaultValue = cart.security.getDefaultValue();
            if (tempVerifyCode != undefined && tempVerifyCode != "" && tempVerifyCode != tempDefaultValue) {
                verifyCode = tempVerifyCode
            }
            cart.security.setNeedVerifyCodeVal(false)
        }
        if (typeof (bd) != "undefined") {
            cart.common.setCookie("c2dt", bd.rst())
        }
        jsonObj.verifyCode = verifyCode;
        jsonObj.uuid = cart.security.getUUID();
        jsonObj.sceneId = cart.security.getSceneId();
        jsonObj.dfpToken = dfpToken_str;
        var targetUrl = "//shopping.suning.com/addCart.do?callback=?";
        try {
            var collect;
            jsonObj.cmmdtyVOList.forEach(function (cmmdty) {
                if (typeof (cmmdty.collect) != "undefined" && cmmdty.collect != null && cmmdty.collect.length > 0) {
                    collect = cmmdty.collect;
                    cmmdty.collect = []
                }
                var c = cmmdty.childCmmdtyVOList;
                if (typeof (c) != "undefined" && c != null && c.length > 0) {
                    cmmdty.childCmmdtyVOList.forEach(function (childC) {
                        collect = childC.collect;
                        childC.collect = []
                    })
                }
            });
            if (typeof (collect) != "undefined" && collect != null && collect.length > 0) {
                jsonObj.collect = collect
            }
        } catch (e) {
            sendUomMsgV2("2", "ccf-gwc1-20000_CCF_SYS_9999", "0", "addcart", e.message)
        }
        var params = {
            cartVO: cart.common.obj2string(jsonObj)
        };
        ajaxCrossDomain(targetUrl, $.param(params), function (data) {
            cartSuccessCallBack(data, callback)
        }, function () {
            cartFailCallBack(callback)
        }, cart.common.passport_config);
        if (cmmdtyVOList[0].activityType != "06") {
            cart.analytics.savePageSaleInfo(cmmdtyVOList[0].cmmdtyCode, cmmdtyVOList[0].shopCode)
        }
    };
    var cartSuccessCallBack = function (respData, callerCallBack) {
        var resp = {};
        resp.analyticsType = "Addcart";
        resp.result = "0";
        var returnCode = respData.returnCode;
        if (null != returnCode && "" != returnCode && "4000" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            cart.analytics.recordErrorMsg(resp);
            callerCallBack(resp);
            return
        }
        var result = respData.isSuccess;
        if (result == "Y") {
            var param = {
                pid: firstCmmdty.cmmdtyCode,
                vid: firstCmmdty.shopCode,
                storeId: sn.storeId,
                catalogId: sn.catalogId,
                langId: "-7",
                cartFlag: "B"
            };
            shoppingCartUrl = "//shopping.suning.com/cart.do?" + $.param(param);
            resp.result = "1";
            resp.url = shoppingCartUrl
        } else {
            var errorCode, errorMsg;
            if (respData.addCartErrorList != undefined && respData.addCartErrorList[0] != undefined) {
                errorCode = respData.addCartErrorList[0].errorCode;
                errorMsg = respData.addCartErrorList[0].errorMessage
            }
            if (errorCode == "017") {
                resp.failCode = errorCode;
                resp.failMsg = errorMsg;
                resp.uuid = respData.uuid;
                cart.security.setNeedVerifyCodeVal(true)
            } else {
                if (errorCode == "018") {
                    resp.failCode = errorCode;
                    resp.failMsg = "澶у畻璐墿璇峰埌浼佷笟鐢ㄦ埛娓犻亾锛屽皬鑻忕殑鏈嶅姟浼氭洿璐村績锛�"
                } else {
                    if (errorCode == "019") {
                        resp.failCode = errorCode;
                        resp.failMsg = errorMsg
                    } else {
                        if (errorCode == "015" || errorCode == "025") {
                            resp.failCode = errorCode;
                            resp.failMsg = errorMsg
                        } else {
                            if (errorCode == "024") {
                                resp.failCode = errorCode;
                                resp.failMsg = "鎮ㄧ櫥闄嗙殑璐﹀彿鏈夊紓甯革紝璇疯仈绯诲湪绾垮鏈嶅鐞�"
                            } else {
                                if (errorCode == "32") {
                                    resp.failCode = errorCode;
                                    resp.failMsg = errorMsg
                                } else {
                                    if (errorMsg != undefined && errorMsg != "") {
                                        resp.failCode = errorCode;
                                        resp.failMsg = errorMsg
                                    } else {
                                        resp.failCode = "001";
                                        resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒"
                                    }
                                }
                            }
                        }
                    }
                }
            }
            cart.analytics.recordErrorMsg(resp)
        }
        callerCallBack(resp)
    };
    var cartFailCallBack = function (callerCallBack) {
        var resp = {};
        resp.analyticsType = "Addcart";
        resp.result = "0";
        resp.failCode = "0000";
        resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆�";
        cart.analytics.recordErrorMsg(resp);
        callerCallBack(resp)
    };
    var addCart = function (jsonObj, callback, httpSwitch) {
        cart.toCartCallback.setData(jsonObj);
        cart.toCartCallback.setCallback(callback);
        cart.toCartCallback.setHttpSwitch(httpSwitch);
        cart.toCartCallback.setOperateType(0);
        if (typeof (callback) != "function") {
            alert("鏈紶鍏ュ弬鏁帮細鍥炶皟鍑芥暟callback锛�");
            return
        }
        var cmmdtyVOList = jsonObj.cmmdtyVOList;
        if (typeof (cmmdtyVOList) == "undefined" || cmmdtyVOList == null || cmmdtyVOList.length == 0) {
            alert("鏈紶鍏ュ弬鏁帮細鍟嗗搧淇℃伅cmmdtyVOList锛�");
            return
        }
        firstCmmdty = cmmdtyVOList[0];
        cmmdtyVOList[0].activityType = cmmdtyVOList[0].activityType || "01";
        cmmdtyVOList[0].activityId = cmmdtyVOList[0].activityId || "";
        cmmdtyVOList[0].shopCode = cmmdtyVOList[0].shopCode || "0000000000";
        var verifyCode = "";
        if (cart.security.getNeedVerifyCodeVal()) {
            var tempVerifyCode = cart.security.getVerifyCodeVal();
            var tempDefaultValue = cart.security.getDefaultValue();
            if (tempVerifyCode != undefined && tempVerifyCode != "" && tempVerifyCode != tempDefaultValue) {
                verifyCode = tempVerifyCode
            }
            cart.security.setNeedVerifyCodeVal(false)
        }
        if (typeof (bd) != "undefined") {
            cart.common.setCookie("c2dt", bd.rst())
        }
        if (typeof (jigsawObj) != "undefined" && jigsawObj != "undefined") {
            jsonObj.sillerToken = jigsawObj.queryToken()
        }
        jsonObj.verifyCode = verifyCode;
        jsonObj.uuid = cart.security.getUUID();
        jsonObj.sceneId = cart.security.getSceneId();
        jsonObj.dfpToken = dfpToken_str;
        var targetUrl = "//shopping.suning.com/addCart.do?callback=?";
        var params = {
            cartVO: cart.common.obj2string(jsonObj),
            b2c_fc_authid: b2c_fc_authid
        };
        goContineCartUrl = targetUrl & params;
        ajaxCrossDomain(targetUrl, $.param(params), function (data) {
            successCallBack("0", data, callback, "", httpSwitch)
        }, function () {
            failCallBack("0", callback)
        }, cart.common.passport_config);
        cart.analytics.savePageSaleInfo(cmmdtyVOList[0].cmmdtyCode, cmmdtyVOList[0].shopCode)
    };
    var buyNow = function (jsonObj, callback, httpSwitch) {
        cart.toCartCallback.setData(jsonObj);
        cart.toCartCallback.setCallback(callback);
        cart.toCartCallback.setHttpSwitch(httpSwitch);
        cart.toCartCallback.setOperateType(1);
        if (typeof (callback) != "function") {
            alert("鏈紶鍏ュ弬鏁帮細鍥炶皟鍑芥暟callback锛�");
            return
        }
        var cmmdtyVOList = jsonObj.cmmdtyVOList;
        if (typeof (cmmdtyVOList) == "undefined" || cmmdtyVOList == null || cmmdtyVOList.length == 0) {
            alert("鏈紶鍏ュ弬鏁帮細鍟嗗搧淇℃伅cmmdtyVOList锛�");
            return
        }
        firstCmmdty = cmmdtyVOList[0];
        cmmdtyVOList[0].activityType = cmmdtyVOList[0].activityType || "01";
        cmmdtyVOList[0].activityId = cmmdtyVOList[0].activityId || "";
        cmmdtyVOList[0].shopCode = cmmdtyVOList[0].shopCode || "0000000000";
        if (typeof (bd) != "undefined") {
            cart.common.setCookie("c2dt", bd.rst())
        }
        var verifyCode = "";
        if (cart.security.getNeedVerifyCodeVal()) {
            var tempVerifyCode = cart.security.getVerifyCodeVal();
            var tempDefaultValue = cart.security.getDefaultValue();
            if (tempVerifyCode != undefined && tempVerifyCode != "" && tempVerifyCode != tempDefaultValue) {
                verifyCode = tempVerifyCode
            } else {
                b2c_fc_authid = ""
            }
            cart.security.setNeedVerifyCodeVal(false)
        }
        jsonObj.verifyCode = verifyCode;
        jsonObj.uuid = cart.security.getUUID();
        jsonObj.sceneId = cart.security.getSceneId();
        jsonObj.dfpToken = dfpToken_str;
        if (typeof (jigsawObj) != "undefined" && jigsawObj != "undefined") {
            jsonObj.sillerToken = jigsawObj.queryToken()
        }
        var targetUrl = "//shopping.suning.com/nowBuy.do?callback=?";
        var params = {
            cartVO: cart.common.obj2string(jsonObj),
            b2c_fc_authid: b2c_fc_authid
        };

        function buy(fcTokenId) {
            params = {
                cartVO: cart.common.obj2string(jsonObj),
                b2c_fc_authid: b2c_fc_authid,
                fcTokenId: fcTokenId
            };
            $.ajax({
                url: targetUrl,
                data: $.param(params),
                crossDomain: true,
                dataType: "jsonp",
                cache: false,
                success: function (data) {
                    successCallBack("1", data, callback)
                }, error: function (e) {
                    cartFailCallBack("1", callback, e)
                }
            })
        }
        ajaxCrossDomain(targetUrl, $.param(params), function (data) {
            successCallBack("1", data, callback, buy, httpSwitch)
        }, function () {
            failCallBack("1", callback)
        }, cart.common.passport_config);
        cart.analytics.savePageSaleInfo(cmmdtyVOList[0].cmmdtyCode, cmmdtyVOList[0].shopCode);
        cart.analytics.updatePageSaleInfo()
    };
    var chooseCartTelNumber = function (shopCode, cmmdtyCode, serviceFlag) {
        if (typeof (shopCode) == "undefined" || shopCode == null || shopCode.length == 0) {
            cart.normal.alertTip("淇℃伅鎻愪氦澶辫触,璇风◢鍚庡啀璇�!");
            return
        }
        if (typeof (cmmdtyCode) == "undefined" || cmmdtyCode == null || cmmdtyCode.length == 0) {
            cart.normal.alertTip("淇℃伅鎻愪氦澶辫触,璇风◢鍚庡啀璇�!");
            return
        }
        if (typeof (serviceFlag) == "undefined" || serviceFlag == null || serviceFlag.length == 0) {
            cart.normal.alertTip("淇℃伅鎻愪氦澶辫触,璇风◢鍚庡啀璇�!");
            return
        }
        window.location.href = "//shopping.suning.com/showContractMachineInfo.do?shopCode=" + shopCode + "&cmmdtyCode=" + cmmdtyCode + "&serviceFlag=" + serviceFlag
    };
    var isEmpty = function (str) {
        if (typeof str === "undefined") {
            return true
        }
        var temp = $.trim(str);
        return (typeof temp === "undefined") || (temp === "") || (temp.length === 0)
    };
    var virtualGameBuyNow = function (jsonObj, callback, httpSwitch) {
        cart.toCartCallback.setData(jsonObj);
        cart.toCartCallback.setCallback(callback);
        cart.toCartCallback.setHttpSwitch(httpSwitch);
        cart.toCartCallback.setOperateType(2);
        if (typeof (callback) != "function") {
            alert("鏈紶鍏ュ弬鏁帮細鍥炶皟鍑芥暟callback锛�");
            return
        }
        var cmmdtyVOList = jsonObj.cmmdtyVOList;
        if (typeof (cmmdtyVOList) == "undefined" || cmmdtyVOList == null || cmmdtyVOList.length == 0) {
            alert("鏈紶鍏ュ弬鏁帮細鍟嗗搧淇℃伅cmmdtyVOList锛�");
            return
        }
        firstCmmdty = cmmdtyVOList[0];
        cmmdtyVOList[0].activityType = cmmdtyVOList[0].activityType || "01";
        cmmdtyVOList[0].activityId = cmmdtyVOList[0].activityId || "";
        cmmdtyVOList[0].shopCode = cmmdtyVOList[0].shopCode || "0000000000";
        if (typeof (bd) != "undefined") {
            cart.common.setCookie("c2dt", bd.rst())
        }
        var verifyCode = "";
        if (cart.security.getNeedVerifyCodeVal()) {
            var tempVerifyCode = cart.security.getVerifyCodeVal();
            var tempDefaultValue = cart.security.getDefaultValue();
            if (tempVerifyCode != undefined && tempVerifyCode != "" && tempVerifyCode != tempDefaultValue) {
                verifyCode = tempVerifyCode
            } else {
                b2c_fc_authid = ""
            }
            cart.security.setNeedVerifyCodeVal(false)
        }
        jsonObj.verifyCode = verifyCode;
        jsonObj.uuid = cart.security.getUUID();
        jsonObj.sceneId = cart.security.getSceneId();
        jsonObj.dfpToken = dfpToken_str;
        if (typeof (jigsawObj) != "undefined" && jigsawObj != "undefined") {
            jsonObj.sillerToken = jigsawObj.queryToken()
        }
        var targetUrl = "//shopping.suning.com/nowBuy.do?callback=?";
        var params = {
            cartVO: cart.common.obj2string(jsonObj),
            b2c_fc_authid: b2c_fc_authid
        };

        function buy(fcTokenId) {
            params = {
                cartVO: cart.common.obj2string(jsonObj),
                b2c_fc_authid: b2c_fc_authid,
                fcTokenId: fcTokenId
            };
            $.ajax({
                url: targetUrl,
                data: $.param(params),
                crossDomain: true,
                dataType: "jsonp",
                cache: false,
                success: function (data) {
                    virtualGameSuccessCallBack("1", data, callback)
                }, error: function (e) {
                    cartFailCallBack("1", callback, e)
                }
            })
        }
        ajaxCrossDomain(targetUrl, $.param(params), function (data) {
            virtualGameSuccessCallBack("1", data, callback, buy, httpSwitch)
        }, function () {
            failCallBack("1", callback)
        }, cart.common.passport_config);
        cart.analytics.savePageSaleInfo(cmmdtyVOList[0].cmmdtyCode, cmmdtyVOList[0].shopCode);
        cart.analytics.updatePageSaleInfo()
    };
    var carHouseKeeperBuyNow = function (jsonObj, callback, httpSwitch) {
        cart.toCartCallback.setData(jsonObj);
        cart.toCartCallback.setCallback(callback);
        cart.toCartCallback.setHttpSwitch(httpSwitch);
        cart.toCartCallback.setOperateType(3);
        if (typeof (callback) != "function") {
            alert("鏈紶鍏ュ弬鏁帮細鍥炶皟鍑芥暟callback锛�");
            return
        }
        var cmmdtyVOList = jsonObj.cmmdtyVOList;
        if (typeof (cmmdtyVOList) == "undefined" || cmmdtyVOList == null || cmmdtyVOList.length == 0) {
            alert("鏈紶鍏ュ弬鏁帮細鍟嗗搧淇℃伅cmmdtyVOList锛�");
            return
        }
        firstCmmdty = cmmdtyVOList[0];
        cmmdtyVOList[0].activityType = cmmdtyVOList[0].activityType || "01";
        cmmdtyVOList[0].activityId = cmmdtyVOList[0].activityId || "";
        cmmdtyVOList[0].shopCode = cmmdtyVOList[0].shopCode || "0000000000";
        if (typeof (bd) != "undefined") {
            cart.common.setCookie("c2dt", bd.rst())
        }
        var verifyCode = "";
        jsonObj.verifyCode = verifyCode;
        jsonObj.uuid = cart.security.getUUID();
        jsonObj.sceneId = cart.security.getSceneId();
        jsonObj.dfpToken = dfpToken_str;
        var targetUrl = "//shopping.suning.com/nowBuy.do?callback=?";
        var params = {
            cartVO: cart.common.obj2string(jsonObj),
            b2c_fc_authid: b2c_fc_authid
        };

        function buy(fcTokenId) {
            params = {
                cartVO: cart.common.obj2string(jsonObj),
                b2c_fc_authid: b2c_fc_authid,
                fcTokenId: fcTokenId
            };
            $.ajax({
                url: targetUrl,
                data: $.param(params),
                crossDomain: true,
                dataType: "jsonp",
                cache: false,
                success: function (data) {
                    carHouseKeeperBuyNowSuccessCallBack(data, callback)
                }, error: function (e) {
                    carHouseKeeperBuyNowfailCallBack(callback, e)
                }
            })
        }
        ajaxCrossDomain(targetUrl, $.param(params), function (data) {
            carHouseKeeperBuyNowSuccessCallBack(data, callback, buy, httpSwitch)
        }, function () {
            carHouseKeeperBuyNowfailCallBack("1", callback)
        }, cart.common.passport_config);
        cart.analytics.savePageSaleInfo(cmmdtyVOList[0].cmmdtyCode, cmmdtyVOList[0].shopCode);
        cart.analytics.updatePageSaleInfo()
    };
    var sendUomMsgV2 = function (error_type, error_code, status, type_name, error_detail) {
        try {
            var uomparam = {
                bid: "pcCart1",
                error_type: error_type,
                error_code: error_code,
                status: status,
                type_name: type_name,
                error_detail: JSON.stringify(error_detail),
                member_id: getCookie("custno"),
                member_level: getCookie("custLevel"),
                region: getCookie("SN_CITY")
            };
            sa.openAPI.sendMsgV2(uomparam)
        } catch (e) {}
    };
    var virtualGameSuccessCallBack = function (operationType, respData, callerCallBack, buy, httpSwitch) {
        var resp = {};
        resp.analyticsType = "Addcart";
        if (operationType === "1") {
            resp.analyticsType = "Buynow"
        }
        resp.result = "0";
        var returnCode = respData.returnCode;
        if (null != returnCode && "" != returnCode && "4000" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            Util.alertErrorBox(resp.failMsg);
            cart.analytics.recordErrorMsg(resp);
            callerCallBack(resp);
            return
        }
        if (null != returnCode && "" != returnCode && "4001" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            b2c_fc_authid = respData.b2c_fc_authid;
            cart.security.setNeedVerifyCodeVal(true);
            cart.security.showMinos3(respData.uuid, respData.sceneId);
            cart.analytics.recordErrorMsg(resp);
            callerCallBack(resp);
            return
        }
        if (typeof buy != "undefined" && typeof (buy) == "function") {
            if (respData.fcFlag == "1") {
                var fc_config = {
                    fcWebUrl: "//tspofc.suning.com",
                    fcResUrl: "//res.suning.cn/project/tspofc"
                };
                openB2cPopPage(respData, buy, fc_config);
                return
            }
        }
        var result = respData.isSuccess;
        var safeDps = respData.safeDps;
        var recommendServiceSwitch = respData.recommendServiceSwitch;
        if (result == "Y") {
            shoppingCartUrl = "//shopping.suning.com/virtualGameOrder.do?cart2No=" + respData.cart2No;
            resp.result = "1";
            resp.url = shoppingCartUrl;
            cart.recommended.toShoppingCart()
        } else {
            var errorCode, errorMsg, backErrorCode, ticket;
            ticket = respData.ticket;
            if (respData.addCartErrorList != undefined && respData.addCartErrorList[0] != undefined && operationType == "0") {
                errorCode = respData.addCartErrorList[0].errorCode;
                errorMsg = respData.addCartErrorList[0].errorMessage;
                backErrorCode = respData.addCartErrorList[0].backErrorCode
            } else {
                if (respData.resultErrorList != undefined && respData.resultErrorList[0] != undefined && respData.resultErrorList[0][0] != undefined && operationType == "1") {
                    errorCode = respData.resultErrorList[0][0].errorCode;
                    errorMsg = respData.resultErrorList[0][0].errorMessage;
                    backErrorCode = respData.resultErrorList[0][0].backErrorCode
                }
            } if (safeDps == "1") {
                var cmmdtyCode = firstCmmdty.cmmdtyCode;
                var shopCode = firstCmmdty.shopCode;
                cart.normal.safeDpsInit(cmmdtyCode, shopCode)
            } else {
                if (errorCode == "017") {
                    resp.failCode = errorCode;
                    resp.failMsg = "";
                    resp.uuid = respData.uuid;
                    cart.security.setNeedVerifyCodeVal(true);
                    cart.security.showMinos3(respData.uuid, respData.sceneId)
                } else {
                    if (errorCode == "118") {
                        cart.security.jigsawInit(ticket)
                    } else {
                        if (errorCode == "018") {
                            resp.failCode = errorCode;
                            resp.failMsg = "";
                            cart.security.showMinos2()
                        } else {
                            if (errorCode == "019") {
                                resp.failCode = errorCode;
                                resp.failMsg = "";
                                cart.security.showMinos1()
                            } else {
                                if (errorCode == "015" || errorCode == "025") {
                                    resp.failCode = errorCode;
                                    resp.failMsg = "";
                                    aqSuning1.showMobilePopType(false)
                                } else {
                                    if (errorCode == "024") {
                                        resp.failCode = errorCode;
                                        resp.failMsg = "鎮ㄧ櫥闄嗙殑璐﹀彿鏈夊紓甯革紝璇疯仈绯诲湪绾垮鏈嶅鐞�";
                                        Util.alertErrorBox(resp.failMsg)
                                    } else {
                                        if (errorCode == "32") {
                                            resp.failCode = errorCode;
                                            resp.failMsg = errorMsg;
                                            Util.alertErrorBox(errorMsg);
                                            location.replace(location)
                                        } else {
                                            if (errorCode == "004") {
                                                resp.failCode = errorCode;
                                                resp.failMsg = errorMsg;
                                                var html = "<div class='nostore-rd'><div class='nostore-hd clearfix'><i class='lion'></i><div class='tips'><h2>" + resp.failMsg + "</h2><a href='javascript:void(0);' class='close-nostore close'>鍏抽棴</a></div></div><div class='nostore-bd'></div></div></div>";
                                                $.mDialog({
                                                    title: "娓╅Θ鎻愮ず",
                                                    css: {
                                                        width: "448px"
                                                    },
                                                    http: function (e, o) {
                                                        e.find(".content").html(html)
                                                    }, overlayCss: {
                                                        background: "black",
                                                        opacity: "0.3"
                                                    }, overlayClick: true,
                                                    fadeIn: 300,
                                                    fadeOut: 300
                                                });
                                                var activityType = firstCmmdty.activityType;
                                                if (activityType != "04" && activityType != "05" && activityType != "06" && activityType != "12") {
                                                    var snma = getCookie("_snma");
                                                    var cookieid = "";
                                                    if (snma != null && snma != undefined) {
                                                        snma = snma.split("|");
                                                        cookieid = snma.length > 1 ? snma[1] : ""
                                                    }
                                                    var cityId = getCookie("SN_CITY").split("_")[1];
                                                    var custno = getCookie("custno");
                                                    noProductRecommend(cityId, firstCmmdty.cmmdtyCode, custno, cookieid, "004", recommendServiceSwitch)
                                                }
                                            } else {
                                                if (errorCode == "010" || errorCode == "011") {
                                                    resp.failCode = errorCode;
                                                    resp.failMsg = errorMsg;
                                                    var html = "<div class='nostore-rd'><div class='nostore-hd clearfix'><i class='lion'></i><div class='tips'><h2>" + resp.failMsg + "</h2><a href='javascript:void(0);' class='close-nostore close'>鍏抽棴</a></div></div><div class='nostore-bd'></div></div></div>";
                                                    $.mDialog({
                                                        title: "娓╅Θ鎻愮ず",
                                                        css: {
                                                            width: "448px"
                                                        },
                                                        http: function (e, o) {
                                                            e.find(".content").html(html)
                                                        }, overlayCss: {
                                                            background: "black",
                                                            opacity: "0.3"
                                                        }, overlayClick: true,
                                                        fadeIn: 300,
                                                        fadeOut: 300
                                                    });
                                                    var activityType = firstCmmdty.activityType;
                                                    if (activityType != "04" && activityType != "05" && activityType != "06" && activityType != "12") {
                                                        var snma = getCookie("_snma");
                                                        var cookieid = "";
                                                        if (snma != null && snma != undefined) {
                                                            snma = snma.split("|");
                                                            cookieid = snma.length > 1 ? snma[1] : ""
                                                        }
                                                        var cityId = getCookie("SN_CITY").split("_")[1];
                                                        var custno = getCookie("custno");
                                                        noProductRecommend(cityId, firstCmmdty.cmmdtyCode, custno, cookieid, "010", recommendServiceSwitch)
                                                    }
                                                } else {
                                                    if (errorCode == "002") {
                                                        resp.failCode = errorCode;
                                                        resp.failMsg = errorMsg;
                                                        var errorMsgTip = "鎮ㄧ殑璐墿杞﹀凡婊★紝璇锋竻鐞嗚喘鐗╄溅鍚庨噸鏂版坊鍔�";
                                                        var sb = [];
                                                        sb[sb.length] = '<div class="dialog-common" style="padding: 2px 20px 20px;">';
                                                        sb[sb.length] = '<div class="main">';
                                                        sb[sb.length] = '<p class="tips"><i class="tip-icon tip-warning-24"></i>' + errorMsgTip + "</p>";
                                                        sb[sb.length] = '<div class="dialog-action">';
                                                        sb[sb.length] = ' <a href="javascript:void(0);" class="dialog-opt dialog-close close" name="item_gmp_qx">鍙栨秷</a>';
                                                        sb[sb.length] = '<a href="//shopping.suning.com/cart.do" class="dialog-opt dialog-certain" target="_bank" name="item_gmp_qql">鍘绘竻鐞�</a>';
                                                        sb[sb.length] = "</div></div></div>";
                                                        var html = sb.join("");
                                                        $.mDialog({
                                                            title: "娓╅Θ鎻愮ず",
                                                            css: {
                                                                width: "448px"
                                                            },
                                                            http: function (e, o) {
                                                                e.find(".content").html(html)
                                                            }, overlayCss: {
                                                                background: "black",
                                                                opacity: "0.3"
                                                            }, overlayClick: true,
                                                            fadeIn: 300,
                                                            fadeOut: 300
                                                        })
                                                    } else {
                                                        if (errorMsg != undefined && errorMsg != "") {
                                                            resp.failCode = errorCode;
                                                            resp.failMsg = errorMsg;
                                                            Util.alertErrorBox(errorMsg)
                                                        } else {
                                                            resp.failCode = "001";
                                                            resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒";
                                                            Util.alertErrorBox(resp.failMsg)
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            resp.backErrorCode = backErrorCode;
            cart.analytics.recordErrorMsg(resp)
        } if (errorCode != "017" && errorCode != "117") {
            callerCallBack(resp)
        }
    };
    var carHouseKeeperBuyNowSuccessCallBack = function (respData, callerCallBack, buy, httpSwitch) {
        var resp = {};
        resp.analyticsType = "Buynow";
        resp.result = "0";
        var returnCode = respData.returnCode;
        if (null != returnCode && "" != returnCode && "4000" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            callerCallBack(resp);
            return
        }
        if (null != returnCode && "" != returnCode && "4001" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            callerCallBack(resp);
            return
        }
        var result = respData.isSuccess;
        var safeDps = respData.safeDps;
        if (result == "Y") {
            shoppingCartUrl = "//shopping.suning.com/order.do?cart2No=" + respData.cart2No;
            resp.result = "1";
            resp.url = shoppingCartUrl
        } else {
            var errorCode, errorMsg;
            if (respData.resultErrorList != undefined && respData.resultErrorList[0] != undefined && respData.resultErrorList[0][0] != undefined) {
                errorCode = respData.resultErrorList[0][0].errorCode;
                errorMsg = respData.resultErrorList[0][0].errorMessage
            }
            if (safeDps == "1") {
                resp.failCode = safeDps
            } else {
                if (errorCode == "019") {
                    resp.failCode = errorCode;
                    resp.failMsg = "浜诧紝寰堟姳姝夛紝鎮ㄨ喘涔扮殑瀹濊礉閿€鍞紓甯哥伀鐖嗚灏忚嫃鎺墜涓嶅強锛岃绋嶅悗鍐嶈瘯~"
                } else {
                    if (errorCode == "024") {
                        resp.failCode = errorCode;
                        resp.failMsg = "鎮ㄧ櫥闄嗙殑璐﹀彿鏈夊紓甯革紝璇疯仈绯诲湪绾垮鏈嶅鐞�"
                    } else {
                        if (errorMsg != undefined && errorMsg != "") {
                            resp.failCode = errorCode;
                            resp.failMsg = errorMsg
                        } else {
                            resp.failCode = "001";
                            resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒"
                        }
                    }
                }
            }
        }
        callerCallBack(resp)
    };
    var successCallBack = function (operationType, respData, callerCallBack, buy, httpSwitch) {
        var resp = {};
        resp.analyticsType = "Addcart";
        if (operationType === "1") {
            resp.analyticsType = "Buynow"
        }
        resp.result = "0";
        var returnCode = respData.returnCode;
        if (null != returnCode && "" != returnCode && "4000" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            Util.alertErrorBox(resp.failMsg);
            cart.analytics.recordErrorMsg(resp);
            callerCallBack(resp);
            if (operationType === "0") {
                sendUomMsgV2("2", "ccf-gwc1-20000_CCF_SYS_9999", "0", "addcart", respData)
            } else {
                sendUomMsgV2("2", "ccf-gwc1-20003_CCF_SYS_9999", "0", "buynow", respData)
            }
            return
        }
        if (null != returnCode && "" != returnCode && "4001" == returnCode) {
            resp.failCode = returnCode;
            if (typeof (respData.fcType) != "undefined" && respData.fcType != null && respData.fcType != "") {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L945" + respData.fcType + ")"
            } else {
                resp.failMsg = "鍟嗗搧閿€鍞伀鐖嗭紝璇风◢鍚庡啀璇�(L946)"
            }
            b2c_fc_authid = respData.b2c_fc_authid;
            cart.security.setNeedVerifyCodeVal(true);
            cart.security.showMinos3(respData.uuid, respData.sceneId);
            cart.analytics.recordErrorMsg(resp);
            callerCallBack(resp);
            if (operationType === "0") {
                sendUomMsgV2("2", "ccf-gwc1-20000_SYS_FC", "0", "addcart", respData)
            } else {
                sendUomMsgV2("2", "ccf-gwc1-20003_CCF_SYS_9999", "0", "buynow", respData)
            }
            return
        }
        if (typeof buy != "undefined" && typeof (buy) == "function") {
            if (respData.fcFlag == "1") {
                var fc_config = {
                    fcWebUrl: "//tspofc.suning.com",
                    fcResUrl: "//res.suning.cn/project/tspofc"
                };
                openB2cPopPage(respData, buy, fc_config);
                return
            }
        }
        var result = respData.isSuccess;
        var safeDps = respData.safeDps;
        var recommendServiceSwitch = respData.recommendServiceSwitch;
        if (result == "Y") {
            var param = {
                pid: firstCmmdty.cmmdtyCode,
                vid: firstCmmdty.shopCode,
                storeId: sn.storeId,
                catalogId: sn.catalogId,
                langId: "-7",
                cartFlag: "B"
            };
            if (operationType != "1") {
                resp.result = "1";
                var toCartUrl = "//shopping.suning.com/cart.do";
                if (httpSwitch == "1") {
                    toCartUrl = "${ccfNewDomain}/cart.do"
                }
                var html = "<div class='nostore-rd'> <div class='add-cart-hd clearfix'><i class='tip-succ'></i><span>宸叉垚鍔熷姞鍏ヨ喘鐗╄溅锛�</span><a href=" + toCartUrl + " class='go-cart' name='cart1_go'>鍘昏喘鐗╄溅缁撶畻<i>></i></a></div><div class='nostore-bd'></div></div>";
                $.mDialog({
                    title: "娓╅Θ鎻愮ず",
                    css: {
                        width: "448px"
                    },
                    http: function (e, o) {
                        e.find(".content").html(html)
                    }, overlayCss: {
                        background: "black",
                        opacity: "0.3"
                    }, fadeIn: 300,
                    fadeOut: 300
                });
                if (!cart.common.isEmpty(recommendServiceSwitch) && recommendServiceSwitch == "1") {
                    var activityType = firstCmmdty.activityType;
                    var partnumber;
                    var cityId = getCookie("SN_CITY").split("_")[1];
                    var custno = getCookie("custno");
                    if (activityType != "04" && activityType != "05" && activityType != "12" && activityType != "06") {
                        partnumber = firstCmmdty.cmmdtyCode;
                        addCartRecommendBuy(cityId, partnumber)
                    } else {
                        partnumber = "";
                        addCartRecommend(cityId, partnumber, custno)
                    }
                }
            } else {
                shoppingCartUrl = "//shopping.suning.com/order.do?cart2No=" + respData.cart2No;
                resp.result = "1";
                resp.url = shoppingCartUrl;
                cart.recommended.toShoppingCart()
            }
        } else {
            var errorCode, errorMsg, backErrorCode, ticket, uomErrorCode;
            ticket = respData.ticket;
            if (respData.addCartErrorList != undefined && respData.addCartErrorList[0] != undefined && operationType == "0") {
                errorCode = respData.addCartErrorList[0].errorCode;
                errorMsg = respData.addCartErrorList[0].errorMessage;
                backErrorCode = respData.addCartErrorList[0].backErrorCode;
                uomErrorCode = respData.addCartErrorList[0].uomErrorCode;
                if (isEmpty(uomErrorCode)) {
                    uomErrorCode = "ccf-gwc1-20000_undefined"
                }
            } else {
                if (respData.resultErrorList != undefined && respData.resultErrorList[0] != undefined && respData.resultErrorList[0][0] != undefined && operationType == "1") {
                    errorCode = respData.resultErrorList[0][0].errorCode;
                    errorMsg = respData.resultErrorList[0][0].errorMessage;
                    backErrorCode = respData.resultErrorList[0][0].backErrorCode;
                    uomErrorCode = respData.resultErrorList[0][0].uomErrorCode;
                    if (isEmpty(uomErrorCode)) {
                        uomErrorCode = "ccf-gwc1-20003_undefined"
                    }
                }
            } if (safeDps == "1") {
                var cmmdtyCode = firstCmmdty.cmmdtyCode;
                var shopCode = firstCmmdty.shopCode;
                cart.normal.safeDpsInit(cmmdtyCode, shopCode)
            } else {
                if (errorCode == "017") {
                    resp.failCode = errorCode;
                    resp.failMsg = "";
                    resp.uuid = respData.uuid;
                    cart.security.setNeedVerifyCodeVal(true);
                    cart.security.showMinos3(respData.uuid, respData.sceneId)
                } else {
                    if (errorCode == "118") {
                        cart.security.jigsawInit(ticket)
                    } else {
                        if (errorCode == "018") {
                            resp.failCode = errorCode;
                            resp.failMsg = "";
                            cart.security.showMinos2()
                        } else {
                            if (errorCode == "019") {
                                resp.failCode = errorCode;
                                resp.failMsg = "";
                                cart.security.showMinos1()
                            } else {
                                if (errorCode == "015" || errorCode == "025") {
                                    resp.failCode = errorCode;
                                    resp.failMsg = "";
                                    aqSuning1.showMobilePopType(false)
                                } else {
                                    if (errorCode == "024") {
                                        resp.failCode = errorCode;
                                        resp.failMsg = "鎮ㄧ櫥闄嗙殑璐﹀彿鏈夊紓甯革紝璇疯仈绯诲湪绾垮鏈嶅鐞�";
                                        Util.alertErrorBox(resp.failMsg)
                                    } else {
                                        if (errorCode == "32") {
                                            resp.failCode = errorCode;
                                            resp.failMsg = errorMsg;
                                            Util.alertErrorBox(errorMsg);
                                            location.replace(location)
                                        } else {
                                            if (errorCode == "004") {
                                                resp.failCode = errorCode;
                                                resp.failMsg = errorMsg;
                                                var html = "<div class='nostore-rd'><div class='nostore-hd clearfix'><i class='lion'></i><div class='tips'><h2>" + resp.failMsg + "</h2><a href='javascript:void(0);' class='close-nostore close'>鍏抽棴</a></div></div><div class='nostore-bd'></div></div></div>";
                                                $.mDialog({
                                                    title: "娓╅Θ鎻愮ず",
                                                    css: {
                                                        width: "448px"
                                                    },
                                                    http: function (e, o) {
                                                        e.find(".content").html(html)
                                                    }, overlayCss: {
                                                        background: "black",
                                                        opacity: "0.3"
                                                    }, overlayClick: true,
                                                    fadeIn: 300,
                                                    fadeOut: 300
                                                });
                                                var activityType = firstCmmdty.activityType;
                                                if (activityType != "04" && activityType != "05" && activityType != "06" && activityType != "12") {
                                                    var snma = getCookie("_snma");
                                                    var cookieid = "";
                                                    if (snma != null && snma != undefined) {
                                                        snma = snma.split("|");
                                                        cookieid = snma.length > 1 ? snma[1] : ""
                                                    }
                                                    var cityId = getCookie("SN_CITY").split("_")[1];
                                                    var custno = getCookie("custno");
                                                    noProductRecommend(cityId, firstCmmdty.cmmdtyCode, custno, cookieid, "004", recommendServiceSwitch)
                                                }
                                            } else {
                                                if (errorCode == "010" || errorCode == "011") {
                                                    resp.failCode = errorCode;
                                                    resp.failMsg = errorMsg;
                                                    var html = "<div class='nostore-rd'><div class='nostore-hd clearfix'><i class='lion'></i><div class='tips'><h2>" + resp.failMsg + "</h2><a href='javascript:void(0);' class='close-nostore close'>鍏抽棴</a></div></div><div class='nostore-bd'></div></div></div>";
                                                    $.mDialog({
                                                        title: "娓╅Θ鎻愮ず",
                                                        css: {
                                                            width: "448px"
                                                        },
                                                        http: function (e, o) {
                                                            e.find(".content").html(html)
                                                        }, overlayCss: {
                                                            background: "black",
                                                            opacity: "0.3"
                                                        }, overlayClick: true,
                                                        fadeIn: 300,
                                                        fadeOut: 300
                                                    });
                                                    var activityType = firstCmmdty.activityType;
                                                    if (activityType != "04" && activityType != "05" && activityType != "06" && activityType != "12") {
                                                        var snma = getCookie("_snma");
                                                        var cookieid = "";
                                                        if (snma != null && snma != undefined) {
                                                            snma = snma.split("|");
                                                            cookieid = snma.length > 1 ? snma[1] : ""
                                                        }
                                                        var cityId = getCookie("SN_CITY").split("_")[1];
                                                        var custno = getCookie("custno");
                                                        noProductRecommend(cityId, firstCmmdty.cmmdtyCode, custno, cookieid, "010", recommendServiceSwitch)
                                                    }
                                                } else {
                                                    if (errorCode == "002") {
                                                        resp.failCode = errorCode;
                                                        resp.failMsg = errorMsg;
                                                        var errorMsgTip = "鎮ㄧ殑璐墿杞﹀凡婊★紝璇锋竻鐞嗚喘鐗╄溅鍚庨噸鏂版坊鍔�";
                                                        var sb = [];
                                                        sb[sb.length] = '<div class="dialog-common" style="padding: 2px 20px 20px;">';
                                                        sb[sb.length] = '<div class="main">';
                                                        sb[sb.length] = '<p class="tips"><i class="tip-icon tip-warning-24"></i>' + errorMsgTip + "</p>";
                                                        sb[sb.length] = '<div class="dialog-action">';
                                                        sb[sb.length] = ' <a href="javascript:void(0);" class="dialog-opt dialog-close close" name="item_gmp_qx">鍙栨秷</a>';
                                                        sb[sb.length] = '<a href="//shopping.suning.com/cart.do" class="dialog-opt dialog-certain" target="_bank" name="item_gmp_qql">鍘绘竻鐞�</a>';
                                                        sb[sb.length] = "</div></div></div>";
                                                        var html = sb.join("");
                                                        $.mDialog({
                                                            title: "娓╅Θ鎻愮ず",
                                                            css: {
                                                                width: "448px"
                                                            },
                                                            http: function (e, o) {
                                                                e.find(".content").html(html)
                                                            }, overlayCss: {
                                                                background: "black",
                                                                opacity: "0.3"
                                                            }, overlayClick: true,
                                                            fadeIn: 300,
                                                            fadeOut: 300
                                                        })
                                                    } else {
                                                        if (errorMsg != undefined && errorMsg != "") {
                                                            resp.failCode = errorCode;
                                                            resp.failMsg = errorMsg;
                                                            Util.alertErrorBox(errorMsg)
                                                        } else {
                                                            resp.failCode = "001";
                                                            resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒";
                                                            Util.alertErrorBox(resp.failMsg)
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            resp.backErrorCode = backErrorCode;
            cart.analytics.recordErrorMsg(resp);
            if (operationType === "0") {
                sendUomMsgV2("2", uomErrorCode, "0", "addcart", respData)
            } else {
                sendUomMsgV2("2", uomErrorCode, "0", "buynow", respData)
            }
        } if (errorCode != "017" && errorCode != "117" && errorCode != "118") {
            callerCallBack(resp)
        }
    };
    var noProductRecommend = function (cityId, parameter, custno, cookieid, errorType, recommendServiceSwitch) {
        if (cart.common.isEmpty(recommendServiceSwitch) || recommendServiceSwitch != "1") {
            return
        }
        $.ajax({
            url: "//tuijian.suning.com/recommend-portal/recommendv2/biz.jsonp",
            data: {
                u: custno,
                c: cookieid,
                parameter: parameter,
                cityId: cityId,
                sceneIds: "10-52",
                count: 12
            },
            cache: true,
            async: false,
            dataType: "jsonp",
            success: function (response) {
                if (null != response && typeof response.sugGoods != "undefined" && response.sugGoods.length > 0 && typeof response.sugGoods[0].skus != "undefined" && response.sugGoods[0].skus.length >= 1) {
                    var productDomain = "//product.suning.com";
                    var imgUrlBase = sn.newImageDomianDir + "/uimg/b2c/newcatentries/";
                    var prodList = response.sugGoods[0].skus;
                    var len = prodList.length;
                    var html = "<h2>鎺ㄨ崘浣犵湅鐪�</h2><div sap-modid='c8RYT' class='nostore-rd-box nostore-rd-box-listloop'>";
                    if (len > 3) {
                        html = html + "<a href='javascript:void(0);' class='rd-btn prev'></a><a href='javascript:void(0);' class='rd-btn next'></a>"
                    }
                    html = html + "<span class='rd-text-page'><em class='rd-cur-count'>1</em>/<em class='rd-total-count'></em></span><div class='nostore-rd-list'> <ul></ul></div>";
                    $(".nostore-bd").html(html);
                    var a = 0,
                        b = 0;
                    var liList = "";
                    for (var i = 0; i < len; i++) {
                        var prod = prodList[i];
                        var shopKey = prod.vendorId;
                        var longPartNumber = prod.sugGoodsCode;
                        if (prod.promotionType == "6") {
                            shopKey = "mp"
                        }
                        a = i % 5 == 0 ? a + 1 : a;
                        b = i % 5 + 1;
                        var shortPartnumber = cart.common.dealPreZeroPartnum(longPartNumber);
                        var prodUrl = productDomain + "/" + shopKey + "/" + shortPartnumber + ".html";
                        var imgUrl = imgUrlBase + prod.vendorId + "-" + longPartNumber + "_1_160x160.jpg";
                        var baoguang = "baoguang_recswh_" + a + "-" + b + "_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianP = "item_" + parameter + "_recswh_" + a + "-" + b + "_p_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianC = "item_" + parameter + "_recswh_" + a + "-" + b + "_c_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianB = "item_" + parameter + "_recswh_" + a + "-" + b + "_b_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var baoguangn = "baoguang_recswhn_" + a + "-" + b + "_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianPn = "item_" + parameter + "_recswhn_" + a + "-" + b + "_p_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianCn = "item_" + parameter + "_recswhn_" + a + "-" + b + "_c_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianBn = "item_" + parameter + "_recswhn_" + a + "-" + b + "_b_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var id4TagLi = prod.vendorId + "_" + shortPartnumber;
                        if (errorType == "004") {
                            liList += getProdHtml(prod, id4TagLi, prodUrl, imgUrl, prod.vendorId, longPartNumber, cityId, prod.promotionType, prod.promotionId, baoguang, maidianP, maidianC, maidianB, "1", "")
                        } else {
                            liList += getProdHtml(prod, id4TagLi, prodUrl, imgUrl, prod.vendorId, longPartNumber, cityId, prod.promotionType, prod.promotionId, baoguangn, maidianPn, maidianCn, maidianBn, "1", "")
                        }
                    }
                    $(".nostore-rd-list").find("ul").html(liList);
                    nostoreRd.listloop({
                        wrap: ".nostore-rd-box",
                        loopBox: ".nostore-rd-list ul",
                        step: {
                            wide: 3,
                            narrow: 3
                        },
                        scrollWidth: {
                            wide: 354,
                            narrow: 354
                        },
                        hasLabel: false,
                        isRandom: false,
                        curCount: ".rd-cur-count",
                        totalCount: ".rd-total-count"
                    });
                    try {
                        cart.analytics.runAnalyseExpo()
                    } catch (e) {}
                } else {
                    $(".nostore-bd").html("")
                }
            }, error: function () {}
        })
    };

    function getProdHtml(prod, id4TagLi, prodUrl, imgUrl, vendorId, partNumber, cityId, promotionType, promotionId, baoguang, maidianP, maidianC, maidianB, needAddCart, salesVolume) {
        var saPrd = '{"eletp":"prd","prdid":"' + partNumber + '","shopid":"' + vendorId + '","supid":"' + prod.supplierCode + '","recvalue":"' + prod.handwork + '"}';
        var saAdd = '{"eletp":"addtocart","prdid":"' + partNumber + '","shopid":"' + vendorId + '","recvalue":"' + prod.handwork + '"}';
        var html = "";
        html += "<li id='" + id4TagLi + "'>";
        var picClickFourthPageUrl = prodUrl + "?src=" + maidianP;
        var nameClickFourthPageUrl = prodUrl + "?src=" + maidianC;
        var adLabelShowFlag = "0";
        if (!cart.common.isEmpty(prod.sugType) && prod.sugType == "3") {
            adLabelShowFlag = "1";
            if (!cart.common.isEmpty(prod.apsClickUrl)) {
                picClickFourthPageUrl = prod.apsClickUrl;
                nameClickFourthPageUrl = prod.apsClickUrl
            }
        }
        html += "<div class='rd-pic'><a sa-data='" + saPrd + "' href='" + picClickFourthPageUrl + "' name='" + maidianP + "' target='_blank' sugType='" + prod.sugType + "'>";
        if (typeof prod.pictureUrl != "undefined" && prod.pictureUrl != "") {
            html += "<img src='" + prod.pictureUrl + "_160w_160h_4e' alt='" + prod.sugGoodsName + "'/>"
        } else {
            html += "<img src='" + imgUrl + "' alt='" + prod.sugGoodsName + "'/>"
        } if (adLabelShowFlag == "1") {
            html += '<span class="add-cart-ad">骞垮憡</span>'
        }
        html += "</a></div>";
        html += "<p class='rd-name'>" + getPromotionTip(prod.promotionInfo) + "<a sa-data='" + saPrd + "' href='" + nameClickFourthPageUrl + "' title='" + prod.sugGoodsName + "' id='" + baoguang + "' name='" + maidianC + "' target='_blank'>" + prod.sugGoodsName + "</a></p>";
        html += "<p class='sn-price'><i>&yen;</i><strong>" + prod.price + "</strong></p>";
        if (typeof needAddCart != "undefined" && needAddCart === "0") {
            if (typeof salesVolume != "undefined" && salesVolume != "") {
                html += "<p class='buy-num'><em>" + salesVolume + "</em>浜哄凡璐拱</p>"
            }
        } else {
            html += "<a sa-data='" + saAdd + "' href='javascript:void(0);' class='add-cart' buyNum='1' vendorId='" + vendorId + "' partNumber='" + partNumber + "' cityId='" + cityId + "' promotionType='" + promotionType + "' promotionId='" + promotionId + "' name='" + maidianB + "'></a>"
        }
        html += "</li>";
        return html
    }
    var addCartRecommend = function (cityId, parameter, custno) {
        $.ajax({
            url: "//tuijian.suning.com/recommend-portal/recommend/paramsBiz.jsonp",
            data: {
                u: custno,
                parameters: parameter,
                cityId: cityId,
                sceneIds: "10-23",
                count: 9,
                flag: ""
            },
            cache: true,
            async: false,
            dataType: "jsonp",
            success: function (response) {
                if (null != response && typeof response.sugGoods != "undefined" && response.sugGoods.length > 0 && typeof response.sugGoods[0].skus != "undefined" && response.sugGoods[0].skus.length >= 3) {
                    var productDomain = "//product.suning.com";
                    var imgUrlBase = sn.newImageDomianDir + "/uimg/b2c/newcatentries/";
                    var prodList = response.sugGoods[0].skus;
                    var len = prodList.length;
                    var html = "<h2>涓烘偍鎺ㄨ崘</h2><div sap-modid='MjRc' class='nostore-rd-box add-cart-listloop'>";
                    if (len > 3) {
                        html = html + "<a href='javascript:void(0);' class='rd-btn prev'></a><a href='javascript:void(0);' class='rd-btn next'></a>"
                    }
                    html = html + "<span class='rd-text-page'><em class='rd-cur-count'>1</em>/<em class='rd-total-count'></em></span><div class='nostore-rd-list'> <ul></ul></div>";
                    $(".nostore-bd").html(html);
                    var a = 0,
                        b = 0;
                    var liList = "";
                    for (var i = 0; i < len; i++) {
                        var prod = prodList[i];
                        var shopKey = prod.vendorId;
                        var longPartNumber = prod.sugGoodsCode;
                        if (prod.promotionType == "6") {
                            shopKey = "mp"
                        }
                        a = i % 3 == 0 ? a + 1 : a;
                        b = i % 3 + 1;
                        var shortPartnumber = cart.common.dealPreZeroPartnum(longPartNumber);
                        var prodUrl = productDomain + "/" + shopKey + "/" + shortPartnumber + ".html";
                        var imgUrl = imgUrlBase + prod.vendorId + "-" + longPartNumber + "_1_100x100.jpg";
                        var baoguang = "baoguang_rectcnxh_" + a + "-" + b + "_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianP = "cartc_" + parameter + "_rectcnxh_" + a + "-" + b + "_p_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianC = "cartc_" + parameter + "_rectcnxh_" + a + "-" + b + "_c_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var maidianB = "cartc_" + parameter + "_rectcnxh_" + a + "-" + b + "_b_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                        var salesVolume = prod.salesVolume;
                        var id4TagLi = prod.vendorId + "_" + shortPartnumber;
                        liList += getProdHtml(prod, id4TagLi, prodUrl, imgUrl, prod.vendorId, longPartNumber, cityId, prod.promotionType, prod.promotionId, baoguang, maidianP, maidianC, maidianB, "0", salesVolume)
                    }
                    $(".nostore-rd-list").find("ul").html(liList);
                    $(".nostore-rd").removeClass("add-no-list");
                    nostoreRd.listloop({
                        wrap: ".nostore-rd-box",
                        loopBox: ".nostore-rd-list ul",
                        step: {
                            wide: 3,
                            narrow: 3
                        },
                        scrollWidth: {
                            wide: 354,
                            narrow: 354
                        },
                        hasLabel: false,
                        isRandom: false,
                        curCount: ".rd-cur-count",
                        totalCount: ".rd-total-count"
                    });
                    try {
                        cart.analytics.runAnalyseExpo()
                    } catch (e) {}
                } else {
                    $(".nostore-bd").html("");
                    $(".nostore-rd").addClass("add-no-list")
                }
            }, error: function () {}
        })
    };
    var addCartRecommendBuy = function (cityId, parameter) {
        var vendorId = firstCmmdty.shopCode;
        var urlB = "//dsms.suning.com/dsms/getAddCartGoodsData.do?parameter=" + parameter + "&vendorId=" + vendorId + "&cityId=" + cityId + "&sceneIds=10-30&count=15&terminal=pc";
        $.ajax({
            url: urlB,
            cache: true,
            dataType: "jsonp",
            success: function (data) {
                cart.normal.recommendBuyCallBack(data)
            }
        })
    };
    var recommendBuyCallBack = function (response) {
        if (null != response && typeof response.sugGoods != "undefined" && response.sugGoods.length > 0 && typeof response.sugGoods[0].skus != "undefined" && response.sugGoods[0].skus.length >= 3) {
            var productDomain = "//product.suning.com";
            var imgUrlBase = sn.newImageDomianDir + "/uimg/b2c/newcatentries/";
            var parameter = response.sugGoods[0].parameter;
            var cityId = getCookie("SN_CITY").split("_")[1];
            var prodList = response.sugGoods[0].skus;
            var len = prodList.length;
            var html = "<h2>涓烘偍鎺ㄨ崘</h2><div sap-modid='MjRc' class='nostore-rd-box add-cart-listloop'>";
            if (len > 3) {
                html = html + "<a href='javascript:void(0);' class='rd-btn prev'></a><a href='javascript:void(0);' class='rd-btn next'></a>"
            }
            html = html + "<span class='rd-text-page'><em class='rd-cur-count'>1</em>/<em class='rd-total-count'></em></span><div class='nostore-rd-list'> <ul></ul></div>";
            $(".nostore-bd").html(html);
            var a = 0,
                b = 0;
            var liList = "";
            for (var i = 0; i < len; i++) {
                var prod = prodList[i];
                var shopKey = prod.vendorId;
                var longPartNumber = prod.sugGoodsCode;
                if (prod.promotionType == "6") {
                    shopKey = "mp"
                }
                a = i % 3 == 0 ? a + 1 : a;
                b = i % 3 + 1;
                var shortPartnumber = cart.common.dealPreZeroPartnum(longPartNumber);
                var prodUrl = productDomain + "/" + shopKey + "/" + shortPartnumber + ".html";
                var imgUrl = imgUrlBase + prod.vendorId + "-" + longPartNumber + "_1_100x100.jpg";
                var baoguang = "baoguang_rectcnxh_" + a + "-" + b + "_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                var maidianP = "cartc_" + parameter + "_rectcnxh_" + a + "-" + b + "_p_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                var maidianC = "cartc_" + parameter + "_rectcnxh_" + a + "-" + b + "_c_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                var maidianB = "cartc_" + parameter + "_rectcnxh_" + a + "-" + b + "_b_" + prod.vendorId + "_" + shortPartnumber + "_" + prod.handwork;
                var salesVolume = prod.salesVolume;
                var id4TagLi = prod.vendorId + "_" + shortPartnumber;
                liList += getProdHtml(prod, id4TagLi, prodUrl, imgUrl, prod.vendorId, longPartNumber, cityId, prod.promotionType, prod.promotionId, baoguang, maidianP, maidianC, maidianB, "0", salesVolume)
            }
            $(".nostore-rd-list").find("ul").html(liList);
            $(".nostore-rd").removeClass("add-no-list");
            nostoreRd.listloop({
                wrap: ".nostore-rd-box",
                loopBox: ".nostore-rd-list ul",
                step: {
                    wide: 3,
                    narrow: 3
                },
                scrollWidth: {
                    wide: 354,
                    narrow: 354
                },
                hasLabel: false,
                isRandom: false,
                curCount: ".rd-cur-count",
                totalCount: ".rd-total-count"
            });
            try {
                cart.analytics.runAnalyseExpo();
                $(".nostore-rd-list .rd-pic a").each(function () {
                    if (!cart.common.isEmpty($(this).attr("sugType")) && $(this).attr("sugType") == 3) {
                        SAUP.sendLogData("expoManual", this)
                    }
                })
            } catch (e) {}
        } else {
            $(".nostore-bd").html("");
            $(".nostore-rd").addClass("add-no-list");
            sendUomMsgV2("2", "ccf-gwc1-2tjjgtj01", "1", "getAddCartGoodsData", response)
        }
    };

    function getPromotionTip(type) {
        var html = "";
        if (cart.common.isEmpty(type)) {
            return html
        }
        html += "<span class='ju'>";
        html += type;
        html += "</span>";
        return html
    }
    var failCallBack = function (operationType, callerCallBack) {
        var resp = {};
        resp.analyticsType = "Addcart";
        if (operationType === "1") {
            resp.analyticsType = "Buynow"
        }
        resp.result = "0";
        resp.failCode = "0000";
        resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒";
        Util.alertErrorBox(resp.failMsg);
        cart.analytics.recordErrorMsg(resp);
        callerCallBack(resp)
    };
    var carHouseKeeperBuyNowfailCallBack = function (callerCallBack) {
        var resp = {};
        resp.analyticsType = "Buynow";
        resp.result = "0";
        resp.failCode = "0000";
        resp.failMsg = "缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒";
        cart.analytics.recordErrorMsg(resp);
        callerCallBack(resp)
    };

    function add2Cart(sellType, buyNum, vendorCode, catEntryIds, warrentProducts, cityId, isPreBuy, partnumber, priceType, PriceShowActionId) {
        commPartnumber = partnumber;
        if (isPreBuy != 1) {
            cartPress(true)
        }
        alsoBuy(cityId);
        var _url = "http://" + sn.cartPath + "/addMiniSoppingCart";
        var add2ShopCartData = {
            ERROEVIEW: "miniShoppingCartView",
            URL: "miniShoppingCartView",
            quantity: buyNum,
            fullInventoryCheck: "0",
            inventoryCheckType: "0",
            fullVoucherCheck: "0",
            voucherCheckType: "0",
            inventoryRemoteCheck: "0",
            voucherRemoteCheck: "1",
            storeId: "10052",
            catalogId: "10051",
            orderId: ".",
            partnumber: partnumber,
            sellType: sellType,
            supplierCode: vendorCode,
            priceType: priceType,
            promotionActiveId: PriceShowActionId
        };
        if (sellType != "0") {
            _url = "SNTreatyProductAddCartCmd"
        }
        var warrentProduct = new Array();
        var tempWarrentProduct = "";
        if (null != warrentProducts && "" != warrentProducts) {
            var warrentProductsArray = warrentProducts.split(",");
            for (var i = 0, len = warrentProductsArray.length; i < len; i++) {
                var warProduct = warrentProductsArray[i].split("-");
                if (warProduct.length > 1) {
                    warrentProduct[i] = warProduct[0]
                } else {
                    warrentProduct[i] = warProduct
                } if (i == (len - 1)) {
                    tempWarrentProduct = tempWarrentProduct + warrentProduct[i]
                } else {
                    tempWarrentProduct = tempWarrentProduct + warrentProduct[i] + ","
                }
            }
        }
        var buyPackPartNumber = "";
        var buyPackQuantity = "";
        var buyPackSort = "";
        if (warrentProduct.length > buyNum) {
            Util.alertErrorBox("寤朵繚鍟嗗搧鏁伴噺蹇呴』灏忎簬绛変簬鍟嗗搧鏁伴噺!");
            if (isPreBuy != 1) {
                cartPress(false)
            }
            return
        } else {
            for (i = 0; i < warrentProduct.length; i++) {
                if (buyPackPartNumber != "") {
                    buyPackPartNumber = buyPackPartNumber + "," + warrentProduct[i];
                    buyPackQuantity = buyPackQuantity + ",1"
                } else {
                    buyPackPartNumber = warrentProduct[i];
                    buyPackQuantity = "1";
                    buyPackSort = 1
                }
            }
        } if (null != buyPackSort && buyPackSort != "") {
            add2ShopCartData.buyPackSort = buyPackSort
        }
        if (null != tempWarrentProduct && tempWarrentProduct != "") {
            add2ShopCartData.buyPackPartNumber_1 = tempWarrentProduct
        }
        if (null != buyPackQuantity && buyPackQuantity != "") {
            add2ShopCartData.buyPackQuantity_1 = buyPackQuantity
        }
        if (null != catEntryIds && "" != catEntryIds) {
            var catentryId = catEntryIds.split(",");
            if (catentryId[0] != null) {
                add2ShopCartData.catEntryId_2 = catentryId[0]
            }
            if (catentryId[1] != null) {
                add2ShopCartData.catEntryId_3 = catentryId[1]
            }
        }
        if (isPreBuy == 1) {
            add2ShopCartData.promotionType = "psell";
            if (typeof (bd) != "undefined") {
                cart.common.setCookie("c2dt", bd.rst())
            }
            if (needVerifyCodeVal) {
                var tempVerifyCode = verifyCodeVal;
                if (tempVerifyCode != undefined && tempVerifyCode != "" && tempVerifyCode != "浠ヤ笅瀛楃涓嶅尯鍒嗗ぇ灏忓啓") {
                    add2ShopCartData.verifyCode = tempVerifyCode;
                    add2ShopCartData.uuid = v_uuid
                }
                needVerifyCodeVal = false
            }
        }
        if (cloudInfo.addCartState == "1") {
            add2ShopCartData.promotionType = "cloud";
            add2ShopCartData.promotionActId = cloudInfo.activityID
        }
        $.ajax({
            url: _url,
            data: add2ShopCartData,
            cache: false,
            async: false,
            dataType: "jsonp",
            jsonp: "callback",
            success: function (response) {
                if (response.userStatus != "") {
                    Util.alertErrorBox("鎮ㄧ殑浼氬憳鍗″凡鍐荤粨锛岃鎷ㄦ墦4008-198-198鎴栧湪绾垮鏈嶅鐞嗐€�")
                } else {
                    var fourthURL = window.location.href;
                    if (response.errorCode == "MINOSE_0001") {
                        quickPress(false);
                        showMinos1()
                    } else {
                        if (response.errorCode == "MINOSE_0002") {
                            quickPress(false);
                            showMinos2()
                        } else {
                            if (response.errorCode == "MINOSE_0003") {
                                needVerifyCodeVal = true;
                                quickPress(false);
                                showMinos3(response.uuid, response.sceneId)
                            } else {
                                if (response.errorCode == "pne") {
                                    Util.alertErrorBox("璇ヤ紭鎯犱环搴撳瓨涓嶈冻锛岃淇敼鏁伴噺锛�")
                                } else {
                                    if (response.errorCode == "BLACKLISTERROR") {
                                        Util.alertErrorBox("鎶辨瓑锛屾偍鏆傛棤璧勬牸璐拱澶ц仛鎯犲晢鍝侊紝璇烽€夋嫨鍏朵粬鍟嗗搧璐拱銆�");
                                        quickPress(false)
                                    } else {
                                        if (response.errorCode == "GROUPTIMEOUT" || response.errorCode == "GROUPNUMOUT" || response.errorCode == "GROUPSIMPLENUMOUT" || response.errorCode == "GROUPPARAMERROR" || response.errorCode == "GROUPINPREHEAT" || response.errorCode == "GROUPHAVINGCHANCE") {
                                            Util.alertErrorBox(response.errorMessage);
                                            quickPress(false)
                                        } else {
                                            if (response.errorCode == "GROUPNOTBINDPHONE") {
                                                aqSuning1.showMobilePopType(false);
                                                quickPress(false)
                                            } else {
                                                if (response.errorCode == "GROUPUSERINFOERR") {
                                                    Util.alertErrorBox("鎮ㄧ櫥闄嗙殑璐﹀彿鏈夊紓甯革紝璇疯仈绯诲湪绾垮鏈嶅鐞�");
                                                    quickPress(false)
                                                } else {
                                                    if (response.errorCode == "GROUPNOTBRONDPAY") {
                                                        Util.alertErrorBox("鎮ㄩ渶瑕佽繘琛�<a href='" + getBrondPayUrl() + "'>鏄撲粯瀹濆揩鎹风粦瀹�</a>鍚庢墠鍙互缁х画璐拱鍝");
                                                        quickPress(false)
                                                    } else {
                                                        if (response.errorCode == "SCODE_NOT_ENOUGH" || response.errorCode == "SCODE_SYS_ERR") {
                                                            Util.alertErrorBox(response.errorMessage);
                                                            quickPress(false)
                                                        } else {
                                                            if (response.errorCode == "SCODE_NOT_BIND") {
                                                                Util.alertErrorBox("鎮ㄦ病鏈夋鍟嗗搧鐨凷鐮佹垨S鐮佽繕娌℃湁<a href='" + getBindScodeUrl() + "'  target='_Blank'>婵€娲�</a>");
                                                                quickPress(false)
                                                            } else {
                                                                if (response.errorCode == "psellNotBuyTime") {
                                                                    Util.alertErrorBox(response.errorMessage)
                                                                } else {
                                                                    if (response.isOverLimitCnt == "OVERLIMIT") {
                                                                        var url = "http://" + sn.cartPath + "/OrderItemDisplay?langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId;
                                                                        Util.alertErrorBox("鎮ㄧ殑璐墿杞﹀晢鍝佹竻鍗曠绫诲凡杈�50绉嶄笂闄愶紝寤鸿鎮ㄧ珛鍗�<a href=" + url + ">娓呯悊璐墿杞�</a>")
                                                                    } else {
                                                                        if (response.errorCode == "NOTVALIDUSER") {
                                                                            Util.alertErrorBox("鐢ㄦ埛鐨勪細鍛樺崱鐘舵€佷笉姝ｇ‘,璇峰挩璇㈠鏈嶏紒")
                                                                        } else {
                                                                            if (response.errorCode == "NOTSALE") {
                                                                                var url = "http://" + sn.domain;
                                                                                Util.alertErrorBox("姝ゅ晢鍝佹殏涓嶉攢鍞紝鎮ㄥ彲浠ュ皾璇曢€夎喘鍏朵粬鍟嗗搧<a href=" + url + ">閫夎喘鍏朵粬鍟嗗搧</a>")
                                                                            } else {
                                                                                if (response.errorCode == "ITNOTSALE") {
                                                                                    Util.alertErrorBox("瀵逛笉璧凤紝璇ュ晢鍝佸府瀹㈡湇鍔℃殏涓嶉攢鍞紝璇峰彇娑堝嬀閫夊悗閲嶆柊鍔犲叆璐墿杞︺€�")
                                                                                } else {
                                                                                    if (response.errorCode == "NOSALESORGITEM") {
                                                                                        Util.alertErrorBox("瀵逛笉璧�,姝ゅ晢鍝佹棤閿€鍞粍缁囷紝鍔犲叆璐墿杞﹀け璐�")
                                                                                    } else {
                                                                                        if (response.errorCode == "limitShopping") {
                                                                                            Util.alertErrorBox("姝ゅ晢鍝佷负闄愯喘鍟嗗搧锛屾渶澶氬彲璐拱" + response.limitCount + "浠�")
                                                                                        } else {
                                                                                            if (response.errorCode == "fql_0001") {
                                                                                                Util.alertErrorBox("鎮ㄧ殑鎿嶄綔杩囦簬棰戠箒锛岃绋嶅悗鍐嶈瘯鍝︼紒")
                                                                                            } else {
                                                                                                if (response.errorCode == "cloudTimeover") {
                                                                                                    Util.alertErrorBox("姝ゅ晢鍝佺殑鍏戞崲娲诲姩宸茬粨鏉燂紒");
                                                                                                    cloudInfo.state = "01";
                                                                                                    cloudInfo.getExchengeStatus()
                                                                                                } else {
                                                                                                    if (response.errorCode == "cloudInvNotEnough") {
                                                                                                        Util.alertErrorBox("鎮ㄨ喘涔扮殑鏁伴噺瓒呰繃鍙厬鎹㈤噺锛岃淇敼鍟嗗搧鏁伴噺");
                                                                                                        cloudInfo.state = "02";
                                                                                                        cloudInfo.getExchengeStatus()
                                                                                                    } else {
                                                                                                        if (response.errorCode == "noInv") {
                                                                                                            Util.alertErrorBox("姝ゅ晢鍝佸凡鍏戞崲鍏変簡锛屾偍鍙互閫夋嫨浠ユ槗璐环璐拱锛�");
                                                                                                            cloudInfo.state = "03";
                                                                                                            cloudInfo.getExchengeStatus()
                                                                                                        } else {
                                                                                                            if (response.errorCode == "cloudNotEnoughOne") {
                                                                                                                Util.alertErrorBox("鎮ㄧ殑浜戦捇涓嶈冻锛屾殏涓嶈兘鍏戞崲姝ゅ晢鍝侊紒");
                                                                                                                cloudInfo.state = "04";
                                                                                                                cloudInfo.getExchengeStatus()
                                                                                                            } else {
                                                                                                                if (response.errorCode == "cloudNotEnoughMulti") {
                                                                                                                    Util.alertErrorBox("浜戦捇涓嶈冻锛岃淇敼鍟嗗搧鏁伴噺");
                                                                                                                    cloudInfo.state = "05";
                                                                                                                    cloudInfo.getExchengeStatus()
                                                                                                                } else {
                                                                                                                    if (response.errorCode == "wrongInput") {
                                                                                                                        Util.alertErrorBox("缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒锛�");
                                                                                                                        cloudInfo.state = "06";
                                                                                                                        cloudInfo.getExchengeStatus()
                                                                                                                    } else {
                                                                                                                        if (response.hasInventor == 1 && response.treaph == 0) {
                                                                                                                            if (isPreBuy == 1 || cloudInfo.addCartState == "1") {
                                                                                                                                shoppingCartUrl = "http://" + sn.cartPath + "/SNCart2ManageCmd?langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId + "&returnURL=" + fourthURL;
                                                                                                                                toShoppingCart()
                                                                                                                            } else {
                                                                                                                                if (response.addToCartAB == "A") {
                                                                                                                                    shoppingCartUrl = "http://" + sn.cartPath + "/addToCart?pid=" + partnumber + "&vid=" + vendorCode + "&langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId;
                                                                                                                                    toShoppingCart()
                                                                                                                                } else {
                                                                                                                                    shoppingCartUrl = "http://" + sn.cartPath + "/OrderItemDisplay?langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId + "&returnURL=" + fourthURL;
                                                                                                                                    shoppingCartPopBox(cityId);
                                                                                                                                    SFE.base.miniCartReload()
                                                                                                                                }
                                                                                                                            }
                                                                                                                        } else {
                                                                                                                            if (response.hasInventor == 0 && response.invErrFlow == 1) {
                                                                                                                                Util.alertErrorBox("姝ゅ晢鍝佹棤璐э紝鎮ㄥ彲浠ュ皾璇曢€夎喘鍏朵粬鍟嗗搧锛�")
                                                                                                                            } else {
                                                                                                                                if (response.hasInventor == 0 && response.invErrFlow == 2) {
                                                                                                                                    Util.alertErrorBox("鎮ㄨ喘涔扮殑鏁伴噺瓒呰繃搴撳瓨涓婇檺锛岃淇敼鍟嗗搧鏁伴噺")
                                                                                                                                } else {
                                                                                                                                    if (response.hasInventor == 0 && (response.invErrFlow == 3 || response.invErrFlow == 0)) {
                                                                                                                                        if (isPreBuy == 1 || cloudInfo.addCartState == "1") {
                                                                                                                                            shoppingCartUrl = "http://" + sn.cartPath + "/SNCart2ManageCmd?langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId + "&returnURL=" + fourthURL;
                                                                                                                                            toShoppingCart()
                                                                                                                                        } else {
                                                                                                                                            if (response.addToCartAB == "A") {
                                                                                                                                                shoppingCartUrl = "http://" + sn.cartPath + "/addToCart?pid=" + partnumber + "&vid=" + vendorCode + "&langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId;
                                                                                                                                                toShoppingCart()
                                                                                                                                            } else {
                                                                                                                                                shoppingCartUrl = "http://" + sn.cartPath + "/OrderItemDisplay?langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId + "&invErrSb=" + response.invErrSb + "&returnURL=" + fourthURL;
                                                                                                                                                shoppingCartPopBox(cityId);
                                                                                                                                                SFE.base.miniCartReload()
                                                                                                                                            }
                                                                                                                                        }
                                                                                                                                    }
                                                                                                                                }
                                                                                                                            }
                                                                                                                        }
                                                                                                                    }
                                                                                                                }
                                                                                                            }
                                                                                                        }
                                                                                                    }
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                } if (typeof (cloudInfo.initCartState) == "function") {
                    cloudInfo.initCartState()
                }
                if (isPreBuy != 1) {
                    cartPress(false)
                }
            }, error: function () {
                Util.alertErrorBox("缃戠粶寮傚父锛屾偍鍙互妫€鏌ョ綉缁滄垨鍐嶈瘯涓€娆★紒");
                if (typeof (cloudInfo.initCartState) == "function") {
                    cloudInfo.initCartState()
                }
                if (isPreBuy != 1) {
                    cartPress(false)
                }
            }
        })
    }
    var saveMessageToCloud = function (cmmdtyCode, shopCode) {
        var phoneNumber = cart.common._getInputVal($("#safe_phone"));
        var addresses = $(".citySelect .cityboxbtn").find("span");
        var address = $(addresses[0]).text() + "," + $(addresses[1]).text() + "," + $(addresses[2]).text();
        var email = cart.common._getInputVal($("#safe_email"));
        var fg = cart.normal.validation();
        if (fg) {
            var cspVO = {
                phoneNumber: phoneNumber,
                cmmdtyCode: cmmdtyCode,
                shopCode: shopCode,
                address: address,
                email: email
            };
            $.ajax({
                url: "//shopping.suning.com/cartSpareProgramme.do",
                data: {
                    cspVO: JSON.stringify(cspVO)
                },
                type: "POST",
                dataType: "jsonp",
                success: function (data) {
                    if (data == "1") {
                        $.unmLionDialog();
                        cart.normal.alertTip("淇℃伅鎻愪氦鎴愬姛锛�");
                        setTimeout("$.unmLionDialog()", 1000)
                    } else {
                        var errorDetail = {
                            cspVO: cspVO,
                            data: data
                        };
                        sendUomMsgV2("2", "ccf-gwc1-20014", "0", "cartSpareProgramme", errorDetail);
                        $.unmLionDialog();
                        cart.normal.alertTip("淇℃伅鎻愪氦澶辫触,璇风◢鍚庡啀璇�!");
                        setTimeout("$.unmLionDialog()", 1000)
                    }
                }, error: function (data) {
                    $.unmLionDialog();
                    cart.normal.alertTip("淇℃伅鎻愪氦澶辫触,璇风◢鍚庡啀璇�!");
                    sendUomMsgV2("1", "ccf-gwc1-20014", "1", "cartSpareProgramme", cspVO);
                    setTimeout("$.unmLionDialog()", 1000)
                }
            })
        }
    };
    var safeDpsInit = function (cmmdtyCode, shopCode) {
        $.mLionDialog({
            css: {
                width: "445px"
            },
            http: function (e, o) {
                var html = "<div class='dialog-common dialog-degrade'><p class='tips'><i class='tip-icon tip-warning-24'></i><span>鎶辨瓑!鐢变簬绯荤粺鍗囩骇锛屾殏鏃舵棤娉曡喘涔板晢鍝侊紝璇风暀涓嬫偍鐨勪俊鎭紝寰呯郴缁熸仮澶嶅悗锛屼細绗竴鏃堕棿閫氱煡鎮�</span></p><div class='address-form'><div class='row clearfix error-row'><div class='label'><em>*</em>鎵嬫満鍙风爜锛�</div><div class='field'><input type='text' id='safe_phone' class='ui-text user' maxlength='11' data-is-enter='0' placetext='璇峰～鍐欐纭殑11浣嶆墜鏈哄彿鐮�' style='color: rgb(187, 187, 187);'><span class='tip-message'></span></div></div><div class='row clearfix error-row'><div class='label'>閭鍦板潃锛�</div><div class='field'><input type='text' id='safe_email' class='ui-text user' maxlength='20' data-is-enter='0' placetext='璇峰～鍐欐纭殑閭鍦板潃' style='color: rgb(187, 187, 187);'><span class='tip-message'></span></div></div><div class='row zdx10 clearfix'><div class='label'><em>*</em>鎵€鍦ㄥ湴鍖猴細</div><div class='field rel'><div id='city1' class='citySelect clearfix'> <a href='javascript:void(0);' class='cityboxbtn'></a><div class='citybox'><div class='chooseArea fix'><p eq='0' class='cur'><span>瀹夊窘</span><b></b></p><p eq='1'><span>榛勫北甯�</span><b></b></p><p eq='2'><span>灞邯鍖�</span><b></b></p><p class='disable'><span>璇烽€夋嫨涔￠晣</span><b></b></p><div class='clear'></div></div><div class='arriveBox'><div class='cityshow'>鍔犺浇涓�...</div></div><div class='closeSelector'></div></div></div><span class='tip-message'></span></div></div><div class='row zdx5 clearfix'><div class='label'><em>*</em>璇︾粏鍦板潃锛�</div><div class='field detail-field'><input type='text' class='ui-text detial-address' id='safe_detial_address' maxlength='30' placetext='琛楅亾銆佸皬鍖恒€佹ゼ鐗屽彿锛屾棤椤婚噸澶嶅～鍐欑渷甯傚尯'><span class='tip-message'></span></div></div></div><div class='dialog-btn'><a class='dialog-opt dialog-certain' name='icart1_cscError_confirm' href='javascript:cart.normal.saveMessageToCloud(" + cmmdtyCode + "," + shopCode + ");'>纭畾</a><a class='dialog-opt dialog-close close' name='icart1_cscError_cancel' href='javascript:void(0);'>鍙栨秷</a></div></div>";
                e.find(".content").html(html);
                cloudCart.supportPlaceHolder.init(".m-lion-dialog")
            }, overlayCss: {
                background: "black",
                opacity: "0.3"
            }, fadeIn: 300,
            fadeOut: 300
        });
        $(".m-lion-dialog .container a.btn.close").attr("name", "icart1_cscError_close");
        cart.normal.addressSelect();
        cart.normal.addressValidation();
        cart.normal.safeValidation()
    };
    var alertTip = function (message) {
        $.mLionDialog({
            css: {
                width: "445px"
            },
            http: function (e, o) {
                var html = "<div class='content'><div class='add-cart-prompt dialog-common'><p class='tips'><i class='tip-icon tip-warning-24'></i>" + message + "</p></div></div>";
                e.find(".content").html(html);
                cloudCart.supportPlaceHolder.init(".m-lion-dialog")
            }, overlayCss: {
                background: "black",
                opacity: "0.3"
            }, fadeIn: 300,
            fadeOut: 300
        })
    };
    var addressSelect = function () {
        var addressColumns;
        addressColumns = [{
            state: "prov",
            text: "璇烽€夋嫨鐪�",
            hide: false,
            addclass: "c-f70"
        }, {
            state: "city",
            text: "璇烽€夋嫨甯�",
            hide: false,
            addclass: "c-f70"
        }, {
            state: "area",
            text: "璇烽€夋嫨鍖�",
            hide: false,
            addclass: "c-f70"
        }];
        addressDatas = [{
            name: "",
            code: "",
            id: ""
        }, {
            name: "",
            code: "",
            id: ""
        }, {
            name: "",
            code: "",
            id: ""
        }];
        regionInfo1 = $("#city1").SnAddress({
            columns: addressColumns,
            url: "//shopping.suning.com/address/querySNAddress.do",
            complete: function (items, bool) {
                if (!bool) {
                    $("#city1 .cityboxbtn span").removeClass();
                    cart.normal.addressValidation()
                }
            }
        }, addressDatas).data("suning.address")
    };

    function safeValidation() {
        $(document).on("blur", ".address-form .field #safe_phone", function () {
            cart.normal.phoneValidation()
        });
        $(document).on("blur", ".address-form .field #safe_email", function () {
            cart.normal.emailValidation()
        });
        $(document).on("blur", ".address-form .field #safe_detial_address", function () {
            cart.normal.tailAddressValidation()
        })
    }
    var validation = function () {
        var emailRg = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
        var phoneRg = /^1[0-9]{10}$/;
        var phone = cart.common._getInputVal($("#safe_phone"));
        var email = cart.common._getInputVal($("#safe_email"));
        var safe_detial_address = cart.common._getInputVal($("#safe_detial_address"));
        var flag = true;
        if (phone == null || phone.trim() == "") {
            $("#safe_phone").next().html("<i class='tip-icon tip-error'></i>鎵嬫満鍙风爜涓嶈兘涓虹┖");
            flag = false
        } else {
            if (!phoneRg.test(phone)) {
                $("#safe_phone").next().html("<i class='tip-icon tip-error'></i>璇峰～鍐欎互1寮€澶寸殑11浣嶇數璇濆彿鐮�");
                flag = false
            } else {
                $("#safe_phone").next().html("<i class='tip-icon tip-ok'></i>")
            }
        } if (!emailRg.test(email) && email.trim() != "" && email != null) {
            $("#safe_email").next().html("<i class='tip-icon tip-error'></i>閭鏍煎紡涓嶆纭�");
            flag = false
        } else {
            if (emailRg.test(email)) {
                $("#safe_email").next().html("<i class='tip-icon tip-ok'></i>")
            } else {
                $("#safe_email").next().html("")
            }
        } if (cart.common.isEmpty(safe_detial_address)) {
            $("#safe_detial_address").next().html("<i class='tip-icon tip-error'></i>璇峰～鍐欒缁嗗湴鍧€");
            flag = false
        } else {
            if (!cart.common.checkIsValid(safe_detial_address)) {
                $("#safe_detial_address").next().html("<i class='tip-icon tip-error'></i>涓嶈兘鍖呭惈鐗规畩瀛楃");
                flag = false
            } else {
                $("#safe_detial_address").next().html("<i class='tip-icon tip-ok'></i>")
            }
        }
        return flag
    };
    var tailAddressValidation = function () {
        var safe_detial_address = cart.common._getInputVal($("#safe_detial_address"));
        if (cart.common.isEmpty(safe_detial_address)) {
            $("#safe_detial_address").next().html("<i class='tip-icon tip-error'></i>璇︾粏鍦板潃涓嶈兘涓虹┖")
        } else {
            if (!cart.common.checkIsValid(safe_detial_address) && !cart.common.isEmpty(safe_detial_address)) {
                $("#safe_detial_address").next().html("<i class='tip-icon tip-error'></i>涓嶈兘鍖呭惈鐗规畩瀛楃")
            } else {
                if (!cart.common.isEmpty(safe_detial_address)) {
                    $("#safe_detial_address").next().html("<i class='tip-icon tip-ok'></i>")
                } else {
                    $("#safe_detial_address").next().html("")
                }
            }
        }
    };
    var emailValidation = function () {
        var emailRg = /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/;
        var email = cart.common._getInputVal($("#safe_email"));
        if (!emailRg.test(email) && email.trim() != "" && email != null) {
            $("#safe_email").next().html("<i class='tip-icon tip-error'></i>閭鏍煎紡涓嶆纭�")
        } else {
            if (emailRg.test(email)) {
                $("#safe_email").next().html("<i class='tip-icon tip-ok'></i>")
            } else {
                $("#safe_email").next().html("")
            }
        }
    };
    var phoneValidation = function () {
        var phoneRg = /^1[0-9]{10}$/;
        var phone = cart.common._getInputVal($("#safe_phone"));
        if (phone.trim() == "" || phone == null) {
            $("#safe_phone").next().html("<i class='tip-icon tip-error'></i>鎵嬫満鍙风爜涓嶈兘涓虹┖")
        } else {
            if (!phoneRg.test(phone) && phone.trim() != "" && phone != null) {
                $("#safe_phone").next().html("<i class='tip-icon tip-error'></i>璇峰～鍐欎互1寮€澶寸殑11浣嶇數璇濆彿鐮�")
            } else {
                if (phoneRg.test(phone)) {
                    $("#safe_phone").next().html("<i class='tip-icon tip-ok'></i>")
                } else {
                    $("#safe_phone").next().html("")
                }
            }
        }
    };
    var addressValidation = function () {
        if ($("#city1 .cityboxbtn span").eq(0).hasClass("c-f70")) {
            $("#safe_detial_address").attr("disabled", "disabled")
        } else {
            $("#safe_detial_address").removeAttr("disabled")
        }
    };
    return {
        addCart: addCart,
        buyNow: buyNow,
        addToCart: addToCart,
        add2Cart: add2Cart,
        saveMessageToCloud: saveMessageToCloud,
        safeDpsInit: safeDpsInit,
        alertTip: alertTip,
        addressSelect: addressSelect,
        validation: validation,
        safeValidation: safeValidation,
        addressValidation: addressValidation,
        recommendBuyCallBack: recommendBuyCallBack,
        phoneValidation: phoneValidation,
        emailValidation: emailValidation,
        tailAddressValidation: tailAddressValidation,
        chooseCartTelNumber: chooseCartTelNumber,
        virtualGameBuyNow: virtualGameBuyNow,
        carHouseKeeperBuyNow: carHouseKeeperBuyNow
    }
})(jQuery);
cart.common = (function ($) {
    var envType = "PRD";
    var domain_pre_reg = /^(\w*)(pre)(\w*)(.cnsuning.com)$/;
    var domain_sit_reg = /^(\w*)(sit)(\w*)(.cnsuning.com)$/;
    var domain_dev_reg = /^(\w*)(dev)(\w*)(.cnsuning.com)$/;
    var _hostName = document.location.hostname;
    var protocol = window.location.protocol;
    if (domain_pre_reg.test(_hostName)) {
        envType = "PRE"
    } else {
        if (domain_sit_reg.test(_hostName)) {
            envType = "SIT"
        } else {
            if (domain_dev_reg.test(_hostName)) {
                envType = "DEV"
            } else {
                envType = "PRD"
            }
        }
    }
    var passport_config = {
        base: "//shopping.suning.com/",
        loginTheme: "b2c_pop"
    };
    var getScriptDomain = function () {
        var scriptDomain = "";
        scriptDomain = ("https:" == protocol) ? "https://res.suning.cn" : "//res.suning.cn";
        return scriptDomain
    };
    var getBindPhoneUrl = function () {
        return "https://aq.suning.com/asc/mobile/check.do"
    };
    var getBrondPayUrl = function () {
        var brondPayUrl = "";
        brondPayUrl = "https://passport.suning.com/ids/trustLogin?sysCode=epp&targetUrl=https://pay.suning.com/epp-epw/quickPay/quick-pay-contract!showBankList.action";
        return brondPayUrl
    };
    var getBindScodeUrl = function () {
        return "//sma.suning.com/sma/self/toBind.htm"
    };
    var esjs = document.getElementsByTagName("script");
    var escss = document.getElementsByTagName("link");
    var isInclude = function (name, isJs) {
        if (isJs) {
            for (var i = 0; i < esjs.length; i++) {
                if (esjs[i][isJs ? "src" : "href"].indexOf(name) != -1) {
                    return true
                }
            }
            return false
        } else {
            for (var i = 0; i < escss.length; i++) {
                if (escss[i][isJs ? "src" : "href"].indexOf(name) != -1) {
                    return true
                }
            }
            return false
        }
    };
    var _loadAsyncJs = function (src) {
        if (isInclude(src, true)) {
            return
        }
        var _src = src;
        var _scripts = document.getElementsByTagName("script");
        for (var i = 0; i < _scripts.length; i++) {
            if (_scripts[i].src == _src) {
                return
            }
        }
        var _script = document.createElement("script");
        _script.type = "text/javascript";
        _script.async = true;
        _script.src = _src;
        var _s = _scripts[0];
        _s.parentNode.insertBefore(_script, _s)
    };
    var _loadJs = function (src) {
        if (isInclude(src, true)) {
            return
        }
        var _src = src;
        var _scripts = document.getElementsByTagName("script");
        for (var i = 0; i < _scripts.length; i++) {
            if (_scripts[i].src == _src) {
                return
            }
        }
        var _script = document.createElement("script");
        _script.type = "text/javascript";
        _script.src = _src;
        var _s = _scripts[0];
        _s.parentNode.insertBefore(_script, _s)
    };
    var _getInputVal = function (inputObj) {
        var inputVal = $.trim(inputObj.val());
        var defaultVal = inputObj.attr("placetext");
        if (inputVal == defaultVal && inputObj.attr("data-is-enter") == 0) {
            inputVal = ""
        }
        return inputVal
    };
    var _loadSillerCss = function () {
        if ($('link[href*="/detect/static/siller.css"]').length == 0) {
            var link = document.createElement("link");
            link.type = "text/css";
            link.rel = "stylesheet";
            link.href = "//dt.suning.com/detect/static/siller.css" + version;
            document.getElementsByTagName("head")[0].appendChild(link)
        }
    };
    var isEmpty = function (str) {
        return str == null || str == undefined || str == ""
    };
    var getUrlParam = function (name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var r = window.location.search.substr(1).match(reg);
        if (r != null) {
            return decodeURI(r[2])
        }
        return ""
    };
    var obj2string = function (o) {
        var r = [];
        if (null == o || typeof (o) == "undefined") {
            return ""
        }
        if (typeof o == "string") {
            return o
        }
        if (typeof o == "object") {
            if (!o.sort) {
                for (var i in o) {
                    if ("string" == typeof (o[i])) {
                        r.push('"' + i + '":"' + obj2string(o[i]) + '"')
                    } else {
                        r.push('"' + i + '":' + obj2string(o[i]))
                    }
                }
                if (!!document.all && !/^\n?function\s*toString\(\)\s*\{\n?\s*\[native code\]\n?\s*\}\n?\s*$/.test(o.toString)) {
                    r.push("toString:" + o.toString.toString())
                }
                r = "{" + r.join() + "}"
            } else {
                for (var i = 0; i < o.length; i++) {
                    r.push(obj2string(o[i]))
                }
                r = "[" + r.join() + "]"
            }
            return r
        }
        return o.toString()
    };
    var setCookie = function (keyStr, valStr) {
        var v3 = window.location.href;
        v3 = v3.substring(v3.indexOf("//") + 2);
        v3 = v3.substring(0, v3.indexOf("/"));
        if (v3.indexOf(".") > 0) {
            v3 = v3.substring(v3.indexOf("."))
        }
        var domain = v3;
        var path = "/";
        var str = keyStr + "=" + encodeURIComponent(valStr) + ";domain=" + domain + ";path=" + path;
        document.cookie = str
    };
    var checkIsValid = function (f) {
        var d = /([\u4e00-\u9fa5\u9fa6-\u9fef\u3400-\u4db5\u20000-\u2a6d6\u2a700-\u2b734\u2b740-\u2b81d\u2b820-\u2cea1\u2ebe0\u2f00-\u2fd5\u2e80-\u2ef3\uf900-\ufad9\u2f800-\u2fa1d\ue815-\ue86f\ue400-\ue518]|\w|[#&路.-]|[\uff0c\uff08\,\u3001\u3002\u00b7\_\u300a\u300b\uff09\(\)| ])+/;
        for (var e = 0; e < f.length; e++) {
            if (!d.test(f.charAt(e))) {
                return false
            }
        }
        return true
    };
    var dealPreZeroPartnum = function (str) {
        var rg = new RegExp("^0*");
        return str.replace(rg, "")
    };
    return {
        getScriptDomain: getScriptDomain,
        getBindPhoneUrl: getBindPhoneUrl,
        getBrondPayUrl: getBrondPayUrl,
        getBindScodeUrl: getBindScodeUrl,
        isInclude: isInclude,
        _loadAsyncJs: _loadAsyncJs,
        _loadJs: _loadJs,
        _loadSillerCss: _loadSillerCss,
        isEmpty: isEmpty,
        getUrlParam: getUrlParam,
        setCookie: setCookie,
        obj2string: obj2string,
        passport_config: passport_config,
        _getInputVal: _getInputVal,
        checkIsValid: checkIsValid,
        dealPreZeroPartnum: dealPreZeroPartnum
    }
})(jQuery);
cart.security = (function ($) {
    var needVerifyCodeVal = false;
    var v_uuid = "";
    var verifyCodeVal = "";
    var gImgVerCdeErrorCount = 0;
    var gLastImgValCode = "";
    var sceneId = "";
    var defaultValue = "浠ヤ笅瀛楃涓嶅尯鍒嗗ぇ灏忓啓";
    var setNeedVerifyCodeVal = function (_needVerifyCodeVal) {
        needVerifyCodeVal = _needVerifyCodeVal
    };
    var getNeedVerifyCodeVal = function () {
        return needVerifyCodeVal
    };
    var getUUID = function () {
        return v_uuid
    };
    var getVerifyCodeVal = function () {
        return verifyCodeVal
    };
    var getSceneId = function () {
        return sceneId
    };
    var setDefauleValue = function (sceneId) {
        if (sceneId != null && sceneId != undefined && sceneId != "undefined") {
            if (sceneId == "1") {
                defaultValue = "浠ヤ笅瀛楃涓嶅尯鍒嗗ぇ灏忓啓"
            } else {
                if (sceneId == "4") {
                    defaultValue = "璇疯緭鍏ヤ互涓嬫眽瀛�"
                } else {
                    if (sceneId == "5") {
                        defaultValue = "璇疯緭鍏ヤ互涓嬮棶棰樼殑璁＄畻缁撴灉"
                    }
                }
            }
        }
    };
    var getDefaultValue = function () {
        return defaultValue
    };
    var fun_getVcode = function () {
        gImgVerCdeErrorCount = 0;
        $("#validateCode").removeClass("error-input");
        document.getElementById("vcodeimg1").src = "//vcs.suning.com/vcs/imageCode.htm?uuid=" + v_uuid + "&sceneId=" + sceneId + "&yys=" + new Date().getTime()
    };
    var onKeyUpForValidate = function (evt) {
        evt = (evt) ? evt : ((window.event) ? window.event : "");
        var keyCode = evt.keyCode ? evt.keyCode : evt.which;
        if (keyCode == 13) {
            ajaxCheckVerifyCodeOrSubmit(true)
        }
    };
    var onBlurForValidate = function () {
        var code = $("#validateCode").val();
        if (code == null || code == "") {
            return false
        } else {
            ajaxCheckVerifyCodeOrSubmit(false)
        }
    };
    var ajaxCheckVerifyCodeOrSubmit = function (isSubmit) {
        var code = $("#validateCode").val();
        if (!isSubmit && isLastImgValCode(code)) {
            return
        }
        var param = {
            code: code,
            uuid: v_uuid,
            sceneId: sceneId,
            delFlag: 0
        };
        $.ajax({
            type: "POST",
            url: "//vcs.suning.com/vcs/validate_jsonp.htm",
            data: param,
            dataType: "jsonp",
            jsonp: "callback",
            success: function (data) {
                if (data[0].result == "true") {
                    result = true;
                    $("#validateCode").removeClass("error-input");
                    $("#imageVerifytip").addClass("tip-icon").show();
                    $(".code-error").hide();
                    if (isSubmit) {
                        verifyCodeVal = code;
                        $.unmDialog();
                        if (cart.toCartCallback.getOperateType() == "0") {
                            cart.normal.addCart(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                        } else {
                            if (cart.toCartCallback.getOperateType() == "1") {
                                cart.normal.buyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                            } else {
                                if (cart.toCartCallback.getOperateType() == "2") {
                                    cart.normal.virtualGameBuyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                                } else {
                                    if (cart.toCartCallback.getOperateType() == "3") {
                                        cart.normal.carHouseKeeperBuyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                                    }
                                }
                            }
                        }
                    }
                } else {
                    $("#validateCode").addClass("error-input");
                    $("#imageVerifytip").hide();
                    $(".code-error").show();
                    gImgVerCdeErrorCount++;
                    if (gImgVerCdeErrorCount >= 3 || isSubmit) {
                        fun_getVcode()
                    }
                }
            }
        })
    };
    var isLastImgValCode = function (code) {
        if (gLastImgValCode == code) {
            return true
        } else {
            gLastImgValCode = code;
            return false
        }
    };
    var showMinos1 = function () {
        $.mDialog({
            title: "娓╅Θ鎻愮ず",
            message: $("#J-boom"),
            css: {
                width: "442px"
            },
            overlayClick: true
        })
    };
    var showMinos2 = function () {
        $.mDialog({
            title: "娓╅Θ鎻愮ず",
            message: $("#J-company-channel"),
            css: {
                width: "442px"
            },
            overlayClick: true
        })
    };
    var showMinos3 = function (t_uuid, t_sceneId) {
        $("#J-identify-code").remove();
        v_uuid = t_uuid;
        if (t_sceneId != null && t_sceneId != undefined && t_sceneId != "undefined") {
            sceneId = t_sceneId
        }
        verifyCodeVal = "";
        setDefauleValue(sceneId);
        var url = "//vcs.suning.com/vcs/imageCode.htm?uuid=" + v_uuid + "&sceneId=" + sceneId + "&yys=" + new Date().getTime();
        var errorMsg = "<div id='J-identify-code' style=''><div class='identify-code'><p class='tips'>寰堟姳姝夛紝鎮ㄨ喘涔扮殑瀹濊礉閿€鍞紓甯哥伀鐖嗭紝璇风◢鍚庡啀璇晘</p><div class='code-input clearfix'><dl><dt class='l'>楠岃瘉鐮�</dt><dd class='l'><p class='item-ide'><input id='validateCode' autocomplete='off' class='ui-text l' type='text' value='" + defaultValue + "'><i id='imageVerifytip' class='tip-icon tip-ok-16 tip-ok l' style='display:none;'></i><em class='code-error l' style='display:none;'>楠岃瘉鐮侀敊璇�</em></p><p class='item-ide'><img onclick='cart.security.fun_getVcode()' name='vcodeimg1' id='vcodeimg1' class='l' src='" + url + "' alt=''><span class='change l'>鐪嬩笉娓呮锛�<a href='javascript:void(0);' onclick='cart.security.fun_getVcode()'>鎹竴寮�</a></span></p><p class='item-ide'><a class='lion-btn certain' href='javascript:void(0);' onclick='cart.security.ajaxCheckVerifyCodeOrSubmit(true);return false;'>纭畾</a><a class='lion-btn close' href='javascript:void(0);'>鍏抽棴</a></p></dd></dl></div></div></div>";
        $.mDialog({
            title: "娓╅Θ鎻愮ず",
            message: errorMsg,
            css: {
                width: "448px"
            },
            overlayClick: true,
            callback: function () {
                $(".m-dialog").addClass("resetbtn-ccf");
                $(".resetbtn-ccf .close").on("click", function () {
                    var resp = "";
                    resp.result = "0";
                    cart.toCartCallback.getCallback()(resp)
                })
            }
        });
        var inputs = $(".m-dialog input");
        inputs.blur(function () {
            if ($(this).val() == "") {
                $(this).val(defaultValue).css("color", "#999");
                return
            } else {
                if ($(this).val() != defaultValue) {
                    $(this).css("color", "#333")
                }
            }
        });
        inputs.focus(function () {
            if ($(this).val() == defaultValue) {
                $(this).val("").removeAttr("style").keyup();
                $(this).css("color", "#333")
            }
        });
        $("#validateCode").keyup(cart.security.onKeyUpForValidate);
        $("#validateCode").blur(cart.security.onBlurForValidate)
    };
    var jigsawInit = function (ticket) {
        if ($("body #jigsaw_id").length < 1) {
            $("body").append('<div class="hide" id="">')
        }
        jigsawObj = SnCaptcha.init({
            id: "jiasawcode",
            env: "prd",
            type: "popup",
            target: "jigsaw_id",
            disableClose: true,
            ticket: ticket,
            width: "300px",
            height: "30px",
            callback: function (token) {
                if (jigsawObj.queryStatus() == true && typeof (token) != "undefined" && token != "undefined" && token != null) {
                    if (cart.toCartCallback.getOperateType() == "1") {
                        cart.normal.buyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                    } else {
                        if (cart.toCartCallback.getOperateType() == "2") {
                            cart.normal.virtualGameBuyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                        } else {
                            if (cart.toCartCallback.getOperateType() == "0") {
                                cart.normal.addCart(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                            }
                        }
                    }
                }
            }
        })
    };
    var sillerComfirm = function () {
        if (typeof (siller) == "undefined" || siller == "undefined" || siller.status == "0") {
            $("#siller_error_msg").show();
            return
        }
        var sillerToken = siller.queryToken();
        if (sillerToken == "REF" || sillerToken == "" || typeof (sillerToken) == "undefined" || sillerToken == "undefined" || sillerToken == null) {
            $("#siller_error_msg").show();
            return
        }
        $.unmDialog();
        if (cart.toCartCallback.getOperateType() == "0") {
            cart.normal.addCart(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
        } else {
            if (cart.toCartCallback.getOperateType() == "1") {
                cart.normal.buyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
            } else {
                if (cart.toCartCallback.getOperateType() == "2") {
                    cart.normal.virtualGameBuyNow(cart.toCartCallback.getData(), cart.toCartCallback.getCallback(), cart.toCartCallback.getHttpSwitch())
                }
            }
        }
    };
    return {
        setNeedVerifyCodeVal: setNeedVerifyCodeVal,
        getNeedVerifyCodeVal: getNeedVerifyCodeVal,
        getUUID: getUUID,
        getSceneId: getSceneId,
        getVerifyCodeVal: getVerifyCodeVal,
        onKeyUpForValidate: onKeyUpForValidate,
        onBlurForValidate: onBlurForValidate,
        showMinos1: showMinos1,
        showMinos2: showMinos2,
        showMinos3: showMinos3,
        fun_getVcode: fun_getVcode,
        ajaxCheckVerifyCodeOrSubmit: ajaxCheckVerifyCodeOrSubmit,
        getDefaultValue: getDefaultValue,
        jigsawInit: jigsawInit,
        sillerComfirm: sillerComfirm
    }
})(jQuery);
cart.analytics = (function ($) {
    var savePageSaleInfo = function (partnumber, vendorCode) {
        vendorCode = cart.common.isEmpty(vendorCode) ? "0000000000" : vendorCode;
        partnumber = partnumber.length == 18 ? partnumber.substring(9, 19) : partnumber;
        var productInfo = partnumber + "_" + vendorCode;
        var fromPoint = $.trim(cart.common.getUrlParam("srcpoint"));
        try {
            pageSaleCookieUtil.saveCookie(productInfo, fromPoint)
        } catch (e) {}
    };
    var updatePageSaleInfo = function () {
        try {
            pageSaleCookieUtil.updateCustNo()
        } catch (e) {}
    };
    var recordErrorMsg = function (resp) {
        try {
            var reg = /^9/g;
            var errorType = "1";
            if (reg.test(resp.failCode) || resp.failCode == "001") {
                errorType = "0"
            }
            if (resp.backErrorCode != undefined && resp.backErrorCode != "undefined" && resp.backErrorCode != "") {
                sa.openAPI.sendMessage(resp.analyticsType, resp.failCode + "&&" + errorType + "&&" + resp.failMsg + "锛�" + resp.backErrorCode + "锛�&&" + getCookie("custno"), "", "", "ccfShop")
            } else {
                sa.openAPI.sendMessage(resp.analyticsType, resp.failCode + "&&" + errorType + "&&" + resp.failMsg + "&&" + getCookie("custno"), "", "", "ccfShop")
            }
        } catch (e) {}
    };
    var runAnalyseExpo = function () {
        if (typeof _analyseExpoTags == "function") {
            _analyseExpoTags("a")
        } else {
            setTimeout(cart.analytics.runAnalyseExpo, 1000)
        }
    };
    var clickSendData = function () {
        $("a[name^=cartc_],a[name^=cart1_go],a[name^=icart1_cscError_]").live("click", function () {
            sa.click.sendDatasIndex(this)
        })
    };
    return {
        savePageSaleInfo: savePageSaleInfo,
        updatePageSaleInfo: updatePageSaleInfo,
        recordErrorMsg: recordErrorMsg,
        runAnalyseExpo: runAnalyseExpo,
        clickSendData: clickSendData
    }
})(jQuery);
cart.recommended = (function ($) {
    var shoppingCartPopBox = function (cityId) {
        $.mDialog({
            css: {
                width: "460px"
            },
            http: function (e, o) {
                if (recommendProductInfo == undefined || recommendProductInfo == "") {
                    var data = '<div class="pop-car-win"><div class="pop-content">';
                    data += '<div class="pop-success no-products"><h4><b></b>娣诲姞鎴愬姛锛�</h4>';
                    data += '<div class="clearfix"><a name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_goshopping" href="javascript:void(0)" class="car-btn shopping-btn close l"><span>缁х画璐墿</span></a>';
                    data += '<a name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_gocart" href="javascript:cart.recommended.toShoppingCart();" class="car-btn account-btn close"><span>鍘昏喘鐗╄溅缁撶畻</span></a></div>';
                    data += "</div>";
                    data += "</div></div>";
                    recommendProductInfo = data
                }
                e.find(".content").html(recommendProductInfo);
                try {
                    runAnalyseExpo()
                } catch (e) {}
                if (sn.catalogId == "22001") {
                    e.find(".btn.close").attr("name", "bprd_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_gwctk_guanbi")
                } else {
                    e.find(".btn.close").attr("name", "item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_gwctk_guanbi")
                }
            }, overlayClick: true,
            overlayCss: {
                background: "black",
                opacity: "0.3"
            },
            fadeIn: 300,
            fadeOut: 300
        })
    };
    var toShoppingCart = function () {
        if (shoppingCartUrl == undefined || shoppingCartUrl == "") {
            var fourthURL = window.location.href;
            shoppingCartUrl = "http://" + sn.cartPath + "/OrderItemDisplay?langId=-7&storeId=" + sn.storeId + "&catalogId=" + sn.catalogId + "&returnURL=" + fourthURL
        }
        hrefLink(shoppingCartUrl)
    };
    var alsoBuy = function (cityId) {
        if (cityId == "undefined") {
            cityId = "-7"
        }
        var u = getCookie("custno");
        if (typeof (u) == "undefined") {
            u = ""
        }
        var c = getCookie("_snma");
        if (typeof (c) != "undefined" && null != c && c != "") {
            c = c.split("|")[1]
        } else {
            c = ""
        }
        var _url = sn.tuijianDomain + "/recommend-portal/recommendv2/biz.jsonp?u=" + u + "&c=" + c + "&parameter=" + firstCmmdty.cmmdtyCode + "&cityId=" + cityId + "&sceneIds=10-11&count=5";
        var catalogId = sn.catalogId;
        if (catalogId == "22001") {
            _url = sn.tuijianDomain + "/recommend-portal/recommendv2/biz.jsonp?u=" + u + "&c=" + c + "&parameter=" + firstCmmdty.cmmdtyCode + "&cityId=" + cityId + "&sceneIds=10-12&count=5"
        }
        $.ajax({
            url: _url,
            cache: true,
            dataType: "jsonp",
            jsonpCallback: "cart.recommended.recommendData",
            success: function () {}
        })
    };
    var recommendData = function (jsondata) {
        var sugGoodsList = jsondata.sugGoods;
        var bbData = "";
        var recomData = "";
        $.each(sugGoodsList, function (i, sugGoods) {
            if (sugGoods.resCode != "02") {
                if (sugGoods.sceneId == "10-11") {
                    recommendProductInit(sugGoods)
                } else {
                    if (sugGoods.sceneId == "10-12") {
                        recommendBookProductInit(sugGoods)
                    }
                }
            }
        })
    };
    var recommendProductInit = function (item) {
        var data = '<div class="pop-car-win"><div class="pop-content">';
        if (item.skus != undefined && item.skus.length >= 4) {
            data += '<div class="pop-success"><h4><b></b>娣诲姞鎴愬姛锛�</h4>';
            data += '<div class="clearfix"><a name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_goshopping" href="javascript:void(0)" class="car-btn shopping-btn close l"><span>缁х画璐墿</span></a>';
            data += '<a name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_gocart" href="javascript:cart.recommended.toShoppingCart();" class="car-btn account-btn close"><span>鍘昏喘鐗╄溅缁撶畻</span></a></div>';
            data += '<div class="pop-others"><p>涔颁簡璇ュ晢鍝佺殑椤惧杩樹拱浜�</p><ul>';
            for (var i = 0; i < 4; i++) {
                if (i == 3) {
                    data += '<li class="last">'
                } else {
                    data += "<li>"
                } if (typeof (item.skus[i].pictureUrl) != "undefined" && (item.skus[i].pictureUrl) != "") {
                    data += '<a id="baoguang_recbuymore_1-' + (i + 1) + "_" + item.skus[i].vendorId + "_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_" + item.skus[i].handwork + '" name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" href="' + sn.elecProductDomain + "/" + item.skus[i].vendorId + "/" + cart.common.dealPreZeroPartnum(item.skus[i].sugGoodsCode) + ".html?src=item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" title="' + item.skus[i].sugGoodsName + '" class="picbox" target="_blank"><img src="' + item.skus[i].pictureUrl + '_160w_160h_4e"" alt="' + item.skus[i].sugGoodsName + '" /></a>'
                } else {
                    data += '<a id="baoguang_recbuymore_1-' + (i + 1) + "_" + item.skus[i].vendorId + "_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_" + item.skus[i].handwork + '" name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" href="' + sn.elecProductDomain + "/" + item.skus[i].vendorId + "/" + cart.common.dealPreZeroPartnum(item.skus[i].sugGoodsCode) + ".html?src=item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" title="' + item.skus[i].sugGoodsName + '" class="picbox" target="_blank"><img src="' + sn.imageDomianDir + "/content/catentries/" + (item.skus[i].sugGoodsCode).substring(0, 14) + "/" + item.skus[i].sugGoodsCode + "/" + item.skus[i].sugGoodsCode + '_ls.jpg"" alt="' + item.skus[i].sugGoodsName + '" /></a>'
                }
                data += '<p id="baoguang_recbuymore_1-' + (i + 1) + "_" + item.skus[i].vendorId + "_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_" + item.skus[i].handwork + '" name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_c_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" class="details"><a href="' + sn.elecProductDomain + "/" + item.skus[i].vendorId + "/" + cart.common.dealPreZeroPartnum(item.skus[i].sugGoodsCode) + ".html?src=item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_c_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" title="' + item.skus[i].sugGoodsName + '" target="_blank">' + item.skus[i].sugGoodsName + "</a></p>";
                data += '<span class="snPrice"><i>楼</i><em>' + item.skus[i].price + "</em></span>";
                data += "</li>"
            }
            data += "</ul></div>"
        } else {
            data += '<div class="pop-success no-products"><h4><b></b>娣诲姞鎴愬姛锛�</h4>';
            data += '<div class="clearfix"><a name="item_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_goshopping" href="javascript:void(0)" class="car-btn shopping-btn close l"><span>缁х画璐墿</span></a>';
            data += '<a name="item_' + (firstCmmdty.cmmdtyCode) + '_gwctk_gocart" href="javascript:cart.recommended.toShoppingCart();" class="car-btn account-btn close"><span>鍘昏喘鐗╄溅缁撶畻</span></a></div>';
            data += "</div>"
        }
        data += "</div></div>";
        recommendProductInfo = data
    };
    var recommendBookProductInit = function (item) {
        var data = '<div class="pop-car-win"><div class="pop-content">';
        if (item.skus != undefined && item.skus.length >= 4) {
            data += '<div class="pop-success"><h4><b></b>娣诲姞鎴愬姛锛�</h4>';
            data += '<div class="clearfix"><a name="bprd_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_goshopping" href="javascript:void(0)" class="car-btn shopping-btn close l"><span>缁х画璐墿</span></a>';
            data += '<a name="bprd_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_gocart" href="javascript:cart.recommended.toShoppingCart();" class="car-btn account-btn close"><span>鍘昏喘鐗╄溅缁撶畻</span></a></div>';
            data += '<div class="pop-others"><p>涔颁簡璇ュ晢鍝佺殑椤惧杩樹拱浜�</p><ul>';
            for (var i = 0; i < 4; i++) {
                if (i == 3) {
                    data += '<li class="last">'
                } else {
                    data += "<li>"
                } if (typeof (item.skus[i].pictureUrl) != "undefined" && item.skus[i].pictureUrl != "") {
                    data += '<a id="baoguang_recbuymore_1-' + (i + 1) + "_" + item.skus[i].vendorId + "_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_" + item.skus[i].handwork + '" name="bprd_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" href="' + sn.elecProductDomain + "/" + item.skus[i].vendorId + "/" + cart.common.dealPreZeroPartnum(item.skus[i].sugGoodsCode) + ".html?src=item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" title="' + item.skus[i].sugGoodsName + '" class="picbox" target="_blank"><img src="' + item.skus[i].pictureUrl + '_160w_160h_4e"" alt="' + item.skus[i].sugGoodsName + '" /></a>'
                } else {
                    data += '<a id="baoguang_recbuymore_1-' + (i + 1) + "_" + item.skus[i].vendorId + "_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_" + item.skus[i].handwork + '" name="bprd_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" href="' + sn.elecProductDomain + "/" + item.skus[i].vendorId + "/" + cart.common.dealPreZeroPartnum(item.skus[i].sugGoodsCode) + ".html?src=item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_p_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" title="' + item.skus[i].sugGoodsName + '" class="picbox" target="_blank"><img src="' + sn.imageDomianDir + "/content/catentries/" + (item.skus[i].sugGoodsCode).substring(0, 14) + "/" + item.skus[i].sugGoodsCode + "/" + item.skus[i].sugGoodsCode + '_ls.jpg"" alt="' + item.skus[i].sugGoodsName + '" /></a>'
                }
                data += '<p id="baoguang_recbuymore_1-' + (i + 1) + "_" + item.skus[i].vendorId + "_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_" + item.skus[i].handwork + '" name="bprd_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_c_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" class="details"><a href="' + sn.elecProductDomain + "/" + item.skus[i].vendorId + "/" + cart.common.dealPreZeroPartnum(item.skus[i].sugGoodsCode) + ".html?src=item_" + (firstCmmdty.cmmdtyCode).substring(9, 18) + "_recbuymore_1-" + (i + 1) + "_c_" + item.skus[i].vendorId + "_" + (item.skus[i].sugGoodsCode).substring(9, 18) + "_" + item.skus[i].handwork + '" title="' + item.skus[i].sugGoodsName + '" target="_blank">' + item.skus[i].sugGoodsName + "</a></p>";
                data += '<span class="snPrice"><i>楼</i><em>' + item.skus[i].price + "</em></span>";
                data += "</li>"
            }
            data += "</ul></div>"
        } else {
            data += '<div class="pop-success no-products"><h4><b></b>娣诲姞鎴愬姛锛�</h4>';
            data += '<div class="clearfix"><a name="bprd_' + (firstCmmdty.cmmdtyCode).substring(9, 18) + '_gwctk_goshopping" href="javascript:void(0)" class="car-btn shopping-btn close l"><span>缁х画璐墿</span></a>';
            data += '<a name="bprd_' + (firstCmmdty.cmmdtyCode) + '_gwctk_gocart" href="javascript:cart.recommended.toShoppingCart();" class="car-btn account-btn close"><span>鍘昏喘鐗╄溅缁撶畻</span></a></div>';
            data += "</div>"
        }
        data += "</div></div>";
        recommendProductInfo = data
    };
    return {
        shoppingCartPopBox: shoppingCartPopBox,
        toShoppingCart: toShoppingCart,
        alsoBuy: alsoBuy
    }
})(jQuery);
$(function () {
    if (!cart.common.isInclude("jquery", true)) {
        alert("璇峰紩鍏Query.js")
    }
    $("script").each(function () {
        if ($(this).attr("src") != undefined && $(this).attr("src").indexOf("cart.js") != -1) {
            if ($(this).attr("src").lastIndexOf("?") <= 0) {
                version = ""
            } else {
                version = $(this).attr("src").substring($(this).attr("src").lastIndexOf("?"))
            }
            return false
        }
    });
    if (typeof (bd) == "undefined" || bd == "undefined") {
        var scriptDetect = document.createElement("script");
        scriptDetect.type = "text/javascript";
        scriptDetect.src = "//mmds.suning.com/mmds/mmds.js" + version;
        var _scripts = document.getElementsByTagName("script");
        var _s = _scripts[0];
        _s.parentNode.insertBefore(scriptDetect, _s);
        if (!/msie/i.test(navigator.userAgent.toLowerCase())) {
            scriptDetect.onload = function () {
                try {
                    if (typeof (bd) != "undefined") {
                        bd.init({
                            appCode: "snCart",
                            env: "prd"
                        })
                    }
                } catch (e) {}
            }
        } else {
            scriptDetect.onreadystatechange = function () {
                var r = scriptDetect.readyState;
                if (r === "loaded" || r === "complete") {
                    scriptDetect.onreadystatechange = null;
                    if (typeof (bd) != "undefined") {
                        try {
                            bd.init({
                                appCode: "snCart",
                                env: "prd"
                            })
                        } catch (e) {}
                    }
                }
            }
        }
    } else {
        var dtstr = bd.rst({
            scene: "3"
        });
        if (dtstr.length < 50) {
            try {
                bd.init({
                    appCode: "snCart",
                    env: "prd"
                })
            } catch (e) {}
        }
    } if (typeof ($.mDialog) == "undefined") {
        cart.common._loadAsyncJs("//res.suning.cn/project/ccf/js/SFE.dialog.js" + version)
    }
    if (typeof (_dfp) == "undefined" || _dfp == "undefined") {
        cart.common._loadAsyncJs("//dfp.suning.com/dfprs-collect/dist/fp.js")
    }
    if (typeof (siller) == "undefined" || siller == "undefined") {
        cart.common._loadAsyncJs("//dt.suning.com//detect/dt/siller.js")
    }
    if (typeof (SnCaptcha) == "undefined" || SnCaptcha == "undefined") {
        cart.common._loadAsyncJs("//iar-web.suning.com/iar-web/snstatic/SnCaptcha.js")
    }
    cart.common._loadAsyncJs(cart.common.getScriptDomain() + "??/javascript/sn_da/da_opt.js,/javascript/sn_da/sa-analytics.js" + version);
    cart.common._loadAsyncJs("//res.suning.cn/project/??/tspofc/js/fcPop.js,/ccf/js/fourth-nostore-rd.js,/ccf/js/addCartUtil.js,/ccf/js/cloudCart.js,/ccf/js/SFE.lion.dialog.js" + version);
    if (typeof ($.fn.SnAddress) != "function") {
        cart.common._loadAsyncJs("//res.suning.cn/project/ccf/js/New.CitySelect.min.js" + version)
    }
    if (typeof ECity != "object") {
        cart.common._loadAsyncJs("//res.suning.cn/project/ip-web/SFE.city.js" + version)
    }
    cart.common._loadSillerCss();
    if (typeof (_dfp) != "undefined" && _dfp != "undefined") {
        _dfp.getToken(function (token) {
            dfpToken_str = token
        })
    } else {
        setTimeout(function () {
            if (typeof (_dfp) != "undefined" && _dfp != "undefined") {
                _dfp.getToken(function (token) {
                    dfpToken_str = token
                })
            }
        }, 1000)
    }
    try {
        sa.openAPI = sa.openAPI || {};
        sa.initTrackerConfig();
        cart.analytics.clickSendData()
    } catch (e) {}
});
cart.toCartCallback = (function ($) {
    var operateType = "",
        data = "",
        callback = "",
        httpSwitch = "";
    var setOperateType = function (_operateType) {
        operateType = _operateType
    };
    var getOperateType = function () {
        return operateType
    };
    var setData = function (_data) {
        data = _data
    };
    var getData = function () {
        return data
    };
    var setCallback = function (_callback) {
        callback = _callback
    };
    var getCallback = function () {
        return callback
    };
    var setHttpSwitch = function (_httpSwitch) {
        httpSwitch = _httpSwitch
    };
    var getHttpSwitch = function () {
        return httpSwitch
    };
    return {
        setOperateType: setOperateType,
        getOperateType: getOperateType,
        setData: setData,
        getData: getData,
        setCallback: setCallback,
        getCallback: getCallback,
        setHttpSwitch: setHttpSwitch,
        getHttpSwitch: getHttpSwitch
    }
})(jQuery);
var mySuning = mySuning || {
    mySuningFavoriteNoticePartnumber: null,
    mySuningFavoriteNoticeShopId: null,
    mySuningFavoriteNoticeEntrace: null
};
var esjs = document.getElementsByTagName("script");
var escss = document.getElementsByTagName("link");
var version;
var lesCityCode = $("#lesCityCode").val();
var lesProviceId = $("#lesProviceId").val();
var lesDistributeCode = $("#lesDistributeCode").val();
var icpsUrl = "//icps.suning.com/icps-web/getVarnishAllPrice014";

function isInclude(a, c) {
    if (c) {
        for (var b = 0; b < esjs.length; b++) {
            if (esjs[b][c ? "src" : "href"].indexOf(a) != -1) {
                return true
            }
        }
        return false
    } else {
        for (var b = 0; b < escss.length; b++) {
            if (escss[b][c ? "src" : "href"].indexOf(a) != -1) {
                return true
            }
        }
        return false
    }
}
$(document).ready(function () {
    if (!isInclude("jquery", true)) {
        alert("璇峰紩鍏Query.js")
    }
    $("script").each(function () {
        if ($(this).attr("src") != null && typeof ($(this).attr("src")) != undefined && $(this).attr("src") != undefined && $(this).attr("src").indexOf("favorite-api") != -1) {
            if ($(this).attr("src").indexOf("?") <= 0) {
                version = ""
            } else {
                version = $(this).attr("src").substring($(this).attr("src").indexOf("?"))
            }
            return false
        }
    });
    if (!isInclude("passport", true)) {
        var c = '<script>var passport_config = { base: "//favorite.suning.com/", loginTheme: "b2c_pop" };<\/script>';
        $("title").after(c);
        var a = document.createElement("script");
        a.src = "https://res.suning.cn/project/passport/js/passport.min.js";
        a.type = "text/javascript";
        var b = document.getElementsByTagName("head")[0];
        b.appendChild(a)
    }
    var d = window.location.protocol;
    if (!isInclude("SFE.dialog", true)) {
        var a = document.createElement("script");
        if (d == "http:") {
            a.src = "http://res.suning.cn/project/myfavorite/js/SFE.dialog.js"
        } else {
            a.src = "https://sslres.suning.com/project/myfavorite/js/SFE.dialog.js"
        }
        a.type = "text/javascript";
        var b = document.getElementsByTagName("head")[0];
        b.appendChild(a)
    }
    if (!isInclude("jquery.cookie", true)) {
        var a = document.createElement("script");
        if (d == "http:") {
            a.src = "http://res.suning.cn/project/myfavorite/js/jquery.cookie.min.js"
        } else {
            a.src = "https://sslres.suning.com/project/myfavorite/js/jquery.cookie.min.js"
        }
        a.type = "text/javascript";
        var b = document.getElementsByTagName("head")[0];
        b.appendChild(a)
    }
});

function checkAndoridNofity() {
    baseApi.checkNotifyStatus(function (a) {
        return "" + a
    })
}
mySuning.requestDialog = function (a, b) {
    $.ajax({
        url: a + b,
        type: "GET",
        dataType: "script",
        async: false,
        cache: false
    })
};

function favoriteCallback(a) {
    $.mDialog({
        css: {
            width: "450px"
        },
        http: function (b, c) {
            b.find(".content").html(a.htmlDom)
        }, overlayCss: {
            background: "black ",
            opacity: "0.3"
        }, title: "娓╅Θ鎻愮ず"
    });
    $.mDialog({
        css: {
            width: "450px"
        },
        message: $(".dialog-addfavor"),
        overlayCss: {
            background: "black",
            opacity: "0.3"
        },
        overlayClick: true,
        fadeIn: 300,
        fadeOut: 300
    })
}

function fiftyCallBack(a) {
    $.mDialog({
        css: {
            width: "450px"
        },
        http: function (b, c) {
            b.find(".content").html(a.htmlDom);
            mySuning.getRecommendedData("1-2", globalPartNumber, "mySuning.myRecommedData");
            $("#noticeDiv").css("display", "none");
            $(".netuser-showWin-title").css("display", "block");
            $("#tipmessage").css("display", "none");
            if (noticeType == "priceDown") {
                $(".netuser-showWin-title").html("<h3>鎮ㄥ凡璁㈤槄婊�50娆＄殑闄嶄环閫氱煡</h3>")
            } else {
                if (noticeType == "arrival") {
                    $(".netuser-showWin-title").html("<h3>鎮ㄥ凡璁㈤槄婊�50娆＄殑鍒拌揣閫氱煡</h3>")
                }
            }
        }, overlayCss: {
            background: "black ",
            opacity: "0.3"
        }, title: "娓╅Θ鎻愮ず"
    })
}

function twoCallBack(a) {
    $.mDialog({
        css: {
            width: "450px"
        },
        http: function (b, c) {
            b.find(".content").html(a.htmlDom);
            mySuning.getRecommendedData("1-2", globalPartNumber, "mySuning.myRecommedData");
            $("#noticeDiv").css("display", "none");
            $(".netuser-showWin-title").css("display", "block");
            $("#tipmessage").css("display", "none");
            if (noticeType == "priceDown") {
                $(".netuser-showWin-title").html("<h3>鎮ㄥ凡璁㈤槄杩囪鍟嗗搧鐨勯檷浠烽€氱煡</h3>")
            } else {
                if (noticeType == "arrival") {
                    $(".netuser-showWin-title").html("<h3>鎮ㄥ凡璁㈤槄杩囪鍟嗗搧鐨勫埌璐ч€氱煡</h3>")
                }
            }
        }, overlayCss: {
            background: "black ",
            opacity: "0.3"
        }, title: "娓╅Θ鎻愮ず"
    })
}

function noticeCallBack(a) {
    $.mDialog({
        css: {
            width: "470px"
        },
        http: function (c, f) {
            c.find(".content").html(a.htmlDom);
            var b = $("#fMobileNumberWhole").val();
            var d = desensitization(b);
            $("#fMobileNumber").val(d);
            if (noticeType == "priceDown") {
                $("#expectPrice").val(parseInt(globalPartPrice));
                if (globalEntrance == "myFavorite" || globalEntrance == "myFavoritePic" || globalEntrance == "myFavoritePicNew") {
                    $("#isFavoriteAdd").css("display", "none")
                }
                $(".exOrder-show-win").css("display", "none")
            } else {
                if (noticeType == "arrival") {
                    if (globalEntrance == "myFavorite" || globalEntrance == "myFavoritePic" || globalEntrance == "myFavoritePicNew") {
                        $("#isFavoriteAdd").css("display", "none")
                    } else {
                        $("#check-addfav").attr("checked", "checked")
                    }
                    $("#arrival_text").css("display", "block");
                    $("#priceLi").css("display", "none");
                    $(".exOrder-show-win").css("display", "none")
                }
            }
        }, overlayCss: {
            background: "black ",
            opacity: "0.3"
        }, title: titleName
    })
}
mySuning.doSuccess = function (c, d, h, f, a, e) {
    var g = c;
    if (g.returnCode == 0) {
        if (d == "product") {
            var b = "//favorite.suning.com/ajax/productFavoriteSuccessLayer.do?partnumber=" + h + "&shopId=" + f + "&callback=";
            mySuning.requestDialog(b, "favoriteCallback");
            if (e) {
                $("#spsc_cksc").attr("name", e + "_spsc_cksc");
                $("#spsc_bjbq").attr("name", e + "_spsc_bjbq")
            }
        } else {
            if (d == "shop") {
                var b = "//favorite.suning.com/ajax/shopFavoriteSuccessLayer.do?shopId=" + f + "&entrance=" + a + "&callback=";
                mySuning.requestDialog(b, "favoriteCallback");
                if (e) {
                    $("#dpsc_cksc").attr("name", e + "_dpsc_cksc");
                    $("#dpsc_bjbq").attr("name", e + "_dpsc_bjbq")
                }
            }
        }
    } else {
        if (g.returnCode == 1) {
            if (d == "product") {
                var b = "//favorite.suning.com/ajax/productFavoritedLayer.do?partnumber=" + h + "&shopId=" + f + "&callback=";
                mySuning.requestDialog(b, "favoriteCallback");
                if (e) {
                    $("#spsc_cksc").attr("name", e + "_spsc_cksc");
                    $("#spsc_bjbq").attr("name", e + "_spsc_bjbq")
                }
            } else {
                if (d == "shop") {
                    var b = "//favorite.suning.com/ajax/shopFavoritedLayer.do?shopId=" + f + "&entrance=" + a + "&callback=";
                    mySuning.requestDialog(b, "favoriteCallback");
                    if (e) {
                        $("#dpsc_cksc").attr("name", e + "_dpsc_cksc");
                        $("#dpsc_bjbq").attr("name", e + "_dpsc_bjbq")
                    }
                }
            }
        } else {
            if (d == "product" && g.returnCode == 10001) {
                mySuning.submitFavoriteSaMessageV2("mf-good-second-category-name-05")
            }
            var b = "//favorite.suning.com/ajax/" + d + "FavoriteFailLayer.do?entrance=" + a + "&callback=";
            mySuning.requestDialog(b, "favoriteCallback")
        }
    }
};
mySuning.doGET = function (b, c, g, e, a, d) {
    $.ajax({
        type: "GET",
        async: false,
        url: b,
        dataType: "jsonp",
        jsonpCallback: "myCallback",
        success: function f(h) {
            mySuning.doSuccess(h, c, g, e, a, d)
        }
    })
};
mySuning.doJsonpGET = function (a, b) {
    $.ajax({
        type: "GET",
        async: false,
        url: a,
        dataType: "jsonp",
        jsonpCallback: b
    })
};
mySuning.add2ProductFavorite = function (k, i, c, j, d, f, g, e) {
    globalEntrance = c;
    globalShopId = i;
    ajaxUrl = window.location.href;
    var a = /^[0-9]{18}$/;
    var h = /^[0-9]{10}$/;
    var b;
    if (!(a.test(k) && h.test(i))) {
        alert("浼犲叆鍙傛暟涓嶆纭�");
        return
    }
    if ("shoppingCart1shopping" == c) {
        b = "https://favorite.suning.com/ajax/addProductFavorite.do?partnumber=" + k + "&shopId=" + i + "&entrance=" + c
    } else {
        if ("shoppingCart1" == c) {
            b = "https://favorite.suning.com/ajax/addProductFavorite.do?partnumber=" + k + "&shopId=" + i + "&entrance=" + c
        } else {
            b = "//favorite.suning.com/ajax/addProductFavorite.do?partnumber=" + k + "&shopId=" + i + "&entrance=" + c
        }
    } if (f !== null && f !== undefined && f !== "") {
        b = b + "&pdType=" + f
    }
    if (g !== null && g !== undefined && g !== "") {
        b = b + "&shoptType=" + g
    }
    probeAuthStatus(function () {
        if (j) {
            mySuning.doJsonpGET(b, j)
        } else {
            mySuning.doGET(b, "product", k, i, d)
        }
    }, function () {
        ensureLogin(function () {
            mySuning.add2ProductFavorite(k, i, c, j, d, f, g, e);
            if (typeof e == "function") {
                e()
            }
        })
    })
};
mySuning.add2ShopFavorite = function (e, a, d, b) {
    globalEntrance = a;
    var c = /^[0-9]{10}$/;
    if (!c.test(e)) {
        alert("浼犲叆鍙傛暟涓嶆纭�");
        return
    }
    url = "//favorite.suning.com/ajax/addShopFavorite.do?shopId=" + e + "&entrance=" + a;
    probeAuthStatus(function () {
        mySuning.doGET(url, "shop", "", e, a, d)
    }, function () {
        ensureLogin(function () {
            mySuning.add2ShopFavorite(e, a, d, b);
            if (typeof b == "function") {
                b()
            }
        })
    })
};
var tel = /^[a-zA-Z0-9_\u4e00-\u9fa5]{0,10}$/;
mySuning.addTag = function (b, a) {
    var d = encodeURI(b);
    $.ajax({
        type: "GET",
        async: false,
        url: d,
        dataType: "jsonp",
        jsonpCallback: "myCallback",
        success: function c(e) {
            var f = e;
            if (f.returnCode == 0) {
                a.find("#btns").css("display", "none");
                a.find("#ok").css("display", "block");
                setTimeout(function () {
                    $.unmDialog()
                }, 2000)
            } else {
                if (f.returnCode = 1) {
                    a.find("#error").css("display", "block")
                } else {
                    if (f.returnCode = -2) {
                        a.find("#notRight").css("display", "block")
                    }
                }
            }
        }
    })
};
mySuning.addTag1 = function (b, a) {
    var d = encodeURI(b);
    $.ajax({
        type: "GET",
        async: false,
        url: d,
        dataType: "jsonp",
        jsonpCallback: "myCallback",
        success: function c(e) {
            var f = e;
            if (f.returnCode == 0) {
                a.find(".add-sign").find("a").remove();
                a.find(".error-ok").css("display", "block");
                setTimeout(function () {
                    $.unmDialog()
                }, 2000)
            } else {
                if (f.returnCode = 1) {
                    a.find(".error-msg").html("娣诲姞鏍囩澶辫触锛�");
                    a.find(".error-msg").css("display", "block");
                    a.find("a").prev().addClass("error-tbx")
                } else {
                    if (f.returnCode = -2) {
                        a.find(".error-msg").html("鏍囩搴斾负10涓互鍐呯殑涓枃銆佹暟瀛椼€佸瓧姣嶆垨涓嬪垝绾匡紒");
                        a.find(".error-msg").css("display", "block");
                        a.find("a").prev().addClass("error-tbx")
                    }
                }
            }
        }
    })
};
mySuning.productFavoriteAndTag = function (c) {
    var f = $(c).parent().parent();
    f.find("#error").css("display", "none");
    var i = f.parent().find("input");
    var b = i.attr("id");
    var e = f.find("i");
    var h = $(c).parent().find(".partnumber").attr("id");
    var g = $(c).parent().find(".shopId").attr("id");
    var d = "notOpen";
    if (typeof (i.val()) == undefined || i.val() == "" || i.val() == null) {
        return
    } else {
        if (tel.test(i.val())) {
            f.find("#notRight").css("display", "none");
            f.find("#error").css("display", "none");
            var a = "//favorite.suning.com/ajax/addProductTag.do?partnumber=" + h + "&shopId=" + g + "&open=" + d + "&productTagName=" + i.val() + "&oldTagName=" + b;
            ensureLogin(function () {
                mySuning.addTag(a, f)
            })
        } else {
            f.find("#notRight").css("display", "block");
            return
        }
    }
};
mySuning.productFavoriteAndTag1 = function (g) {
    var e = $(g).parent().parent();
    var a = $(g).prev();
    if (a.val() == "鎮ㄨ繕鍙互鑷畾涔夋爣绛� (10瀛椾互鍐�)") {
        return
    } else {
        var d = a.attr("id");
        var h = $(g).parent().find(".partnumber").attr("id");
        var f = $(g).parent().find(".shopId").attr("id");
        var c = "notOpen";
        if (typeof (a.val()) == undefined || a.val() == "" || a.val() == null) {
            return
        } else {
            if (tel.test(a.val())) {
                var b = "//favorite.suning.com/ajax/addProductTag.do?partnumber=" + h + "&shopId=" + f + "&open=" + c + "&productTagName=" + a.val() + "&oldTagName=" + d;
                probeAuthStatus(function () {
                    mySuning.addTag1(b, e)
                }, function () {
                    ensureLogin(function () {
                        mySuning.addTag1(b, e)
                    })
                })
            } else {
                e.find(".error-msg").html("鏍囩搴斾负10涓互鍐呯殑涓枃銆佹暟瀛椼€佸瓧姣嶆垨涓嬪垝绾匡紒");
                e.find(".error-msg").css("display", "block");
                a.addClass("error-tbx");
                return
            }
        }
    }
};
mySuning.shopFavoriteAndTag = function (g) {
    var e = $(g).parent().parent();
    e.find("#error").css("display", "none");
    var a = e.parent().find("input");
    var d = a.attr("id");
    var c = e.find("i");
    var f = $(g).parent().find(".shopId").attr("id");
    if (typeof (a.val()) == undefined || a.val() == "" || a.val() == null) {
        return
    } else {
        if (tel.test(a.val())) {
            e.find("#notRight").css("display", "none");
            e.find("#error").css("display", "none");
            var b = "//favorite.suning.com/ajax/addShopTag.do?&shopId=" + f + "&shopTagName=" + a.val();
            ensureLogin(function () {
                mySuning.addTag(b, e)
            })
        } else {
            e.find("#notRight").css("display", "block");
            return
        }
    }
};
mySuning.shopFavoriteAndTag1 = function (f) {
    var d = $(f).parent().parent();
    var a = $(f).prev();
    if (a.val() == "鎮ㄨ繕鍙互鑷畾涔夋爣绛� (10瀛椾互鍐�)") {
        return
    } else {
        var c = a.attr("id");
        var e = $(f).parent().find(".shopId").attr("id");
        if (typeof (a.val()) == undefined || a.val() == "" || a.val() == null) {
            return
        } else {
            if (tel.test(a.val())) {
                var b = "//favorite.suning.com/ajax/addShopTag.do?&shopId=" + e + "&shopTagName=" + a.val() + "&oldTagName=" + c;
                probeAuthStatus(function () {
                    mySuning.addTag1(b, d)
                }, function () {
                    ensureLogin(function () {
                        mySuning.addTag1(b, d)
                    })
                })
            } else {
                d.find(".error-msg").html("鏍囩搴斾负10涓互鍐呯殑涓枃銆佹暟瀛椼€佸瓧姣嶆垨涓嬪垝绾匡紒");
                d.find(".error-msg").css("display", "block");
                a.addClass("error-tbx");
                return
            }
        }
    }
};
mySuning.onerr = function (a, b) {
    a.css("display", "block");
    a.html("<i></i><label>" + b + "</label>")
};
mySuning.validatePrice = function (b, c) {
    var a = /^[1-9]\d*$/;
    var d = c.val();
    if (d == undefined || d == "") {
        mySuning.onerr(b, "鏈熸湜浠锋牸涓嶈兘涓虹┖");
        $("#expectPrice").css("border-color", "#ff0000");
        return false
    } else {
        if (!a.test(d)) {
            mySuning.onerr(b, "鏈熸湜浠锋牸蹇呴』鏄鏁�");
            return false
        }
        if (Number(d) > Number(globalPartPrice)) {
            mySuning.onerr(b, "鏈熸湜浠锋牸涓嶈兘楂樹簬鍘熶环");
            return false
        } else {
            return true
        }
    }
    return true
};
mySuning.validateMobile = function (f, a) {
    var e = /^1\d{10}$/;
    var d = a.val();
    var c = $("#email").val();
    if ((d == undefined || d == "") && (c == undefined || c == "")) {
        $("#emailMobileErr").css("display", "block");
        return false
    } else {
        if (d.length > 0) {
            var b = $("#fMobileNumberWhole").val();
            if (desensitization(b) != d) {
                if (d.length != 11 || !e.test(d)) {
                    $("#emailMobileErr").css("display", "none");
                    mySuning.onerr(f, "鎵嬫満鍙风爜杈撳叆鏍煎紡閿欒");
                    return false
                }
            }
            return true
        } else {
            return true
        }
    }
};
mySuning.validateEmail = function (e, a) {
    var d = /^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$/;
    var c = a.val();
    var b = $("#fMobileNumber").val();
    if ((c == undefined || c == "") && (b == undefined || b == "")) {
        $("#emailMobileErr").css("display", "block");
        return false
    } else {
        if (c.length > 0) {
            if (c.length > 50 || !d.test(c)) {
                if (c.match(/(\s+)/) && c.match(/@/) && c.match(/\./)) {
                    $("#emailMobileErr").css("display", "none");
                    mySuning.onerr(e, "閭涓嶈兘鍖呭惈绌烘牸锛�")
                } else {
                    mySuning.onerr(e, "閭鍦板潃杈撳叆鏍煎紡閿欒");
                    $("#emailMobileErr").css("display", "none")
                }
                return false
            }
            return true
        } else {
            return true
        }
    }
};
mySuning.fcus = function (b, a) {
    b.css("display", "none");
    if (null != a) {
        a.css("display", "none")
    }
    if ("error1" != b.attr("id") && $("#errorMobile").css("display") == "none" && $("#error2").css("display") == "none") {
        $("#emailMobileErr").css("display", "block")
    }
};
mySuning.clickNotice = function (c, b) {
    var a;
    if (noticeType == "priceDown") {
        a = "//favorite.suning.com/ajax/fourPage/checkCountPrice.do"
    } else {
        if (noticeType == "arrival") {
            a = "//favorite.suning.com/ajax/fourPage/checkCountArrival.do"
        }
    }
    ensureLogin(function () {
        $.ajax({
            type: "GET",
            async: false,
            url: a + "?partnumber=" + c + "&shopId=" + b,
            dataType: "jsonp",
            jsonpCallback: "myCallbacknotice",
            success: function d(f) {
                var g = f.bookFlag;
                var e;
                if (g == 2) {
                    e = "//favorite.suning.com/ajax/fourPage/clickAlertPrice.do?callback=", mySuning.requestDialog(e, "fiftyCallBack")
                } else {
                    if (g == 1) {
                        e = "//favorite.suning.com/ajax/fourPage/clickAlertPrice.do?partnumber=" + globalPartNumber + "&shopId=" + globalShopId + "&entrance=" + globalEntrance + "&callback=", mySuning.requestDialog(e, "twoCallBack")
                    } else {
                        if (g == 0) {
                            thisMfCityId = f.cityId;
                            if (noticeType == "priceDown") {
                                titleName = "闄嶄环閫氱煡"
                            } else {
                                if (noticeType == "arrival") {
                                    titleName = "鍒拌揣閫氱煡"
                                } else {
                                    titleName = "娓╅Θ鎻愮ず"
                                }
                            }
                            var h;
                            h = "//favorite.suning.com/ajax/fourPage/clickAlertPrice.do";
                            e = h + "?partnumber=" + globalPartNumber + "&shopId=" + globalShopId + "&entrance=" + globalEntrance + "&callback=", mySuning.requestDialog(e, "noticeCallBack")
                        }
                    }
                }
            }
        })
    })
};
mySuning.myClickPrice = function (g, d, f, b, e, a) {
    var c = mySuning.validatePrice(g, d);
    var b = mySuning.validateEmail(f, b);
    var a = mySuning.validateMobile(e, a);
    if (noticeType == "priceDown") {
        if (c && b && a) {
            mySuning.fromSubmit()
        }
    } else {
        if (b && a) {
            mySuning.fromSubmit()
        }
    }
};
mySuning.myClickArrival = function (b, a) {
    var a = mySuning.validateEmail(b, a);
    if (a && cityflag) {
        mySuning.fromSubmit($(" #arrivalEmail"))
    }
};
mySuning.fromSubmit = function () {
    var i = $(" #email");
    var g = $(" #expectPrice");
    var e = $("#fMobileNumber").val();
    var a = $("#fMobileNumberWhole").val();
    var c = a;
    if (desensitization(a) != e) {
        c = e
    }
    var f = "";
    if (noticeType == "priceDown") {
        f = g.val()
    }
    var d;
    var h = i.val();
    if (globalEntrance == "myFavorite" || globalEntrance == "myFavoritePic" || globalEntrance == "myFavoritePicNew") {
        d = false
    } else {
        if ($("#check-addfav").attr("checked") == "checked") {
            d = true
        } else {
            d = false
        }
    }
    var b;
    if (noticeType == "priceDown") {
        b = "//favorite.suning.com/ajax/myFavorite/addProductPriceNotice.do?expectedPrice=" + f + "&price=" + globalPartPrice + "&email=" + h + "&mobilePhone=" + c
    } else {
        if (noticeType == "arrival") {
            b = "//favorite.suning.com/ajax/myFavorite/addProductArrivalNotice.do?email=" + h + "&mobilePhone=" + c
        }
    }
    probeAuthStatus(function () {
        if (noticeType == "arrival") {
            try {
                if (window.SNNativeClient) {
                    if (window.SNNativeClient.appNotificationStatus) {
                        window.SNNativeClient.appNotificationStatus(1)
                    }
                }
            } catch (k) {}
        }
        $.ajax({
            type: "GET",
            url: b + "&&partnumber=" + globalPartNumber + "&&shopId=" + globalShopId + "&entrance=" + globalEntrance + "&pdType=" + globalPdType + "&shoptType=" + globalShoptType,
            dataType: "jsonp",
            jsonpCallback: "myCallbacknotice",
            success: function j(l) {
                if (l.returnCode == -1) {
                    $.unmDialog();
                    ensureLogin(function () {})
                } else {
                    var m = l.returnMsg;
                    if (m == undefined || m == "") {
                        if (d) {
                            mySuning.mySuningFavoriteNoticePartnumber = globalPartNumber;
                            mySuning.mySuningFavoriteNoticeShopId = globalShopId;
                            mySuning.mySuningFavoriteNoticeEntrace = globalEntrance;
                            mySuning.add2ProductFavorite(globalPartNumber, globalShopId, globalEntrance, "mySuningFavoriteShowNoticesSuccessCallback", "", globalPdType, globalShoptType, "")
                        } else {
                            mySuning.showNoticeSuccess(globalPartNumber, globalShopId, "'" + globalEntrance + "'", f)
                        }
                    } else {
                        mySuning.onerr($("#messagePrice"), m)
                    }
                }
            }, error: function () {
                if (noticeType == "priceDown") {
                    mySuning.submitFavoriteSaMessageV2("mf-pcproductarrivenotice-2_error");
                    mySuning.onerr($("#messagePrice"), "绯荤粺寮傚父")
                } else {
                    if (noticeType == "arrival") {
                        mySuning.submitFavoriteSaMessageV2("mf-pcproductdownpricenotice-2_error");
                        mySuning.onerr($("#messageArrival"), "绯荤粺寮傚父")
                    }
                }
            }
        })
    }, function () {
        if (noticeType == "arrival") {
            mySuning.submitFavoriteSaMessageV2("mf-arrival-1error")
        } else {
            if (noticeType == "priceDown") {
                mySuning.submitFavoriteSaMessageV2("mf-priceDown-2error")
            }
        }
        $.unmDialog();
        ensureLogin(function () {})
    })
};
mySuningFavoriteShowNoticesSuccessCallback = function () {
    mySuning.showNoticeSuccess(mySuning.mySuningFavoriteNoticePartnumber, mySuning.mySuningFavoriteNoticeShopId, "'" + mySuning.mySuningFavoriteNoticeEntrace + "'", "");
    mySuning.mySuningFavoriteNoticePartnumber = null;
    mySuning.mySuningFavoriteNoticeShopId = null;
    mySuning.mySuningFavoriteNoticeEntrace = null
};
mySuning.showNoticeSuccess = function (b, a, c, d) {
    mySuning.getRecommendedData("1-2", b, "mySuning.myRecommedData");
    $("#noticeDiv").css("display", "none");
    $("#noticeSuccess").css("display", "block");
    if (noticeType == "priceDown") {
        $(".netuser-showWin-title").html("<h3>鍟嗗搧璁㈤槄闄嶄环閫氱煡鎴愬姛</h3>");
        $("#tipmessage").html("鍟嗗搧涓€鏃﹀湪30鏃ュ唴闄嶄环锛屾垜浠皢浼氱涓€鏃堕棿閫氱煡鎮紝璇峰強鏃跺叧娉ㄥ摝锛�");
        if (c == "'myFavorite'" && d != "") {
            var e = $("#prod" + b + "_" + a + "_" + lesProviceId + "_" + lesCityCode + "_" + lesDistributeCode).find("#refreshPriceDown");
            e.attr("title", "璁㈤槄浠仿�" + d + ".00");
            e.html("宸茶闃�")
        }
    } else {
        if (noticeType == "arrival") {
            $(".netuser-showWin-title").html("<h3>鍟嗗搧璁㈤槄鍒拌揣閫氱煡鎴愬姛</h3>");
            $("#tipmessage").html("");
            if (c == "'myFavorite'") {
                var e = $("#prod" + b + "_" + a + "_" + lesProviceId + "_" + lesCityCode + "_" + lesDistributeCode).find(".prod-edit .btn");
                e.html("宸茶闃�");
                e.attr("title", "宸茶闃呭埌璐ч€氱煡");
                e.attr("href", "javascript:void(0);");
                e.attr("style", "color:#999;cursor:default;text-decoration:none;")
            }
            if (c == "'myFavoritePic'") {
                var e = $("#prod" + b + "_" + a + "_" + lesProviceId + "_" + lesCityCode + "_" + lesDistributeCode).find(".cost-pic a");
                e.html("宸茶闃�");
                e.attr("title", "宸茶闃呭埌璐ч€氱煡");
                e.attr("href", "javascript:void(0);");
                e.attr("style", "color:#999;cursor:default;text-decoration:none;")
            }
            if (c == "'myFavoritePicNew'") {
                var e = $("#prod" + b + "_" + a + "_" + lesProviceId + "_" + lesCityCode + "_" + lesDistributeCode).find("#refreshArrivalNotice" + b + a);
                e.html("宸茶闃呭埌璐ч€氱煡");
                e.attr("title", "宸茶闃呭埌璐ч€氱煡");
                e.attr("href", "javascript:void(0);");
                e.attr("style", "color:#999;cursor:default;text-decoration:none;")
            }
        }
    }
};
mySuning.subscribePriceNotice = function (g, e, b, a, f, c, d) {
    noticeType = "priceDown";
    globalPartPrice = b;
    globalPartNumber = g;
    globalShopId = e;
    globalEntrance = a;
    if (f == null || f == undefined) {
        globalPdType = "0"
    } else {
        globalPdType = f
    } if (c == null || c == undefined) {
        globalShoptType = "N"
    } else {
        globalShoptType = c
    }
    ajaxUrl = window.location.href;
    ensureLogin(function () {
        mySuning.clickNotice(g, e);
        if (typeof d == "function") {
            d()
        }
    })
};
mySuning.subscribeArrivalNotice = function (f, d, a, e, b, c) {
    noticeType = "arrival";
    globalPartNumber = f;
    globalShopId = d;
    globalEntrance = a;
    if (e == null || e == undefined) {
        globalPdType = "0"
    } else {
        globalPdType = e
    } if (b == null || b == undefined) {
        globalShoptType = "N"
    } else {
        globalShoptType = b
    }
    ajaxUrl = window.location.href;
    ensureLogin(function () {
        mySuning.clickNotice(f, d);
        if (typeof c == "function") {
            c()
        }
    })
};
mySuning.cityValidate = function (b) {
    favoriteCityId = b.find("#inputCityId").val();
    if (!favoriteCityId || favoriteCityId == "") {
        favoriteCityId = thisMfCityId
    }
    var a;
    if (noticeType == "priceDown") {
        a = "//favorite.suning.com/ajax/myFavorite/checkProductPriceNoticeCity.do"
    } else {
        if (noticeType == "arrival") {
            a = "//favorite.suning.com/ajax/myFavorite/checkProductArrivalNoticeCity.do"
        }
    }
    probeAuthStatus(function () {
        $.ajax({
            type: "GET",
            url: a + "?cityId=" + favoriteCityId + "&&partnumber=" + globalPartNumber + "&&shopId=" + globalShopId,
            dataType: "jsonp",
            jsonpCallback: "myCallbacknotice",
            success: function c(d) {
                if (d.returnCode == -1) {
                    $.unmDialog();
                    ensureLogin(function () {})
                } else {
                    var e = d.returnMsg;
                    if (e && e != "") {
                        if (noticeType == "priceDown") {
                            mySuning.onerr($("#errorCityMsgPrice"), e)
                        } else {
                            if (noticeType == "arrival") {
                                mySuning.onerr($("#errorCityMsgArrival"), e)
                            }
                        }
                        cityflag = false
                    } else {
                        cityflag = true
                    }
                }
            }, error: function () {
                if (noticeType == "priceDown") {
                    mySuning.onerr($("#errorCityMsgPrice"), "绯荤粺寮傚父")
                } else {
                    if (noticeType == "arrival") {
                        mySuning.onerr($("#errorCityMsgArrival"), "绯荤粺寮傚父")
                    }
                }
            }
        })
    }, function () {
        $.unmDialog();
        ensureLogin(function () {})
    })
};

function desensitization(b) {
    var a = b;
    if (b != undefined && b != "" && typeof b == "string") {
        a = b.substring(0, 3) + "******" + b.substring(9, 11)
    }
    return a
}
mySuning.getRecommendedData = function (a, g, e) {
    var f;
    f = $.cookie("cityId");
    if (f == "cityId=undefined") {
        var c = document.cookie.split(";");
        for (var d = 0; d < c.length; d++) {
            var b = c[d].split("=");
            if (b[0] == "cityId") {
                f = unescape(b[1])
            }
        }
    }
    if (f == undefined || f == "" || f == "cityId=undefined") {
        f = "9173"
    }
    $.ajax({
        type: "get",
        url: "//tuijian.suning.com/recommend-portal/recommendv2/biz.jsonp?parameter=" + g + "&cityId=" + f + "&sceneIds=" + a + "&count=12&u=156126",
        dataType: "jsonp",
        jsonpCallback: e,
        cache: true
    })
};
mySuning.myRecommedData = function (e) {
    leng = e.sugGoods[0].skus.length;
    var n = "";
    var a;
    var m;
    if (leng > 12) {
        leng = 12
    }
    if (leng >= 1) {
        $("#picRecommend").css("display", "block");
        for (var f = 0; f < leng; f++) {
            var j = e.sugGoods[0].skus[f].sugGoodsCode;
            var k = e.sugGoods[0].skus[f].sugGoodsName;
            var g = e.sugGoods[0].parameter;
            var r = e.sugGoods[0].skus[f].vendorId;
            var l = e.sugGoods[0].skus[f].price;
            var o = e.sugGoods[0].skus[f].handwork;
            var d = e.sugGoods[0].skus[f].pictureUrl;
            var h;
            var b;
            var c = "";
            if (noticeType == "priceDown") {
                b = "_recsijijzn_"
            } else {
                b = "_recsjdhtzn_"
            } if (globalEntrance == "productDetail") {
                if (ajaxUrl.indexOf("//item") == 0) {
                    h = "item_"
                } else {
                    if (globalShopId != "0000000000") {
                        h = "cprd_";
                        if (noticeType == "priceDown") {
                            b = "_reccsijijz_"
                        } else {
                            b = "_reccsjdhtz_"
                        }
                    } else {
                        h = "item_"
                    }
                }
            } else {
                if (globalEntrance == "searchResult") {
                    if (ajaxUrl.indexOf("//search") == 0) {
                        h = "ssdsn_"
                    } else {
                        h = "ssdln_"
                    } if (noticeType == "priceDown") {
                        b = "_recsijijzn_"
                    } else {
                        b = "_recsojdhtzn_"
                    }
                } else {
                    h = "favorite_"
                }
            }
            var q = h + g.substring(9, 18) + b + (Math.floor(f / 3) + 1) + "-" + (f % 3 + 1) + "_p_" + r + "_" + j.substring(9, 18) + "_" + o;
            var p = h + g.substring(9, 18) + b + (Math.floor(f / 3) + 1) + "-" + (f % 3 + 1) + "_c_" + r + "_" + j.substring(9, 18) + "_" + o;
            if (d == null || d == "") {
                c = "<img src='//image.suning.cn/content/catentries/" + j.substring(0, 14) + "/" + j + "/" + j + "_ls1.jpg' "
            } else {
                c = "<img src='" + d + "_100w_100h_4e'"
            }
            n = n + "<li><a  class='fav-pic' title='" + k + "' name='" + q + "' href='//product.suning.com/" + r + "/" + j + ".html?src=" + q + "' target='_blank'> " + c + "id='img" + j + "' /></a>    <p class='msg-protitle' style='height:34px; overflow: hidden;'><a name='" + q + "' title='" + k + "' target='_blank'  href='//product.suning.com/" + r + "/" + j.substring(9, 18) + ".html?src=" + p + "' >" + k + "</a></p> <p class='snPrice'><em class='l'>锟�</em><i> " + l + "</i></p> </li>"
        }
        $(".movbox-artic").html(n);
        $(".m-dialog").css("top", "30%");
        mySuning.fav_showPic();
        if ((navigator.userAgent.indexOf("MSIE") >= 0) && (navigator.userAgent.indexOf("Opera") < 0)) {
            setTimeout(function () {
                $(".movpic-shot").find("li").each(function () {
                    var i = $(this).find("img");
                    var s = i.attr("src");
                    i.attr("src", "");
                    i.load(function () {
                        var t = i.attr("id");
                        mySuning.zoom(t, 100, 100)
                    });
                    i.attr("src", s)
                })
            }, 200)
        } else {
            $(".movpic-shot").find("li").each(function () {
                var i = $(this).find("img");
                var s = i.attr("src");
                i.attr("src", "");
                i.load(function () {
                    var t = i.attr("id");
                    mySuning.zoom(t, 100, 100)
                });
                i.attr("src", s)
            })
        }
    } else {
        $("#picRecommend").css("display", "none")
    }
};
mySuning.productSuccessRecommedCallback = function (r) {
    var d = r.sugGoods[0].skus.length;
    var j = "<ul class='movbox-artic'>";
    var p;
    if (globalEntrance == "productDetail") {
        if (ajaxUrl.indexOf("//item") == 0) {
            p = "item_";
            recommedBuriedPointCollect = "_recscollectn_"
        } else {
            if (globalShopId != "0000000000") {
                p = "cprd_";
                recommedBuriedPointCollect = "_reccscollect_"
            } else {
                p = "item_";
                recommedBuriedPointCollect = "_recscollectn_"
            }
        }
    } else {
        if (globalEntrance == "searchResult") {
            if (ajaxUrl.indexOf("//search") == 0) {
                p = "ssdsn_";
                recommedBuriedPointCollect = "_recsostore_"
            } else {
                p = "ssdln_";
                recommedBuriedPointCollect = "_recstore_"
            }
        } else {
            p = "favorite_";
            recommedBuriedPointCollect = "_recscollectn_"
        }
    }
    var e = r.sugGoods[0].parameter;
    if (d > 0) {
        var g = d;
        if (d > 12) {
            g = 12
        }
        for (var m = 0; m < g; m++) {
            var o = r.sugGoods[0].skus[m].sugGoodsCode;
            var s = r.sugGoods[0].skus[m].vendorId;
            var q = r.sugGoods[0].skus[m].sugGoodsName;
            if (q.length >= 20) {
                var a = q.substring(0, 20)
            } else {
                var a = q
            }
            var l = r.sugGoods[0].skus[m].price;
            var t = r.sugGoods[0].skus[m].handwork;
            var k = r.sugGoods[0].skus[m].pictureUrl;
            var c = "//product.suning.com/" + s + "/" + o + ".html?src=" + p + e.substring(9, 18) + recommedBuriedPointCollect + (Math.floor(m / 3) + 1) + "-" + (m % 3 + 1) + "_p_" + s + "_" + o.substring(9, 18) + "_" + t;
            var n = "//product.suning.com/" + s + "/" + o + ".html?src=" + p + e.substring(9, 18) + recommedBuriedPointCollect + (Math.floor(m / 3) + 1) + "-" + (m % 3 + 1) + "_c_" + s + "_" + o.substring(9, 18) + "_" + t;
            var f;
            if (typeof k == "undefined" || k == null || k == "") {
                f = "//image.suning.cn/content/catentries/" + o.substring(0, 14) + "/" + o + "/" + o + "_ls1.jpg"
            } else {
                f = k + "_100w_100h_4e"
            }
            var h = p + e.substring(9, 18) + recommedBuriedPointCollect + (Math.floor(m / 3) + 1) + "-" + (m % 3 + 1) + "_p_" + s + "_" + o.substring(9, 18) + "_" + t;
            var b = p + e.substring(9, 18) + recommedBuriedPointCollect + (Math.floor(m / 3) + 1) + "-" + (m % 3 + 1) + "_c_" + s + "_" + o.substring(9, 18) + "_" + t;
            j = j + "<li><a title='" + q + "' name='" + h + "' href='" + c + "' target='_blank' class='fav-pic'><img src='" + f + "' alt='" + q + "' id='img" + o + "'/></a><a href='" + n + "' title='" + q + "'  name='" + b + "' target='_blank' class='fav-msg'>" + q + "</a><span class='fav-price'>&yen;" + l + " </span></li>"
        }
        j = j + "</ul>";
        $(".movpic-shot").html(j);
        $(".movpic-artic").removeAttr("style");
        $(".m-dialog").css("top", "30%");
        mySuning.fav_showPic();
        if ((navigator.userAgent.indexOf("MSIE") >= 0) && (navigator.userAgent.indexOf("Opera") < 0)) {
            setTimeout(function () {
                $(".movpic-shot").find("li").each(function () {
                    var i = $(this).find("img");
                    var u = i.attr("src");
                    i.attr("src", "");
                    i.load(function () {
                        var v = i.attr("id");
                        mySuning.zoom(v, 100, 100)
                    });
                    i.attr("src", u)
                })
            }, 200)
        } else {
            $(".movpic-shot").find("li").each(function () {
                var i = $(this).find("img");
                var u = i.attr("src");
                i.attr("src", "");
                i.load(function () {
                    var v = i.attr("id");
                    mySuning.zoom(v, 100, 100)
                });
                i.attr("src", u)
            })
        }
    }
};
mySuning.shopSuccessRecommedCallback = function (k) {
    var a = k.sugGoods[0].skus.length;
    var p = "<ul class='movbox-artic'>";
    if (a > 0) {
        var c = "";
        var d = a;
        if (a > 12) {
            d = 12
        }
        var e = "cprd_";
        for (var l = 0; l < d; l++) {
            var j = k.sugGoods[0].skus[l].sugGoodsName;
            var n = k.sugGoods[0].parameter;
            var f = k.sugGoods[0].skus[l].sugGoodsDes;
            var m = k.sugGoods[0].skus[l].sugGoodsCode;
            var q = k.sugGoods[0].skus[l].handwork;
            if (f == undefined || f.length == 0) {
                f = "//image.suning.cn/project/myfavorite/images/shop.png"
            }
            var o = k.sugGoods[0].skus[l].sugGoodsCode;
            var h = k.sugGoods[0].skus[l].promotionInfo;
            if (o.length > 8) {
                c = c + o + "_"
            }
            c = c.substring(0, c.length - 1);
            var b = e + n + "_recscdp_" + (Math.floor(l / 3) + 1) + "-" + (l % 3 + 1) + "_p_0000000000_" + m + "_" + q;
            var g = h + "?src=" + b;
            p = p + '<li id="recmStar' + o + '"><a title="' + j + '" name="' + b + '" href="' + g + '" class="fav-pic" target="_blank"><img src="' + f + '" id="img' + o + '"/></a><p class="msg-protitle"><a href="' + g + '" title="' + j + '" target="_blank">' + j + '</a></p><div class="pro-lvstart"><span class="comment-star"><em style="width:' + 5 * 14 + 'px;margin-top:0"></em></span></div></li>'
        }
        p = p + "</ul>";
        $(".movpic-shot").html(p);
        $(".movpic-artic").removeAttr("style");
        $(".m-dialog").css("top", "30%");
        mySuning.fav_showPic();
        if ((navigator.userAgent.indexOf("MSIE") >= 0) && (navigator.userAgent.indexOf("Opera") < 0)) {
            setTimeout(function () {
                $(".movpic-shot").find("li").each(function () {
                    var i = $(this).find("img");
                    var r = i.attr("src");
                    i.attr("src", "");
                    i.load(function () {
                        var s = i.attr("id");
                        mySuning.zoom(s, 100, 100)
                    });
                    i.attr("src", r)
                })
            }, 200)
        } else {
            $(".movpic-shot").find("li").each(function () {
                var i = $(this).find("img");
                var r = i.attr("src");
                i.attr("src", "");
                i.load(function () {
                    var s = i.attr("id");
                    mySuning.zoom(s, 100, 100)
                });
                i.attr("src", r)
            })
        }
        mySuning.getShopStarsJsonp(c)
    }
};
mySuning.getShopStarsJsonp = function (c) {
    var b = "//favorite.suning.com/ajax/getShopStarsJsonp.do?shopIdStr=" + c;
    $.ajax({
        type: "get",
        url: b,
        async: false,
        dataType: "jsonp",
        jsonpCallback: "myCallbackStars",
        success: function a(g) {
            var d = 0;
            for (var e in g) {
                var f = (g.shopReviewScoreList[e].shopStar / 5 * 69).toFixed(2);
                $("#recmStar" + g[e].supplierCode).find("em").attr("style", "width:" + f + "px")
            }
        }
    })
};
mySuning.subscribeArrivalNoticeCheck = function (i, h, d, b, e, f, g, c) {
    var a = "//favorite.suning.com/ajax/fourPage/checkCountArrival.do";
    ensureLogin(function () {
        $.ajax({
            type: "GET",
            async: false,
            url: a + "?partnumber=" + i + "&shopId=" + h,
            dataType: "jsonp",
            jsonpCallback: "myCallbacknotice",
            success: function j(m) {
                var n = m.bookFlag;
                var k;
                if (n == 2) {
                    showMsg("璁㈤槄宸叉弧50娆★紝鏃犳硶璁㈤槄锛�")
                } else {
                    if (n == 0) {
                        try {
                            if (window.SNNativeClient) {
                                if (window.SNNativeClient.appNotificationStatus) {
                                    window.SNNativeClient.appNotificationStatus(1)
                                }
                            }
                        } catch (o) {}
                        var p = "//favorite.suning.com/ajax/myFavorite/addProductArrivalNotice.do?mobilePhone=" + e;
                        if (f == null || f == undefined) {
                            f = "0"
                        }
                        if (g == null || g == undefined) {
                            g = "N"
                        }
                        $.ajax({
                            type: "GET",
                            url: p + "&&partnumber=" + i + "&&shopId=" + h + "&mdmCityCode=" + d + "&entrance=" + b + "&channel=2&pdType=" + f + "&shoptType=" + g,
                            dataType: "jsonp",
                            jsonpCallback: "myCallbacknotice",
                            success: function l(q) {
                                var t = q.returnCode;
                                if (t !== undefined && t === "-3") {
                                    showMsg("鎮ㄨ闃呯殑娆℃暟宸茶揪涓婇檺锛岃鏄庡ぉ鍐嶈瘯锛�");
                                    c();
                                    return
                                }
                                var s = q.returnMsg;
                                if (s == undefined || s == "") {
                                    var u = $("#checkin8").prop("checked");
                                    if (u) {
                                        var r = "//favorite.suning.com/ajax/addProductFavoriteJsonp.do?";
                                        $.ajax({
                                            type: "GET",
                                            url: r + "partnumber=" + i + "&shopId=" + h + "&entrance=" + b + "&channel=2&pdType=" + f + "&shoptType=" + g,
                                            async: false,
                                            dataType: "json",
                                            success: function (v) {}
                                        })
                                    }
                                    showMsg("璁㈤槄鎴愬姛锛岃鑰愬績绛夊緟锛�")
                                } else {
                                    showMsg("璁㈤槄澶辫触锛岀郴缁熷紓甯革紒");
                                    c()
                                }
                            }, error: function () {
                                c();
                                showMsg("璁㈤槄澶辫触锛岀郴缁熷紓甯革紒")
                            }
                        })
                    }
                }
            }
        })
    })
};
mySuning.zoom = function (a, e, f) {
    $("#" + a).css("width", "");
    $("#" + a).css("height", "");
    var g = $("#" + a).width();
    var h = $("#" + a).height();
    if ((e / f) > (g / h)) {
        $("#" + a).width((f * g) / h);
        $("#" + a).height(f);
        var c = (e - $("#" + a).width()) / 2;
        var b = (f - $("#" + a).height()) / 2;
        $("#" + a).css("margin-top", b);
        $("#" + a).css("margin-left", c);
        $("#" + a).css("margin-right", c - 1)
    } else {
        $("#" + a).width(e);
        $("#" + a).height((e * h) / g);
        var d = (f - $("#" + a).height()) / 2;
        var i = ($("#" + a).width()) / 2;
        $("#" + a).css("margin-top", d)
    }
};
var spacing = 118;
var page = 1;
var setUpCovers = function () {
    var a;
    a = parseInt(leng / 3);
    $(".pageNum").html("/" + a);
    var b = $(".covers").last();
    var c = b.find(".covers_a");
    $(".btn_forLeft").die("click");
    $(".btn_forRight").die("click");
    c.eq(0).css("left", "0");
    c.eq(1).css("left", spacing);
    c.eq(2).css("left", spacing * 2);
    $(".btn_forLeft").live("click", function (e) {
        var d = $(".covers").last();
        var f = d.find(".covers_a");
        f.eq(2).animate({
            left: spacing * 5
        }, "fast");
        f.eq(1).animate({
            left: spacing * 4
        }, "fast");
        f.eq(0).animate({
            left: spacing * 3
        }, "fast");
        f.eq(f.length - 1).css("left", (-spacing)).animate({
            left: spacing * 2
        }, "fast");
        f.eq(f.length - 2).css("left", (-spacing) * 2).animate({
            left: spacing
        }, "fast");
        f.eq(f.length - 3).css("left", (-spacing) * 3).animate({
            left: 0
        }, "fast", function () {
            f.eq(f.length - 1).prependTo(".covers");
            f.eq(f.length - 2).prependTo(".covers");
            f.eq(f.length - 3).prependTo(".covers");
            setUpCovers()
        });
        if (page > 1) {
            page--
        } else {
            page = a
        }
        $(".page").html(page);
        e.preventDefault()
    });
    $(".btn_forRight").live("click", function (e) {
        var d = $(".covers").last();
        var f = d.find(".covers_a");
        f.eq(0).animate({
            left: -spacing * 3
        }, "fast");
        f.eq(1).animate({
            left: -spacing * 2
        }, "fast");
        f.eq(2).animate({
            left: -spacing
        }, "fast");
        f.eq(3).css("left", spacing * 3).animate({
            left: 0
        }, "fast");
        f.eq(4).css("left", spacing * 4).animate({
            left: spacing
        }, "fast");
        f.eq(5).css("left", spacing * 5).animate({
            left: spacing * 2
        }, "fast", function () {
            f.eq(0).appendTo(".covers");
            f.eq(1).appendTo(".covers");
            f.eq(2).appendTo(".covers");
            setUpCovers()
        });
        if (page < a) {
            page++
        } else {
            page = 1
        }
        $(".page").html(page);
        e.preventDefault()
    })
};
mySuning.listloop = function (b) {
    var c = {
        wrap: "#brandPromo",
        loopBox: "#brandPromo-list",
        triggerLeft: ".dir-prev",
        triggerRight: ".dir-next",
        curCount: ".cur-count",
        totalCount: ".total-count",
        step: {
            wide: 7,
            narrow: 6
        },
        scrollWidth: {
            wide: 840,
            narrow: 660
        },
        hasCount: true,
        isLoop: true,
        isLazyLoad: true,
        delay: 0
    };
    $.extend(c, b);
    var h = $(c.wrap),
        n = h.find(c.triggerLeft),
        a = h.find(c.triggerRight),
        q = h.find(c.loopBox),
        g = q.find("li"),
        e = c.step.wide,
        l = c.scrollWidth.wide,
        s = Math.ceil(g.length / e),
        f = g.length,
        j = h.find(c.curCount),
        t = h.find(c.totalCount),
        r = 0;
    if (screen.width < 1280) {
        e = c.step.narrow;
        l = c.scrollWidth.narrow;
        var u = g.length % e;
        s = Math.ceil(g.length / e);
        f = g.length - u
    }
    c.hasCount && t.html(s);
    n.click(function () {
        m();
        return false
    });
    a.click(function () {
        o();
        return false
    });

    function o() {
        if (s == 1 || q.is(":animated")) {
            return false
        }
        if (!c.isLoop) {
            r++;
            if (r >= s) {
                r = s - 1
            }
            p(false, r);
            return
        }
        if (r == s - 1) {
            for (var i = 0; i < e; i++) {
                g.eq(i).css({
                    position: "relative",
                    left: s * l + "px"
                })
            }
        }
        r++;
        p(function () {
            if (r == s) {
                r = 0;
                g.removeAttr("style");
                q.css("marginLeft", r * l)
            }
        }, r)
    }

    function m() {
        if (s == 1 || q.is(":animated")) {
            return false
        }
        if (!c.isLoop) {
            r--;
            if (r <= 0) {
                r = 0
            }
            p(false, r);
            return
        }
        if (r == 0) {
            for (var i = 1; i <= e; i++) {
                g.eq(f - i).css({
                    position: "relative",
                    left: -s * l + "px"
                })
            }
        }
        r--;
        p(function () {
            if (r == -1) {
                r = s - 1;
                g.removeAttr("style");
                q.css("marginLeft", -r * l)
            }
        }, r)
    }

    function p(v, i) {
        k();
        if (c.hasCount) {
            if (i > s - 1) {
                i = 0
            }
            if (i < 0) {
                i = s - 1
            }
            j.html(i + 1)
        }
        if (!v) {
            v = function () {}
        }
        q.stop().animate({
            marginLeft: -r * l
        }, 500, v)
    }

    function k() {
        if (!c.isLazyLoad) {
            return
        }
        for (var v = 0; v < e; v++) {
            var i = g.eq(r * e + v).find("img");
            if (i.attr("src3")) {
                i.attr("src", i.attr("src3")).removeAttr("src3").addClass("err-product")
            }
        }
    }
    if (c.delay) {
        var d = setInterval(function () {
            o()
        }, c.delay);
        h.hover(function () {
            clearInterval(d)
        }, function () {
            d = setInterval(function () {
                o()
            }, c.delay)
        })
    }
};
mySuning.getShopStar = function (c) {
    var b = "//favorite.suning.com/ajax/getShopStar.do?shopId=" + c;
    var a = $.ajax({
        type: "get",
        url: b,
        async: false,
        dataType: "json",
        success: function (e) {
            var d = e;
            return d
        }, error: function (d) {
            return 5
        }
    });
    return a.responseText
};
mySuning.addCookie = function (a) {
    $.cookie("smhst", a)
};
mySuning.add2BrandFavorite = function (d, c, a, e, b) {
    probeAuthStatus(function () {
        var f = "//favorite.suning.com/ajax/addBrandFavorite.do?brandId=" + d + "&deptId=" + c + "&entrance=" + a;
        if (e) {
            $.ajax({
                type: "GET",
                async: false,
                url: f,
                dataType: "jsonp",
                jsonpCallback: e
            })
        } else {
            f = f + "&dialog=1";
            $.ajax({
                type: "GET",
                async: false,
                url: f,
                dataType: "jsonp",
                jsonpCallback: "myBrandFavorWithDialog",
                success: function g(h) {
                    $.mDialog({
                        css: {
                            width: "450px"
                        },
                        http: function (i, j) {
                            i.find(".content").html(h.htmlDom)
                        }, overlayCss: {
                            background: "black ",
                            opacity: "0.3"
                        }, title: "娓╅Θ鎻愮ず"
                    })
                }
            })
        }
    }, function () {
        ensureLogin(function () {
            mySuning.add2BrandFavorite(d, c, a, e, b)
        })
    })
};
mySuning.cancelSubscibeConfirm = function () {
    alert(fMobileNumber.val());
    $.mLionDialog({
        css: {
            width: "420px"
        },
        message: $(".cancel-subscibe-confirm"),
        overlayCss: {
            background: "black",
            opacity: "0.3"
        },
        title: "娓╅Θ鎻愮ず",
        fadeIn: 300,
        fadeOut: 300
    })
};
mySuning.cancelSubscibeSuccess = function () {
    $.mLionDialog({
        css: {
            width: "420px"
        },
        message: $(".cancel-subscibe-success"),
        overlayCss: {
            background: "black",
            opacity: "0.3"
        },
        title: "娓╅Θ鎻愮ず",
        fadeIn: 300,
        fadeOut: 300
    })
};
mySuning.submitFavoriteSaMessageV2 = function (b) {
    try {
        if (b) {
            if (sa.openAPI && sa.openAPI.sendMsgV2) {
                mySuning.sendFavoriteLazySaMessageV2(b)
            } else {
                $.getScript("//res.suning.cn/javascript/sn_da/sa-analytics.js", function () {
                    sa.openAPI = true;
                    sa.initTrackerConfig();
                    mySuning.sendFavoriteLazySaMessageV2(b)
                })
            }
        }
    } catch (a) {}
};
mySuning.sendFavoriteLazySaMessageV2 = function (e) {
    var b = e.split(",");
    for (var a = 0; a < b.length; a++) {
        var c = b[a];
        if (c != "") {
            var d = mySuning.getFavoriteSaRequestData(c);
            sa.openAPI.sendMsgV2(d)
        }
    }
};
mySuning.getFavoriteSaRequestData = function (d) {
    var b = "1";
    var a = "";
    var c = "";
    switch (d) {
    case "mf-pcproductunsell-2_unsell":
        a = "ICPS";
        c = "鏆備笉閿€鍞�";
        break;
    case "mf-pcproductunsell-2_soldout":
        a = "ICPS";
        c = "鏃犺揣";
        break;
    case "mf-goodicps-1empty":
        a = "ICPS";
        c = "浠锋牸鎺ュ彛杩斿洖绌�";
        break;
    case "mf-goodicps-1error":
        a = "ICPS";
        c = "404";
        break;
    case "mf-good-second-category-name-05":
        a = "MF";
        c = "鍟嗗搧浜岀骇鐩綍杩斿洖绌�";
        break;
    case "mf-shopscore-1empty":
        a = "REVIEW";
        c = "搴楅摵鏃燚SR璇勫垎";
        break;
    case "mf-shopscore-2error":
        a = "REVIEW";
        c = "搴楅摵DSR璇勫垎寮傚父";
        break;
    case "mf-shopfans-1empty":
        a = "MF";
        c = "鏃犵矇涓濇暟";
        break;
    case "mf-shopfans-2error":
        a = "MF";
        c = "绮変笣鏁版帴鍙ｅ紓甯�";
        break;
    case "mf-pcproductcancel-2_error":
        a = "MF";
        c = "鍙栨秷鍟嗗搧鍏虫敞鎺ュ彛寮傚父";
        break;
    case "mf-goodcancel-2error":
        a = "MF";
        c = "鍙栨秷鍟嗗搧鍏虫敞鐧诲綍寮傚父";
        break;
    case "mf-shopcancel-1error":
        a = "MF";
        c = "鍙栨秷搴楅摵鍏虫敞鎺ュ彛寮傚父";
        break;
    case "mf-shopcancel-2error":
        a = "MF";
        c = "鍙栨秷搴楅摵鍏虫敞鐧诲綍寮傚父";
        break;
    case "mf-arrival-1error":
        a = "MF";
        c = "璁㈤槄鍒拌揣閫氱煡鏈櫥褰�";
        break;
    case "mf-pcproductdownpricenotice-2_error":
        a = "MF";
        c = "璁㈤槄鍒拌揣閫氱煡寮傚父";
        break;
    case "mf-pcproductarrivenotice-2_error":
        a = "MF";
        c = "璁㈤槄闄嶄环閫氱煡寮傚父";
        break;
    case "mf-priceDown-2error":
        a = "MF";
        c = "璁㈤槄闄嶄环閫氱煡鏈櫥褰�";
        break;
    case "mf-good-1empty":
        a = "MF";
        c = "鍟嗗搧鍒楄〃椤靛睍绀虹┖鐧�";
        break;
    case "mf-shoptag-1empty":
        a = "MF";
        c = "搴楅摵鐩綍灞曠ず绌虹櫧";
        break;
    case "mf-shopbaseInfo-1empty":
        a = "MF";
        c = "搴楅摵鍩烘湰淇℃伅灞曠ず绌虹櫧";
        break;
    case "mf-shoplist-1empty":
        a = "MF";
        c = "搴楅摵鍒楄〃椤靛睍绀虹┖鐧�";
        break;
    case "mf-shopnewAndSale-1error":
        a = "MF";
        c = "搴楅摵鍏虫敞鍒楄〃涓婃柊鍜岀儹閿€鍙栦俊鎭け璐�";
        break;
    case "mf-shopnewAndSale-2error":
        a = "MF";
        c = "搴楅摵鍏虫敞鍒楄〃涓婃柊鍜岀儹閿€淇冮攢鎺ュ彛璇锋眰澶辫触";
        break;
    case "mf-wapshopcancel-1error":
        a = "MF";
        c = "鍙栨秷搴楅摵鍏虫敞澶辫触";
        break;
    case "mf-shopremove-2error":
        a = "MF";
        c = "鍙栨秷搴楅摵鍏虫敞璇锋眰澶辫触";
        break;
    case "mf-shoptop-1error":
        a = "MF";
        c = "PC绔簵閾虹疆椤跺け璐�";
        break;
    case "mf-shoptop-2error":
        a = "MF";
        c = "PC绔簵閾虹疆椤惰姹傚け璐�";
        break;
    case "mf-shoprecommend-1error":
        a = "MF";
        c = "PC绔簵閾虹寽浣犲枩娆㈣幏鍙栦俊鎭け璐�";
        break;
    case "mf-brandremove-1error":
        a = "MF";
        c = "鍝佺墝鍏虫敞鍒犻櫎鍝佺墝澶辫触";
        break;
    case "mf-pcbrandcancel-2_error":
        a = "MF";
        c = "鍝佺墝鍙栨秷鍏虫敞鎺ュ彛寮傚父";
        break;
    case "mf-shoprecommend-1empty":
        a = "MF";
        c = "PC绔寽浣犲枩娆㈢┖鐧�";
        break;
    case "mf-pcshoptag-2_error":
        a = "MF";
        c = "搴楅摵鐩綍鎺ュ彛寮傚父";
        break;
    case "mf-pcshopbaseInfo-2_error":
        a = "MF";
        c = "搴楅摵鍩烘湰淇℃伅鎺ュ彛寮傚父";
        break;
    case "mf-pcshoplist-2_error":
        a = "MF";
        c = "搴楅摵鍒楄〃椤垫帴鍙ｅ紓甯�";
        break;
    case "mf-pcshopnewAndSale-2_error":
        a = "MF";
        c = "搴楅摵鍏虫敞鍒楄〃涓婃柊鍜岀儹閿€鎺ュ彛寮傚父";
        break;
    case "mf-pcshopnewAndSale-2_empty":
        a = "MF";
        c = "搴楅摵鍏虫敞鍒楄〃涓婃柊鍜岀儹閿€鎺ュ彛涓虹┖";
        break;
    case "mf-pcshopremove-2_error":
        a = "MF";
        c = "鍙栨秷搴楅摵鍏虫敞鎺ュ彛寮傚父";
        break;
    case "mf-pcshoptop-2_error":
        a = "MF";
        c = "搴楅摵缃《鎺ュ彛寮傚父";
        break;
    case "mf-pcshopcanceltop-2_error":
        a = "MF";
        c = "搴楅摵鍙栨秷缃《鎺ュ彛寮傚父";
        break;
    case "mf-pcshoprecommend-2_error":
        a = "MF";
        c = "搴楅摵鐚滀綘鍠滄鎺ュ彛寮傚父";
        break;
    case "mf-pcshoprecommend-2_empty":
        a = "MF";
        c = "搴楅摵鐚滀綘鍠滄鎺ュ彛涓虹┖";
        break;
    case "mf-pcshoprecommendcollect-2_error":
        a = "MF";
        c = "鎺ㄨ崘搴楅摵娣诲姞鍏虫敞鎺ュ彛寮傚父";
        break;
    case "mf-pcshoprecommendcancel-2_error":
        a = "MF";
        c = "鎺ㄨ崘搴楅摵鍙栨秷鍏虫敞鎺ュ彛寮傚父";
        break;
    case "mf-pcshopscore-2_error":
        a = "MF";
        c = "搴楅摵璇勫垎鎺ュ彛寮傚父";
        break;
    case "mf-pcshopscore-2_empty":
        a = "MF";
        c = "搴楅摵璇勫垎鎺ュ彛涓虹┖";
        break;
    case "mf-pcshopfans-2_error":
        a = "MF";
        c = "搴楅摵绮変笣鏁版帴鍙ｅ紓甯�";
        break;
    case "mf-pcshopfans-2_empty":
        a = "MF";
        c = "搴楅摵绮変笣鏁版帴鍙ｄ负绌�";
        break
    }
    var e = {
        type_name: a,
        error_type: b,
        error_code: d,
        error_detail: c,
        member_id: $.cookie("custno"),
        member_level: $.cookie("custLevel"),
        region: $.cookie("SN_CITY"),
        bid: "mf"
    };
    return e
};
var mySuning = mySuning || {
    mySuningFavoriteNoticePartnumber: null,
    mySuningFavoriteNoticeShopId: null,
    mySuningFavoriteNoticeEntrace: null
};
var noticeMin = 5;
var mobilePhone = "";
var dzMobilePhone = "";
var favSaleNotice = {
    inputPhone: function (a, b) {
        ensureLogin(function () {
            $.ajax({
                url: "//favorite.suning.com/ajax/myFavorite/checkSaleNotice.do",
                type: "get",
                data: a,
                dataType: "jsonp",
                success: function (d) {
                    if (d.returnCode == "0") {
                        var e = d.returnMsg;
                        var f = e.split("_");
                        noticeMin = f[0];
                        if (f.length > 1) {
                            mobilePhone = f[1];
                            dzMobilePhone = desensitization(mobilePhone)
                        }
                        $("#dlg-input-phone").remove();
                        if ($("#dlg-input-phone").length == 0) {
                            var c = '<div id="dlg-input-phone" style="display:none;"><div class="onsale-remaind-dialog" style="width:300px"><table border="0" class=" table-pd"><tr class="d-row"><td class="d-left"><i class="tips-icon"></i></td><td valign="middle"><h3 class="tips-text" >娲诲姩寮€鍞墠' + noticeMin + '鍒嗛挓鎻愰啋鎴�!</h3></td></tr><tr class="d-row"><td class="d-left"></td><td id="phoneTd"><div><label>鎵嬫満鍙风爜锛�</label><input type="text" name="mobilePhone" placeholder="璇疯緭鍏�11浣嶆墜鏈哄彿鐮�" value="' + dzMobilePhone + '" class="input-phone"/><input type="hidden" name="wholeMobilePhone" value="' + mobilePhone + '"  /></div></td></tr><tr class="d-row"><td class="d-left"></td><td class="operate-btns"><a href="javascript:;" class="btn-orange btn-ok l">璁�&nbsp;闃�</a><a href="javascript:;" class="btn-smokewhite btn-cancel l close">鍙�&nbsp;娑�</a></td></tr></table></div></div>';
                            $("body").append(c)
                        }
                        newDialog("#dlg-input-phone", "寮€鍞彁閱�");
                        $("input[name='mobilePhone']").on("focus", function () {
                            $(".err-info").remove();
                            if ($(this).val() == "璇疯緭鍏�11浣嶆墜鏈哄彿鐮�") {
                                $(this).val("");
                                $(this).css("color", "#333")
                            }
                        }).on("blur", function () {
                            var g = this;
                            setTimeout(function () {
                                if ($.trim($(g).val()) == "") {
                                    $(g).css("color", "#999");
                                    $(g).val("璇疯緭鍏�11浣嶆墜鏈哄彿鐮�")
                                }
                                if (desensitization($("input[name='wholeMobilePhone']").val()) != $(g).val()) {
                                    if (!/^(1)\d{10}$/.test($(g).val())) {
                                        if ($(".err-info").length == 0) {
                                            $("#phoneTd").append('<div class="err-info"><i class="tips-icon-err"></i>璇疯緭鍏ユ湁鏁堟墜鏈哄彿鐮�</div>')
                                        }
                                    }
                                }
                            }, 100)
                        });
                        $(".btn-ok").click(function () {
                            var h = $("input[name='mobilePhone']").val();
                            var g = $("input[name='wholeMobilePhone']").val();
                            if (desensitization(g) != h) {
                                if (!/^(1)\d{10}$/.test(h)) {
                                    if ($(".err-info").length == 0) {
                                        $("#phoneTd").append('<div class="err-info"><i class="tips-icon-err"></i>璇疯緭鍏ユ湁鏁堟墜鏈哄彿鐮�</div>')
                                    }
                                    return
                                }
                                a.mobilePhone = $("input[name='mobilePhone']").val()
                            } else {
                                a.mobilePhone = $("input[name='wholeMobilePhone']").val()
                            }
                            $.ajax({
                                url: "//favorite.suning.com/ajax/myFavorite/subscribeNotice.do",
                                type: "get",
                                timeout: 3000,
                                data: a,
                                dataType: "jsonp",
                                success: function (j) {
                                    if (j.returnCode == "0") {
                                        if ($("#dlg-subscribe-ok").length == 0) {
                                            var i = '<div id="dlg-subscribe-ok" style="display:none;"><div class="onsale-remaind-dialog" style="width:400px"><table border="0" class=" table-pd"><tr><td valign="top"><i class="tips-icon-ok"></i></td><td valign="middle"><h3 class="common-tips-text">璁㈤槄鎴愬姛</h3><p class="tips-sub-text">娲诲姩寮€濮嬪墠' + noticeMin + "鍒嗛挓锛屾垜浠皢浼氱涓€鏃堕棿閫氱煡鎮紝璇峰強鏃跺叧娉ㄥ摝锛�</p></td></tr></table></div></div>";
                                            $("body").append(i);
                                            $.unmDialog();
                                            newDialog("#dlg-subscribe-ok", "寮€鍞彁閱�");
                                            setTimeout(function () {
                                                $.unmDialog();
                                                $(".btn-buy").addClass("btn-disable");
                                                $(".btn-buy").html("宸茶闃�")
                                            }, 3000);
                                            b && typeof (b) == "function" && b(j)
                                        }
                                    } else {
                                        $.unmDialog();
                                        failMsgDiv(j.returnMsg);
                                        mySuning.submitFavoriteSaMessageV2("mf-favSaleNotice-error-01")
                                    }
                                }, error: function () {
                                    $.unmDialog();
                                    failMsgDiv("缃戠粶寮€灏忓樊浜嗭紝璇风◢鍚庡啀璇曪紒");
                                    mySuning.submitFavoriteSaMessageV2("mf-favSaleNotice-error-02")
                                }, complete: function (j, i) {
                                    if (i == "timeout") {
                                        $.unmDialog();
                                        failMsgDiv("缃戠粶寮€灏忓樊浜嗭紝璇风◢鍚庡啀璇曪紒");
                                        mySuning.submitFavoriteSaMessageV2("mf-favSaleNotice-error-03")
                                    }
                                }
                            })
                        })
                    } else {
                        failMsgDiv(d.returnMsg);
                        mySuning.submitFavoriteSaMessageV2("mf-favSaleNotice-error-04")
                    }
                }
            })
        })
    }, checkNotice: function (a, b) {
        ensureLogin(function () {
            $.ajax({
                url: "//favorite.suning.com/ajax/myFavorite/checkSaleNotice.do",
                type: "get",
                data: a,
                dataType: "jsonp",
                success: function (c) {
                    b && typeof (b) == "function" && b(c)
                }, error: function (c) {
                    b && typeof (b) == "function" && b(c)
                }
            })
        })
    }
};

function desensitization(b) {
    var a = b;
    if (b != undefined && b != "" && typeof b == "string") {
        a = b.substring(0, 3) + "******" + b.substring(9, 11)
    }
    return a
}

function newDialog(b, a) {
    $.mDialog({
        css: {
            width: "470px"
        },
        message: $(b),
        overlayCss: {
            background: "black",
            opacity: "0.3"
        },
        title: a,
        overlayClick: true,
        fadeIn: 300,
        fadeOut: 300
    })
}

function failMsgDiv(a) {
    $("#dlg-fail-prompt").remove();
    if ($("#dlg-fail-prompt").length == 0) {
        var b = '<div id="dlg-fail-prompt" style="display:none;"><div class="onsale-remaind-dialog"><table border="0" class=" table-pd"><tr><td valign="top"><i class="tips-icon"></i></td><td valign="middle"><h3 class="common-tips-text ">' + a + '</h3></td></tr></table><a href="javascript:;" class="btn-orange btn-ok center close">纭�&nbsp;璁�</a></div></div>';
        $("body").append(b)
    }
    newDialog("#dlg-fail-prompt", "寮€鍞彁閱�")
}
mySuning.submitFavoriteSaMessageV2 = function (b) {
    try {
        if (b) {
            if (sa.openAPI && sa.openAPI.sendMsgV2) {
                mySuning.sendFavoriteLazySaMessageV2(b)
            } else {
                $.getScript("//res.suning.cn/javascript/sn_da/sa-analytics.js", function () {
                    sa.openAPI = true;
                    sa.initTrackerConfig();
                    mySuning.sendFavoriteLazySaMessageV2(b)
                })
            }
        }
    } catch (a) {}
};
mySuning.sendFavoriteLazySaMessageV2 = function (e) {
    var b = e.split(",");
    for (var a = 0; a < b.length; a++) {
        var c = b[a];
        if (c != "") {
            var d = mySuning.getFavoriteSaRequestData(c);
            sa.openAPI.sendMsgV2(d)
        }
    }
};
mySuning.getFavoriteSaRequestData = function (d) {
    var b = "1";
    var a = "";
    var c = "";
    switch (d) {
    case "mf-favSaleNotice-error-01":
        a = "MF";
        c = "璁㈤槄寮€鍞彁閱掓坊鍔犲紓甯�";
        break;
    case "mf-favSaleNotice-error-02":
        a = "MF";
        c = "璁㈤槄寮€鍞彁閱掓帴鍙ｅ紓甯�";
        break;
    case "mf-favSaleNotice-error-03":
        a = "MF";
        c = "璁㈤槄寮€鍞彁閱掕秴鏃跺紓甯�";
        break;
    case "mf-favSaleNotice-error-04":
        a = "MF";
        c = "璁㈤槄寮€鍞彁閱掓牎楠屽紓甯�";
        break
    }
    var e = {
        type_name: a,
        error_type: b,
        error_code: d,
        error_detail: c,
        member_id: $.cookie("custno"),
        member_level: $.cookie("custLevel"),
        region: $.cookie("SN_CITY"),
        bid: "mf"
    };
    return e
};
var ccfsTalkDomain = (function () {
    var a = window.location.hostname;
    var c = a.indexOf("pre.cnsuning");
    if (c != -1) {
        return "//ccfspre.cnsuning.com/ccfs-web"
    }
    var b = a.indexOf("sit.cnsuning");
    if (b != -1) {
        return "//ccfssit.cnsuning.com/ccfs-web"
    }
    return "//ccfs.suning.com/ccfs-web"
})();

function getWebcallParamByHYJ(a, b, c) {
    var d = [];
    if (a) {
        d[d.length] = ("prodUrl=" + encodeURIComponent(a))
    }
    if (b) {
        d[d.length] = ("prodNo=" + encodeURIComponent(b))
    }
    if (c) {
        d[d.length] = ("page=" + encodeURIComponent(c))
    }
    d[d.length] = "url=" + encodeURIComponent(document.location.href);
    d[d.length] = "_t=" + Math.round(Math.random() * 1000000);
    return d.join("&")
}

function getTreatyInfoBigPloy(f, a, b, c, d, e, g) {
    $.ajax({
        url: "//hyj.suning.com/newFourPageService/treatyInfoBigPloy_" + f + "_" + a + "_" + b + "_" + c + "_" + d + "_" + e + ".hs",
        cache: false,
        dataType: "jsonp",
        jsonp: "callback",
        jsonpCallback: "callbackFun",
        success: function (h) {
            g(h)
        }, error: function () {}
    })
}

function getTreatyInfo(f, a, b, c, d, e, g) {
    $.ajax({
        url: "//hyj.suning.com/newFourPageService/treatyInfo_" + f + "_" + a + "_" + b + "_" + c + "_" + d + "_" + e + ".hs",
        cache: false,
        dataType: "jsonp",
        jsonp: "callback",
        jsonpCallback: "callbackFun",
        success: function (h) {
            g(h)
        }, error: function () {}
    })
}

function addShoppingCartCheckBigPloy(g, f, e, c, h, j, d, b, n, l, a, k, i, m) {
    ensureLogin(function () {
        $.ajax({
            url: "//hyj.suning.com/newFourPageService/addShoppingCartCheckForBigPoly_" + g + "_" + f + "_" + e + "_" + c + "_" + h + "_" + j + "_" + d + "_" + b + "_" + n + "_" + l + "_" + a + "_" + k + "_" + i + ".tp",
            dataType: "jsonp",
            jsonp: "callback",
            jsonpCallback: "callbackFun",
            success: function (o) {
                if (o.returnCode == "1") {
                    m(o.returnMsg)
                } else {
                    var q = o.pageFlag;
                    var p = "?type=" + b + "_" + d + "_null_" + q;
                    window.location.href = "//hyj.suning.com/treadyPlan.tp" + p
                }
            }, error: function () {
                addShoppingCartTip()
            }
        })
    })
}

function addShoppingCartCheck(f, e, d, b, g, i, c, a, l, j, h, k) {
    ensureLogin(function () {
        $.ajax({
            url: "//hyj.suning.com/newFourPageService/addShoppingCartCheck_" + f + "_" + e + "_" + d + "_" + b + "_" + g + "_" + i + "_" + c + "_" + a + "_" + l + "_" + j + "_" + h + ".tp",
            dataType: "jsonp",
            jsonp: "callback",
            jsonpCallback: "callbackFun",
            success: function (m) {
                if (m.returnCode == "1") {
                    k(m.returnMsg)
                } else {
                    var o = m.pageFlag;
                    var n = "?type=" + a + "_" + c + "_null_" + o;
                    window.location.href = "//hyj.suning.com/treadyPlan.tp" + n
                }
            }, error: function () {
                addShoppingCartTip()
            }
        })
    })
}
var treatyPhoneAddCartFailMsg = "鎮ㄩ€夋嫨鐨勫晢鍝侊紝鍦ㄦ偍閫夋嫨鐨勫煄甯傛殏鏃犳硶璐拱";

function addShoppingCartTip() {
    alert(treatyPhoneAddCartFailMsg)
}

function getSimPrice(d, c, a, b) {
    $.ajax({
        url: "//hyj.suning.com/fourPageService/simPrice_" + d + "_" + c + "_" + a + ".hs",
        cache: true,
        dataType: "jsonp",
        jsonp: "callback",
        jsonpCallback: "callbackFun",
        success: function (e) {
            b(e)
        }, error: function () {}
    })
}

function getSellPointByCity(b, a, c) {
    $.ajax({
        url: "//hyj.suning.com/fourPageService/sellPointInfo_" + b + "_" + a + ".hs",
        cache: true,
        dataType: "jsonp",
        jsonp: "callback",
        jsonpCallback: "sellPointCallBackFun",
        success: function (d) {
            c(d)
        }, error: function () {}
    })
}

function addSimShoppingCartCheck(d, c, a, b) {
    ensureLogin(function () {
        $.ajax({
            url: "//hyj.suning.com/shoppingCart/addSimShoppingCart.tp",
            data: {
                "simPartnum": d,
                "cityId": c,
                "buyTypeId": a
            },
            dataType: "jsonp",
            jsonp: "callback",
            success: function (f) {
                if (f.returnCode == "1") {
                    if (f.returnMsg == "鎮ㄦ湰鏈堢殑璁㈠崟鏁板凡杈惧埌3寮犱笂闄愶紝鍙厛鏀粯鏈敮浠樿鍗曘€傝嫢鏈変换浣曠枒闂紝璇疯仈绯昏嫃瀹佸鏈嶃€�") {
                        b(f.returnMsg)
                    } else {
                        b(treatyPhoneAddCartFailMsg)
                    }
                } else {
                    var e = f.operatorId;
                    var g = "?type=" + e + "_" + a + "_null";
                    window.location.href = "//hyj.suning.com/treadyPlan.tp" + g
                }
            }, error: function () {
                addShoppingCartTip()
            }
        })
    })
}

function _isInclude(a) {
    var c = /js$/i.test(a);
    var d = document.getElementsByTagName(c ? "script" : "link");
    for (var b = 0; b < d.length; b++) {
        if (d[b][c ? "src" : "href"].indexOf(a) != -1) {
            return true
        }
    }
    return false
}

function getBroadBandSalePointInfo(c, b, d, a, e) {
    $.ajax({
        url: "//hyj.suning.com/appoint/getBroadbandSalePoint_" + c + "_" + b + "_" + d + "_" + a + ".hs",
        dataType: "jsonp",
        jsonp: "callback",
        jsonpCallback: "callbackFun",
        success: function (f) {
            e(f)
        }, error: function () {}
    })
}

function addBroadbandShoppingCartCheck(c, b, d, a) {
    ensureLogin(function () {
        window.location.href = "//hyj.suning.com/appoint/addBroadbandShoppingCartCheck.tp?cmmdtyCode=" + c + "&provinceCode=" + b + "&cityCode=" + d + "&districtCode=" + a
    })
}

function gotoXiaoE(c, i, d, k, b, l, f, h) {
    var a = sn || {};
    var e = ccfsTalkDomain;
    var j = a.vendorCode || "";
    var g = a.flagshipId || "0000000000";
    window.open(e + "/toTalk.htm?groupMember=" + d + "&classCode=" + k + "&brandId=" + b + "&groupId=" + l + "&" + getWebcallParamByHYJ(f, c, i) + "&sc=" + j + "&shopCode=" + g + "&rt=1" + "&cityId=" + h, "_blank")
}
$(document).ready(function () {
    var a = "";
    $("script").each(function () {
        if (typeof ($(this).attr("src")) != "undefined" && $(this).attr("src").indexOf("newFourPageService.js") != -1) {
            a = $(this).attr("src").substring($(this).attr("src").indexOf("?"))
        }
    });
    if (!_isInclude("passport.min.js")) {
        var b = "<script>" + "var passport_config = { " + 'base: "//hyj.suning.com/", ' + 'loginTheme: "b2c_pop" ' + "};" + "<\/script>";
        $("title").append(b);
        var c = '<script type="text/javascript" src="//res.suning.cn/project/passport/js/passport.min.js' + a + '"/>';
        $("title").append(c)
    }
});
ms_memberOrgs = {};
ms_memberOrgs.getEnv = function (d) {
    var f = "";
    var i = /^(\w*)(prexg)(\w*)(.cnsuning.com)$/,
        g = /^(\w*)(xgpre)(\w*)(.cnsuning.com)$/,
        a = /^(\w*)(pre)(\w*)(.cnsuning.com)$/,
        h = /^(\w*)(sit)(\w*)(.cnsuning.com)$/,
        c = /^(\w*)(dev)(\w*)(.cnsuning.com)$/,
        b = window.location.hostname;
    var e = "prd";
    if (i.test(b) || g.test(b)) {
        e = "prexg"
    } else {
        if (a.test(b)) {
            e = "pre"
        } else {
            if (h.test(b)) {
                e = "sit"
            } else {
                if (c.test(b)) {
                    e = "dev"
                }
            }
        }
    }
    switch (e) {
    case "prd":
        switch (d) {
        case "msiDomain":
            f = "my.suning.com";
            break;
        case "msiApiDomain":
            f = "myapi.suning.com";
            break
        }
        break;
    case "prexg":
        switch (d) {
        case "msiDomain":
            f = "myprexg.cnsuning.com";
            break;
        case "msiApiDomain":
            f = "myprexg.cnsuning.com";
            break
        }
        break;
    case "pre":
        switch (d) {
        case "msiDomain":
            f = "mypre.cnsuning.com";
            break;
        case "msiApiDomain":
            f = "mypre.cnsuning.com";
            break
        }
        break;
    case "sit":
        switch (d) {
        case "msiDomain":
            f = "mysit.cnsuning.com/msi-web";
            break;
        case "msiApiDomain":
            f = "mysit.cnsuning.com/msi-web";
            break
        }
        break;
    case "dev":
        switch (d) {
        case "msiDomain":
            f = "mydev.cnsuning.com:8080/msi-web";
            break;
        case "msiApiDomain":
            f = "mydev.cnsuning.com:8080/msi-web";
            break
        }
        break
    }
    return f
};
ms_memberOrgs.getCookie = function (c) {
    var d;
    return (d = document.cookie.match(RegExp("(^| )" + c + "=([^;]*)(;|$)"))) ? decodeURIComponent(d[2].replace(/\+/g, "%20")) : null
};
ms_memberOrgs.setCookie = function (b, e, c, h) {
    var d = false;
    if (!!window.ActiveXObject || "ActiveXObject" in window) {
        d = true
    } else {
        d = false
    } if (d) {
        if (e) {
            if (h) {
                var g = new Date();
                g.setTime(g.getTime() + (h * 1000 * 60));
                var a = "; expires=" + g.toGMTString()
            } else {
                var a = "; expires=At the end of the Session"
            }
            var f = "";
            if (c != null) {
                f = "; path=" + c
            }
            document.cookie = b + "=" + escape(e) + a + f
        }
    } else {
        if (e) {
            if (h) {
                var g = new Date();
                g.setTime(g.getTime() + (h * 1000 * 60));
                var a = "; expires=" + g.toGMTString()
            } else {
                var a = "; expires=Session"
            }
            var f = "";
            if (c != null) {
                f = "; path=" + c
            }
            document.cookie = b + "=" + escape(e) + a + f
        }
    }
};
ms_memberOrgs.setCookieWithDomain = function (a, g, f, c, h) {
    var d = false;
    if (!!window.ActiveXObject || "ActiveXObject" in window) {
        d = true
    } else {
        d = false
    } if (d) {
        if (g) {
            if (c) {
                var e = new Date();
                e.setTime(e.getTime() + (c * 1000 * 60));
                var b = "; expires=" + e.toGMTString()
            } else {
                var b = "; expires=At the end of the Session"
            }
            var i = "";
            if (f != null) {
                i = "; path=" + f
            }
            if (h) {
                i = "; domain=" + h
            }
            document.cookie = a + "=" + escape(g) + b + i
        }
    } else {
        if (g) {
            if (c) {
                var e = new Date();
                e.setTime(e.getTime() + (c * 1000 * 60));
                var b = "; expires=" + e.toGMTString()
            } else {
                var b = "; expires=Session"
            }
            var i = "";
            if (f != null) {
                i = i + "; path=" + f
            }
            if (h) {
                i = i + "; domain=" + h
            }
            document.cookie = a + "=" + escape(g) + b + i
        }
    }
};
ms_memberOrgs.queryMemberOrgsInfo = function (b, e) {
    var a = {
        status: "failure",
        code: "",
        msg: ""
    };
    var d = "_memberOrgIds";
    var c = ms_memberOrgs.getEnv("msiApiDomain");
    if (typeof e == "undefined") {
        if (typeof passport_config != "undefined") {
            e = passport_config
        } else {
            e = {
                base: "//" + c + "/",
                loginTheme: "b2c_pop"
            }
        }
    }
    probeAuthStatus(function (m) {
        var h = ms_memberOrgs.getCookie(d);
        if (h) {
            try {
                var k = h.split("|");
                if (m == k[2]) {
                    a.status = k[0];
                    a.code = k[1];
                    if (k[3]) {
                        a.result = new Object();
                        a.result.orgIds = [];
                        a.result.custNum = m;
                        var j = k[3].split(",");
                        for (var g in j) {
                            var i = new Object();
                            i.orgId = j[g];
                            a.result.orgIds[g] = i
                        }
                    }
                    b(a);
                    return
                }
                ms_memberOrgs.setCookie(d, "failure", "/", -1)
            } catch (l) {}
        }
        var n = "https:" == document.location.protocol ? "https" : "http";
        var f = n + "://" + c + "/api/person/getPersonOrgInfo-" + m + "-getMemberOrgsCallBack.htm";
        $.ajax({
            url: f,
            type: "GET",
            dataType: "jsonp",
            timeout: 5000,
            cache: true,
            jsonpCallback: "getMemberOrgsCallBack",
            success: function (r) {
                try {
                    a = r;
                    if (r.status == "success") {
                        var q = "success|" + r.code + "|" + m + "|";
                        var p = r.result;
                        if (p) {
                            var o = p.orgIds;
                            for (var t in o) {
                                q += o[t].orgId + ","
                            }
                            q = q.substring(0, q.length - 1)
                        }
                        ms_memberOrgs.setCookie(d, q, "/")
                    }
                    b(a)
                } catch (s) {
                    b(a)
                }
            }, error: function (o) {
                b(a)
            }
        })
    }, function () {
        a.code = "NOT_LOGIN";
        a.msg = "鏈櫥褰�";
        b(a)
    }, e)
};
ms_memberOrgs.queryIsEnterprise = function (b, d) {
    var a = {
        status: "failure",
        code: "",
        msg: ""
    };
    var e = "_memberIsEn";
    var c = ms_memberOrgs.getEnv("msiApiDomain");
    if (typeof d == "undefined") {
        if (typeof passport_config != "undefined") {
            d = passport_config
        } else {
            d = {
                base: "//" + c + "/",
                loginTheme: "b2c_pop"
            }
        }
    }
    probeAuthStatus(function (j) {
        var k = ms_memberOrgs.getCookie(e);
        if (k) {
            try {
                var f = k.split("|");
                if (j == f[1]) {
                    a.status = f[0];
                    a.code = f[2];
                    b(a);
                    return
                }
            } catch (i) {}
        }
        var g = "https:" == document.location.protocol ? "https" : "http";
        var h = g + "://" + c + "/api/person/isEnterpriseMember-" + j + "-getIsEnCallBack.htm";
        $.ajax({
            url: h,
            type: "GET",
            dataType: "jsonp",
            timeout: 5000,
            cache: false,
            jsonpCallback: "getIsEnCallBack",
            success: function (o) {
                a = o;
                if (o.status == "success") {
                    var m = o.code;
                    var p = o.msg;
                    var n = "success|" + j + "|" + m;
                    var l = 2 * 60;
                    ms_memberOrgs.setCookie(e, n, "/", l)
                }
                b(a)
            }, error: function (l) {
                b(a)
            }
        })
    }, function () {
        a.code = "NOT_LOGIN";
        a.msg = "鏈櫥褰�";
        b(a)
    }, d)
};
ms_memberOrgs.queryIdentityStatus = function (b, d) {
    var a = {
        status: "failure",
        code: "",
        msg: ""
    };
    var e = "_memberIdSt";
    var c = ms_memberOrgs.getEnv("msiApiDomain");
    if (typeof d == "undefined") {
        if (typeof passport_config != "undefined") {
            d = passport_config
        } else {
            d = {
                base: "//" + c + "/",
                loginTheme: "b2c_pop"
            }
        }
    }
    probeAuthStatus(function (j) {
        var k = ms_memberOrgs.getCookie(e);
        if (k) {
            try {
                var f = k.split("|");
                if (j == f[1]) {
                    a.status = f[0];
                    a.code = "";
                    a.msg = "";
                    a.result = new Object();
                    a.result.custNum = j;
                    a.result.idstCode = f[2];
                    a.result.idstDesc = f[3];
                    b(a);
                    return
                }
                ms_memberOrgs.setCookie(e, "failure", "/", -1)
            } catch (i) {}
        }
        var g = "https:" == document.location.protocol ? "https" : "http";
        var h = g + "://" + c + "/api/person/getIdenStat-" + j + "-getIdStCallBack.htm";
        $.ajax({
            url: h,
            type: "GET",
            dataType: "jsonp",
            timeout: 5000,
            cache: false,
            jsonpCallback: "getIdStCallBack",
            success: function (n) {
                try {
                    a = n;
                    if (n.status == "success") {
                        var p = a.result.idstDesc;
                        var m = "success|" + j + "|" + idstCode + "|" + p;
                        var l = 2 * 60;
                        if ("233000000030" == idstCode) {
                            l = 30 * 24 * 60
                        }
                        ms_memberOrgs.setCookie(e, m, "/", l)
                    }
                    b(a)
                } catch (o) {
                    b(a)
                }
            }, error: function (l) {
                b(a)
            }
        })
    }, function () {
        a.code = "NOT_LOGIN";
        a.msg = "鏈櫥褰�";
        b(a)
    }, d)
};
ms_memberOrgs.queryMemberStatusInfo = function (c, f, b) {
    var a = {
        status: "failure",
        code: "",
        msg: ""
    };
    var g = "_memberStInfo";
    var e = ms_memberOrgs.getEnv("msiApiDomain");
    if (typeof f == "undefined") {
        if (typeof passport_config != "undefined") {
            f = passport_config
        } else {
            f = {
                base: "//" + e + "/",
                loginTheme: "b2c_pop"
            }
        }
    }
    var d = ".suning.com";
    probeAuthStatus(function (r) {
        var k = ms_memberOrgs.getCookie(g);
        if (k) {
            try {
                var n = k.split("|");
                if (r == n[1]) {
                    a.status = n[0];
                    a.code = "";
                    a.msg = "";
                    a.result = new Object();
                    a.resultObj = new Object();
                    a.result.custNum = r;
                    var u = n[2];
                    a.result.custType = u;
                    if ("person" == u) {
                        a.result.eppAuthStat = n[3];
                        a.result.paidFlag = n[4];
                        a.result.levelNum = n[5];
                        if (n.length > 6) {
                            var q = new Array();
                            for (var m = 6; m < n.length; m++) {
                                if (n[m]) {
                                    var p = n[m].split(",") || [];
                                    if (p.length >= 3) {
                                        var s = new Object();
                                        s.levelType = p[0];
                                        s.paidFlag = p[1];
                                        var j = p[2];
                                        if (j && j != "undefined") {
                                            s.paidType = j
                                        }
                                        var l = p[3];
                                        if (l && l != "undefined") {
                                            s.levelNum = l
                                        }
                                        q.push(s)
                                    }
                                }
                            }
                            a.resultObj.custLevelInfoDtoList = q
                        }
                    } else {
                        if ("company" == u) {
                            a.result.idstCode = n[3]
                        }
                    }
                    c(a);
                    return
                }
                ms_memberOrgs.setCookieWithDomain(g, "failure", "/", -1, d)
            } catch (o) {}
        }
        var t = "https:" == document.location.protocol ? "https" : "http";
        var h = t + "://" + e + "/api/person/getMemberStatusInfo-" + r + "-getMemberStatusInfoCallBack.do";
        if (b) {
            h = h + "?levelTypes=" + b
        }
        $.ajax({
            url: h,
            type: "GET",
            dataType: "jsonp",
            timeout: 5000,
            cache: true,
            jsonpCallback: "getMemberStatusInfoCallBack",
            success: function (D) {
                a = D;
                a.result.custNum = r;
                try {
                    if (D.status == "success") {
                        var K = a.result.custType;
                        if ("person" == K) {
                            var x = a.result.eppAuthStat;
                            var v = a.result.paidFlag;
                            var I = "success|" + r + "|" + K + "|" + x + "|" + v;
                            var B = a.resultObj;
                            var H;
                            if (B) {
                                H = B.custLevelInfoDtoList || []
                            }
                            if (H && H.length > 0) {
                                for (var E = 0; E < H.length; E++) {
                                    var G = H[E];
                                    var A = G.levelType;
                                    var C = G.paidFlag;
                                    var w = G.paidType;
                                    var z = G.levelNum;
                                    I = I + "|" + A + "," + C + "," + w + "," + z
                                }
                            }
                            var J = 2 * 60;
                            if ("233000000030" == y) {
                                J = 30 * 24 * 60
                            }
                            ms_memberOrgs.setCookieWithDomain(g, I, "/", J, d)
                        } else {
                            if ("company" == K) {
                                var y = a.result.idstCode;
                                var I = "success|" + r + "|" + K + "|" + y;
                                var J = 2 * 60;
                                if ("233000000030" == y) {
                                    J = 30 * 24 * 60
                                }
                                ms_memberOrgs.setCookieWithDomain(g, I, "/", J, d)
                            }
                        }
                    }
                    c(a)
                } catch (F) {
                    c(a)
                }
            }, error: function (i) {
                c(a)
            }
        })
    }, function () {
        a.code = "NOT_LOGIN";
        a.msg = "鏈櫥褰�";
        c(a)
    }, f)
};

function fctCart2(d, c, e, b, f) {
    var a = {
        flag: "0",
        price: 0,
        message: "鏆備笉閿€鍞�"
    };
    $.ajax({
        type: "get",
        async: false,
        url: "//fct.suning.com/m/searchSourcePrice/jsonp/pc.do",
        dataType: "jsonp",
        data: {
            cmmdtyCode: d,
            supplierCode: c,
            cityCode: e,
            requestQty: b
        },
        timeout: 30000,
        jsonp: "callback",
        jsonpCallback: "callback",
        success: function (g) {
            if (g.flag == "1" && g.price > 0) {
                window.location.href = g.url
            } else {
                f(a)
            }
        }, error: function () {
            f(a)
        }
    })
};