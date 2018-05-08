import websocket
import logging
import urllib
import threading
import time
import json
import pandas as pd
import numpy as np
import math


import time, urllib, hmac, hashlib


def generate_nonce():
    return int(round(time.time() * 1000))

# Generates an API signature.
# A signature is HMAC_SHA256(secret, verb + path + nonce + data), hex encoded.
# Verb must be uppercased, url is relative, nonce must be an increasing 64-bit integer
# and the data, if present, must be JSON without whitespace between keys.
#
# For example, in psuedocode (and in real code below):
#
# verb=POST
# url=/api/v1/order
# nonce=1416993995705
# data={"symbol":"XBTZ14","quantity":1,"price":395.01}
# signature = HEX(HMAC_SHA256(secret, 'POST/api/v1/order1416993995705{"symbol":"XBTZ14","quantity":1,"price":395.01}'))
def generate_signature(secret, verb, url, nonce, data):
    """Generate a request signature compatible with BitMEX."""
    # Parse the url so we can remove the base and extract just the path.
    parsedURL = urllib.parse.urlparse(url)
    path = parsedURL.path
    if parsedURL.query:
        path = path + '?' + parsedURL.query

    # print "Computing HMAC: %s" % verb + path + str(nonce) + data
    message = (verb + path + str(nonce) + data).encode('utf-8')

    signature = hmac.new(secret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()
    return signature


def cn2key(my_list):
    key=""
    for i in my_list:
        key+=str(i)+"_"
        
    return key


#dir(keys)

class DummyLogger:
    
    def debug(self,message):
        pass
        #print("DummyLogger_debug:",message)

    def error(self,message):
        pass
        #print("DummyLogger_error:",message)




class BitmexWebsocket:
    
    MAX_TABLE_LEN = 200
    
    def __init__(self):
        self.endpoint = "https://www.bitmex.com/realtime"
        self.symbol="XBTUSD"
        
        #self.logger = logging.getLogger(__name__)
        self.logger = DummyLogger()
        self.logger.debug("Initializing WebSocket.")
        self.wsURL = self.__get_url()
        self.logger.debug(self.wsURL)    
        self.keys={}
        self.data={}
        self.timer={}
        
        self.aa=pd.DataFrame()
        self.bb=pd.DataFrame()
        
        self.__connect(self.wsURL, self.symbol)
        
        self.__wait_for_symbol(self.symbol)
        
    def reindex_dataframe(self,df ,keys):
        test = 'reindex'
        start = time.time()
        if keys==[]:
            return df
        df["newkeys"] = [cn2key(a) for a in df[keys].values]
            
        
        if test not in self.timer:
            self.timer[test]=[0,0]
        self.timer[test][0] += time.time() - start
        self.timer[test][1] +=1
        test="reindex2"
        start = time.time()
        #print(test,3)
        df.set_index('newkeys',inplace=True)
        #df2=df.set_index(keys)
        #print(df)
        #print(test,4)
        if test not in self.timer:
            self.timer[test]=[0,0]
            
        self.timer[test][0] += time.time() - start
        self.timer[test][1] +=1
        #print(test,5)
        return df

    def __get_url(self):
        symbolSubs = ["execution", "instrument", "order", "orderBookL2", "position", "quote", "trade"]
        genericSubs = ["margin"]

        subscriptions = [sub + ':' + self.symbol for sub in symbolSubs]
        #subscriptions = [sub + ':' + "BTC/USD" for sub in symbolSubs]
        subscriptions += genericSubs

        urlParts = list(urllib.parse.urlparse(self.endpoint))
        urlParts[0] = urlParts[0].replace('http', 'ws')
        urlParts[2] = "/realtime?subscribe={}".format(','.join(subscriptions))
        #print(urlParts)
        return urllib.parse.urlunparse(urlParts)

    def exit(self):
        '''Call this to exit - will close websocket.'''
        self.logger.debug("close")
        self.exited = True
        self.ws.close()
        
        
    def market_depth(self):
        while 'orderBookL2' not in self.data:
            time.sleep(0.05)
        return self.data['orderBookL2']

    def get_data(self):
        return self.data
    
    def get_instrument(self):
        '''Get the raw instrument data for this symbol.'''
        # Turn the 'tickSize' into 'tickLog' for use in rounding
        instrument = self.data['instrument'].head()
        instrument['tickLog'] = int(math.fabs(math.log10(instrument['tickSize'])))
        return instrument
    
    def reset_market_depth(self):
        #self.data['orderBookL2'] =pd.DataFrame()
        self.__send_command("unsubscribe", "orderBookL2:"+self.symbol)
        time.sleep(0.1)
        del self.data['orderBookL2']
        self.__send_command("subscribe", "orderBookL2:"+self.symbol)
       
    def get_ticker(self):
        '''Return a ticker object. Generated from quote and trade.'''
        lastQuote = self.data['quote'][-1:]
        lastTrade = self.data['trade'][-1:]
        ticker = {
            "last": lastTrade['price'].get_values()[0],
            "buy": lastQuote['bidPrice'].get_values()[0],
            "sell": lastQuote['askPrice'].get_values()[0],
            "mid": (float(lastQuote['bidPrice'].get_values()[0] or 0) + float(lastQuote['askPrice'].get_values()[0] or 0)) / 2
        }

        # The instrument has a tickSize. Use it to round values.
        #instrument = self.get_instrument()
        return {k: round(float(v or 0), 1) for k, v in ticker.items()}

    
    def __wait_for_symbol(self, symbol):
        '''On subscribe, this data will come down. Wait for it.'''
        while not {'instrument', 'trade', 'quote'} <= set(self.data):
            #print(set(self.data))
            time.sleep(0.05)
            
            
    def __send_command(self, command, args=None):
        '''Send a raw command.'''
        if args is None:
            args = []
        self.ws.send(json.dumps({"op": command, "args": args}))
    
    
    
    
    def __connect(self,wsURL,symbol):
        self.logger.debug("start connect")
        
        self.ws = websocket.WebSocketApp(
            wsURL,on_message=self.__on_message,
            on_close=self.__on_close,
            on_open=self.__on_open,
            on_error=self.__on_error
            #header=self.__get_auth()
        )
        #self.ws.run_forever()
        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()
        self.logger.debug("Started thread")
        
    def __on_message(self,ws, message):
        #self.logger.debug(message)
        message = json.loads(message)
        #self.logger.debug(message)
        #table=message['table']
        table  = message['table'] if 'table' in message else None
        action = message['action'] if 'action' in message else None
        if table == None :
            return 
        if table =='instrument':
            self.logger.debug({action:table})
        
        start = time.time()
        
        try:
            if action not in  self.timer:
                self.timer[action] = [0,0]
            
            if action=='partial':
                self.logger.debug({action:table,"lin":1})
                print({action:table,"lin":1})
                if table not in self.keys:
                    self.keys[table]=message['keys']
                    
                df = self.reindex_dataframe(pd.DataFrame(message['data']),message['keys'])
                self.data[table] =  pd.concat([self.data[table],df]) if table in self.data else df

            elif action == 'update' :
                if table in self.data:
                    df = self.reindex_dataframe(pd.DataFrame(message['data']),self.keys[table])
                    #self.data[table].update(df)
                    for dd in df.index:
                        for col in df.columns:
                            if col not in self.keys[table] and col!="newkey":
                                #print(p2.at[dd ,col])
                                self.data[table].at[dd ,col] = df.at[dd,col]
                                #print(p2.at[dd ,col])
#                 self.data[table].update(df)
                
                

            elif action == 'insert' :
                if table not in self.keys:
                    self.keys[table]=message['keys']
                #self.logger.debug({action:table})
                df = self.reindex_dataframe(pd.DataFrame(message['data']),self.keys[table])
                self.data[table] =  pd.concat([self.data[table],df])
                #self.data[table] =  pd.concat([self.data[table],df]) if table in self.data else df
                
                if table not in ['order','orderBookL2'] and len(self.data[table]) > BitmexWebsocket.MAX_TABLE_LEN:
                    self.data[table] = self.data[table][-1 * BitmexWebsocket.MAX_TABLE_LEN:]


            elif action=='delete':
                if table!='orderBookL2' and table in self.data:
                    #self.logger.debug({action:table})
                    df = self.reindex_dataframe(pd.DataFrame(message['data']),self.keys[table])
                    self.data[table] =  self.data[table].drop(df.index.get_values())
                
            else:
                raise Exception("Unknown action: %s" % action)
            
            
            self.timer[action][0] += time.time() - start
            self.timer[action][1] +=1
            
            

        except KeyError:
            self.logger.error("key error on messsage")
                
                                             
    def __on_error(self,ws, error):
        self.logger.error(error)

    def __on_close(self,ws):
        self.logger.debug("### closed ###")

    def __on_open(self,ws):
        self.logger.debug("### open ###")

        