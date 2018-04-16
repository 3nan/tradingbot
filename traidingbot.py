from cryptowatch import Cryptowatch
import time
from datetime import datetime
from static import Sma_Static
from notify import Line_Notify
import os
import sys


def date_from_timestamp(s=None):
    if s==None:
        s = round(time.time())
    return str(datetime.fromtimestamp(s + 60 * 60 * 9))


if __name__ == '__main__':
    LINE_TOKEN=sys.argv[1]
    #print(LINE_TOKEN)
    cw=Cryptowatch("60,180")
    sma=Sma_Static(13,26)
    mycount=0
    nf = Line_Notify(LINE_TOKEN)
    while True :

        try:
            nowdate=date_from_timestamp()
            cw.load()
            ohlc  = cw.get_ohlc_dataframe("60")
            ohlc2 = cw.get_ohlc_dataframe("180")
            res  ,j_log  = sma.judge(ohlc)
            res2 ,j_log2 = sma.judge(ohlc2)

            datetime1=ohlc.time.get_values()[-1]
            closes = ohlc.close.get_values()
            close_a = closes[-1]
            close_b = closes[-2]

            datetime2=ohlc2.time.get_values()[-1]
            closes2 = ohlc2.close.get_values()
            close_a2 = closes2[-1]
            close_b2 = closes2[-2]

            print1=["1M",nowdate,date_from_timestamp(datetime1) ,str(close_b),str(close_a),str(res) ,j_log]
            print2=["3M",nowdate,date_from_timestamp(datetime2) ,str(close_b2),str(close_a2),str(res2) ,j_log2]

            #print(nowdate,date_from_timestamp(datetime1) ,close_b,close_a,res ,j_log)
            #print(nowdate,date_from_timestamp(datetime2) ,close_b2,close_a2,res2 ,j_log2)
            print("-----------------------------------")
            if res != 0 :
                nf.notify("closs")
                nf.notify(",".join(print1))

            if res2 != 0:
                nf.notify("closs")
                nf.notify(",".join(print2))

            if mycount%36 == 0 :
                mycount = 0
                nf.notify(",".join(print1))
                nf.notify(",".join(print1))

            mycount=mycount + 1
            time.sleep(5)
        except Exception as e:
            print(e)
