import config
import indicator_wrappers as iw
import alpaca_trade_api as trade_api 
import talib
import json
import websocket
import numpy as np
import pandas as pd


'''
This file contains functions and classes to implement a simple RSI-based trading strategy.
The strategy only takes single, long positions, executed by a OTO order, once the RSI is less
than a chosen oversold threshold and sells using a limit order, once the RSI is greater
than a chosen overbought threshold.

Note: this strategy is very simple and the primary use is to show that the automated trading system works.  

Contents:
    i)   Functions to interact with the Alpaca API, such as to get account info and make orders.
    ii)  Functions to calculate order quantities based on a chosen stop loss and risk. 
    iii) Class to create functions which are used to build an array of price data and calculate the RSI.
    iv)  Class to create functions used to perform trading logic. 
'''




'''Trading Functions for Alpaca API'''
def get_account():
    return  api.get_account()

def list_orders(status=None, limit=None, after=None, until=None, direction=None, nested=None):
    return api.list_orders(status,limit,after,until,direction,nested)

def oto_buy(symbol,qty,side,order_type,time_in_force,order_class,stop_loss):

    try:
        order = api.submit_order(symbol,qty,side,order_type,time_in_force,order_class,stop_loss)
        print(order)
    except Exception as e:
        return False
    
    return True

def limit_sell(symbol,limit_price,qty,side,order_type,time_in_force):
    
    try:
        order = api.submit_order(symbol,limit_price,qty,side,order_type,time_in_force,limit_price)
        print(order)
    except Exception as e:
        return False
    return True


'''Utility functions'''
def round_down(n):
    '''Used to round order size down to the closest
    multiple of a power of , e.g round_down(12)=10
    and round_down(234)=200'''
    
    def order_magnitude(number):
        return math.floor(math.log(number, 10))
        
    order = order_magnitude(n)
    return (10**order)*math.floor((10**(-1*order)*n))
    
    

def order_size(buy_price,stop_loss,risk=0.01):
    '''This calculates an order size based upon the percentage of
    the account willing to risk (1% default) and a chosen DECIMAL stop-loss.'''
    
    acc = get_account() #get latest account info
    acc_cash = float(acc.cash) #extract cash amount 
    account_cash_risk = risk*acc_cash #percentage of current cash willing to risk, 1% by default
    trade_cash_risk = buy_price-buy_price*(1-stop_loss) #cash risk of trade (difference between buy price and stop loss price)
    number_of_shares = account_cash_risk/trade_cash_risk #number of shares you can buy risking 1% of account for given stop-loss
    cost_of_shares = buy_price*number_of_shares #calculate cost of order
    
    if cost_of_shares>acc_cash: #if cost of transaction is more than available in cash, reduce order size so no need for leverage
        excess = cost_of_shares-acc_cash #how much more cost is than what we have in cash, the excess
        excess_shares = excess/buy_price #how many shares we buy according with the excess
        number_of_shares = number_of_shares-excess_shares #reduce the number of shares so we are within cash limit.
        return round_down(number_of_shares)#round down to closest multiple of power of 10.
    
    return round_down(number_of_shares)#round down to closest multiple of power of 10.
        

class BuildData:

    def __init__(self,period)
        self.period = period
        
    def __call__(self,message):
        '''Stores open, high, low, close, average, volume, vwap and RSI over chosen time period
        It then updates the global variable price_history (no need to have return statement).'''
        
        
        global price_history #set price_history to be a global variable
        message = eval(message) #convert message from string to dictionary
        n_cols = 8 #7 columns to store o,h,l,c,a,v,vw, +1 for rsi column
        price_data = np.zeros(n_cols) #initialise NumPy array to store prices and indicators
        data = message['data'] #data is a dictionary extracted from the message
        price_data[0:6] = data['o'],data['h'],data['l'],data['c'],data['a'],data['v'],data['vw'] #open,high,low,close,average,volume,VWAP
        
        rsi = iw.RSI(self.period) #instantiate RSI function, default period 14
        price_data[7] = rsi(data['c'])#calculate rsi from closing prices and store in final column 
        
        if price_history.size==0:
            price_history = price_data #overwrite empty array after receiving the first price data.
        else:
            price_history = np.vstack([price_data,price_history]) #latest price on top of stack


class TradingRules:

    def __init__(self,symbol,oversold,overbought,stop_loss):
        self.symbol = symbol
        self.oversold = oversold
        self.overbought = overbought
        self.stop_loss = stop_loss #in decimal form i.e. 0.02 instead of 2%

    def __call__(self,price_history): 
   
        rsi = price_history[0,7] # row 0 column 7
        last_close = price_history [0,3] #row0 column 3
        
        if rsi == np.nan:
            pass #do nothing if we have no rsi data yet
        
        else:
            if rsi<self.oversold: #check if oversold
                if not in_trade: #then check if we are position
                    print('Oversold! Buy!')
                    buy_qty = order_size(last_close,self.stop_loss)#calculate quantity to buy
                    if buy_qty<1:#check we have integer quantity 
                        print('Not enough cash to buy at least 1 unit.')
                        
                    order_succeeded = oto_buy(self.symbol,buy_qty,'buy','market','day','oto',
                    {'stop_price': last_close*(1-self.stop_loss),
                    'limit_price':last_close*(1-self.stop_loss)}) #execute an one-triggers-other order to automatically set stop-loss
   
                    if order_succeeded:
                        in_trade=True 

                else:
                    pass #overbought but already in a position
            
            if rsi>self.overbought: #check if overbought
                if in_trade: #then check if we are position
                    print('Overbought! Sell!')
                    sell_qty = buy_qty #set sell quantity to the buy quantity, so we sell all assets
                    order_succeeded = limit_sell(self.symbol,last_close,sell_qty,'sell','limit',time_in_force='day') #sell with limit order on last closing price
                    if order_succeeded:
                        in_trade = False
                                           
                else:
                    pass #No stock to sell since not currently in a position
                    
        
        