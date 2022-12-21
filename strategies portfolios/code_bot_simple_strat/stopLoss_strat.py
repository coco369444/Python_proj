# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 20:32:15 2022

@author: corentin
"""
import pandas as pd
import numpy as np

from binance import Client
client=Client()

def getdailydata(symbol):
    frame = pd.DataFrame(client.get_historical_klines(symbol,"1m","3 week ago UTC"))
    frame=frame[[0,1,2,3,4,5,8]]
    frame.columns=["Timestamp","Open","High","Low","Close","Volume","Number of trades"]
    frame.set_index(frame.columns[0],inplace=True)
    frame=frame.astype(float)
    frame.index = pd.to_datetime(frame.index, unit='ms')
    return frame
 
data_ada=getdailydata("XRPUSDT")

df_price_ada = data_ada["Close"]

df_price_ada.plot()

def buy_sell(t,df,limit=0.05):
    buy_price =df.iloc[t]
    bench = df.iloc[t]
    stop_limit = bench*(1-limit)
    price=buy_price
    
    while price>stop_limit and t<len(df)-1:
        t+=1
        price = df.iloc[t]
        
        if price > bench:
            bench=price
            stop_limit = bench*(1-limit)
    
    sell_price = df.iloc[t+1] #suppose we sell after reaching the threesold
    profit = sell_price-buy_price
    print(profit)
    print(profit/buy_price)
    
    return t,buy_price,sell_price


buy_sell(0,df_price_ada,limit=0.08)
            
        
        
        
