# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 21:12:46 2023

@author: corentin
"""
import requests
import pandas as pd



import pandas_ta as pd_ta
from ta import volatility
import ta

import numpy as np

path = r"G:\Python Github\Python_proj\Binance_trading"
#path = r"C:\Users\cbour\OneDrive\Bureau\Python proj\Python_proj\Binance_trading"
df_source = pd.read_csv(path+"/history_base_eth.csv",index_col=0)



df=df_source[["Close","High","Low","Volume"]].astype(float)
df = df.sort_index()

# Calculate Moving Averages (SMA, EMA, and WMA)
df['sma20'] = pd_ta.sma(df['Close'], window=20)
df['sma50'] = pd_ta.sma(df['Close'], window=50)
df['ema20'] = pd_ta.ema(df['Close'], window=20)
df['ema50'] = pd_ta.ema(df['Close'], window=50)
df['wma20'] = pd_ta.wma(df['Close'], window=20)
df['wma50'] = pd_ta.wma(df['Close'], window=50)

# Calculate RSI
df['rsi14'] = pd_ta.rsi(df['Close'], window=14)

# Calculate Bollinger Bands

df["bb_hband"] = volatility.bollinger_hband(df["Close"], window=20, window_dev=2)
df["bb_lower"] = volatility.bollinger_lband(df["Close"], window=20, window_dev=2)
# df["bb_mband"] = volatility.bollinger_mband(df["Close"], window=20, window_dev=2)
df['bb_width'] = df['bb_hband'] - df['bb_lower']

# Calculate MACD
df['macd'], df['macd_hist'] ,df['macd_signal'] = pd_ta.macd(df['Close'])

# Calculate Stochastic Oscillator
df['stoch_k'], df['stoch_d'] = pd_ta.stoch(df['High'], df['Low'], df['Close'])

# Calculate Average True Range (ATR)
df['atr'] = pd_ta.atr(df['High'], df['Low'], df['Close'])

# Calculate On-Balance Volume (OBV)
df['obv'] = pd_ta.obv(df['Close'], df['Volume'])

# Calculate Rate of Change (ROC)
df['roc14'] = pd_ta.roc(df['Close'], window=14)

# Calculate Ichimoku Cloud
df['ichimoku_base'], df['ichimoku_conversion'] = ta.ichimoku_base_line(df['High'], df['Low'])
df['ichimoku_lead_a'], df['ichimoku_lead_b'] = ta.ichimoku_a_line(df['High'], df['Low'])
df['ichimoku_span_a'] = (df['ichimoku_base'] + df['ichimoku_conversion']) / 2
df['ichimoku_span_b'] = (df['ichimoku_lead_a'] + df['ichimoku_lead_b']) / 2

# Calculate Fibonacci Retracement Levels
df['fib23.6'] = ta.fibonacci(df['Low'], df['High'], retracement_level=23.6)
df['fib38.2'] = ta.fibonacci(df['Low'], df['High'], retracement_level=38.2)
df['fib50.0'] = ta.fibonacci(df['Low'], df['High'], retracement_level=50.0)
df