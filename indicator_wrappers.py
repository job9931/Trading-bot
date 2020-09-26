import talib


'''This file contains wrappers for various indicators from TA-Lib, to enable
instantiation of multiple indicators with different parameter values.'''




'''MOVING AVERAGES: many available in TA-Lib so far only define wrappers for:
                    i) Simple moving average
                    ii)Exponential moving average
'''

'''Simple moving average wrapper class'''
class SMA:
    
    def __init__(self,period):
        self.period = period #integer
    
    def __call__(self,close):
        return talib.SMA(close, self.period)

'''Exponential moving average wrapper class'''
class EMA:
    
    def __init__(self,period):
        self.period = period #integer
    
    def __call__(self,close):
        return talib.EMA(close, self.period)



'''MOMENTUM INDICATORS: many available in TA-Lib so far only define wrappers for:
                    i) Relative strength index'''

'''Relative strength index wrapper class'''
class RSI:

    def __init__(self,period):
        self.period = period #integer
    
    def __call__(self,close):
        return talib.RSI(close, self.period)
        
        
'''CANDLESTICK PATTERNS: almost all candlestick pattern recognition functions
do not take any parameters, so no need to wrap them.'''

    