from bitmexwebsocket import BitmexWebsocket
import time
import numpy as np
import pandas as pd
from notify import Line_Notify



def date_from_timestamp(s=None):
    if s==None:
        s = round(time.time())
    return str(datetime.fromtimestamp(s + 60 * 60 * 9))



if __name__ == '__main__':
    LINE_TOKEN=sys.argv[1]
    start=time.time()
    bs =BitmexWebsocket()
    #bs=BitMEXWebsocket(endpoint="https://testnet.bitmex.com/api/v1", symbol="XBTUSD", api_key=None, api_secret=None)
    #bs=BitMEXWebsocket(endpoint="https://www.bitmex.com/api/v1", symbol="XBTUSD", api_key=None, api_secret=None)
    #bs._get_url()
    same_count_index = {"Sell":0,"Buy":0}


    b_buy =(0,0)
    b_sell=(0,0)
    position = 0 # -1 0 1
    target=5
    sleep_num=1
    print("loop")
    for i in bs.ws.sock.connected:

        #print("test")
        md=bs.market_depth()


        bsres = md[md.side=='Sell' ].sort_values(by=["price","size"])
        bbres = md[md.side=='Buy'].sort_values(by=["price","size"])
        sell_min  = bsres.price.min()
        sell_size = bsres[bsres.price==sell_min]["size"].values[0]
        buy_max   = bbres.price.max()
        buy_size  = bbres[bbres.price==buy_max]["size"].values[0]
        ticker    = bs.get_ticker()

        c_sell=(sell_min,sell_size)
        c_buy =(buy_max,buy_size)

        #print( c_sell,c_buy ,ticker["last"] )
        print ("CURRENT:",ticker["last"] ,"POSSTION:",position)
        time.sleep(sleep_num)

        if (b_buy == c_buy):
            same_count_index["Buy"] += 1
        else:
            same_count_index["Buy"] = 0


        if(b_sell == c_sell ):
            same_count_index["Sell"] += 1
        else:
            same_count_index["Sell"]  = 0

        if (position !=-1 and same_count_index["Buy"]>target and same_count_index["Sell"]<target):
            position = -1
            print("SELL")
                #bs.reset_market_depth()

        if (position !=1 and same_count_index["Sell"]>target and same_count_index["Buy"]<target):
            position = 1
            print("BUY")
                #bs.reset_market_depth()

        if (same_count_index["Sell"]>target and same_count_index["Buy"]>target):
            if (position==1):
                print("BUY CLOSE")
                position =0
            elif(position==-1):
                print("SELL CLOSE")
                position =0
            same_count_index = {"Sell":0,"Buy":0}
            bs.reset_market_depth()
            print("RESET!!")

        b_sell = c_sell
        b_buy = c_buy
        print(same_count_index)



    bs.exit()
    print(time.time()-start)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    