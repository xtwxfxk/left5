%module(directors="1") thosttraderapi 
%{ 
#include "ThostFtdcTraderApi.h"
#include "iconv.h"
%}

%typemap(out) char[ANY], char[] {
    if ($1) {
        iconv_t cd = iconv_open("utf-8", "gb2312");
        if (cd != reinterpret_cast<iconv_t>(-1)) {
            char buf[4096] = {};
            char **in = &$1;
            char *out = buf;
            size_t inlen = strlen($1), outlen = 4096;

            if (iconv(cd, in, &inlen, &out, &outlen) != static_cast<size_t>(-1))
            {
              size_t size = outlen;
              while (size && (buf[size - 1] == '\0')) --size;
              resultobj = SWIG_FromCharPtrAndSize(buf, size);
            }
            iconv_close(cd);
        }
    }
}
%feature("director") CThostFtdcTraderSpi; 
%ignore THOST_FTDC_VTC_BankBankToFuture;
%ignore THOST_FTDC_VTC_BankFutureToBank;
%ignore THOST_FTDC_VTC_FutureBankToFuture;
%ignore THOST_FTDC_VTC_FutureFutureToBank;
%ignore THOST_FTDC_FTC_BankLaunchBankToBroker;
%ignore THOST_FTDC_FTC_BrokerLaunchBankToBroker;
%ignore THOST_FTDC_FTC_BankLaunchBrokerToBank;
%ignore THOST_FTDC_FTC_BrokerLaunchBrokerToBank;  
%feature("director") CThostFtdcTraderSpi; 
%include "ThostFtdcUserApiDataType.h"
%include "ThostFtdcUserApiStruct.h" 
%include "ThostFtdcTraderApi.h"