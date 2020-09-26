import config
import alpaca_trade_api as trade_api 
import talib
import json
import websocket
import numpy as np
import pandas as pd


'''Global variables'''
BASE_URL = 'https://paper-api.alpaca.markets'
stream_socket = 'wss://data.alpaca.markets/stream'
api = trade_api.REST(config.API_KEY,config.SECRET_KEY,BASE_URL,api_version='v2')

price_history = np.asarray([])#initialialse empty numpy array to store price history



'''Websocket functions'''
def on_open(ws):
    print("opened")
    auth_data = {
        "action": "authenticate",
        "data": {"key_id": config.API_KEY, "secret_key": config.SECRET_KEY}
    }

    ws.send(json.dumps(auth_data))
    listen_message = {"action": "listen", "data": {"streams": ["AM.{}".format(ticker)]}}
    ws.send(json.dumps(listen_message))

def on_message(ws, message): #we build logic into this function
    print("received a message")
    build_data(message) #update price data 
    trading_rules(price_history) #apply trading logic to latest price data

def on_close(ws):
    print("closed connection")



'''Main Program'''
if __name__ == '__main__':
    ticker = 'TSLA' #select ticker symbol to trade
    in_trade = False #initialise flag to signal if program is in trade or not
    build_data = rsi_strategy.BuildData(period=14)#instantiate function to build data set with 14-day RSI column
    trading_rules = rsi_strategy.TradingRules(symbol=ticker,oversold=30,overbought=70,stop_loss=0.01) #nstantiat function of trading tules from RSI strategy
    ws = websocket.WebSocketApp(stream_socket, on_open=on_open, on_message=on_message, on_close=on_close)
    ws.run_forever()

exit()
