#戦略クラスを作成
#static
#戦略クラスを作成
#static
class IStatic:
    
    BUY=1
    SELL=-1
    NONE=0
    
    
    #def __init__(self):
        #self.candle = candle
        
    def judge(self):
        return (False ,"")
    
class Sma_Static(IStatic):
    
    def __init__(self,short_term=15,long_term=50):
        self.__short_term=short_term
        self.__long_term=long_term
    
    def sma(self,candle_stick ,n,start=1):
        
        if start == 0:
            from_index = -1 *start
            to_index   = -1 * n
            check = candle_stick[to_index:]
        else:
            from_index = -1 *start
            to_index   = -1 * (n+start)
        
            check = candle_stick[to_index:from_index]
        
        #print(from_index,to_index ,len(check))
        if len(check) == 0 :
            return 0
        
        return check.sum()/len(check)
    
    
    def judge(self, ohlcv,start=1):
        sma_short_b = (0, self.sma(ohlcv.close, self.__short_term , start + 1))
        sma_short_a = (1, self.sma(ohlcv.close, self.__short_term , start ))
        sma_long_b  = (0, self.sma(ohlcv.close, self.__long_term , start + 1))
        sma_long_a  = (1, self.sma(ohlcv.close, self.__long_term , start ))
        self.juge_log = " SMA_SHORT_B:"+str(sma_short_b[1])+  " SMA_SHORT_A:"+str(sma_short_a[1])+ " SMA_LONG_B:"+str(sma_long_b[1])+  " SMA_LONG_A:"+str(sma_long_a[1])
        res1 = self.line_eq( (sma_short_b,sma_short_a) , (sma_long_b,sma_long_a)  )
        res2 = self.line_eq( (sma_long_b,sma_long_a)  , (sma_short_b,sma_short_a) )
        
        is_cross =  res1 and res2
        
        
        #tes
        if is_cross and sma_short_a >= sma_long_a:
            return (self.BUY,self.juge_log )
        if is_cross and sma_short_a < sma_long_a:
            return (self.SELL,self.juge_log )
        
        return (self.NONE,self.juge_log )

    def line_eq(self,cros1, cros2):
        a,b = cros1
        c,d = cros2
        ax,ay=a
        bx,by=b
        cx,cy=c
        dx,dy=d
        tc=(ax-bx)*(cy-ay)+(ay-by)*(ax-cx)
        td=(ax-bx)*(dy-ay)+(ay-by)*(ax-dx)
        if td*tc < 0:
            return True
        else:
            return False
        
        
        