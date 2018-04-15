import requests 
import time as tm
import pandas as pd
import numpy as np


class Cryptowatch():
    CRYPT_API="https://api.cryptowat.ch/markets/bitmex/btcusd-perpetual-futures/ohlc?periods=60,180"
    def __get_ohlc_cols(self):
        return ['time','open','high','low','close','volume_coin','volume_usd' ]
    
    def __init__(self,periods=["60"]):
        self.res = None
        self.__params={"periods":",".join(periods)}
    
    def load(self ):
        self.res=requests.get(self.CRYPT_API,params=self.__params).json()
    
    def unset(self):
        self.res = None
    
    def get_ohlc_list(self ,span='span'):
        return self.res['result'][span]
    
    def get_ohlc_dataframe(self ,span='60'):
        res = self.res['result'][span]
        res = pd.DataFrame(res,columns=self.__get_ohlc_cols())
        return res