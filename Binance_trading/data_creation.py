# -*- coding: utf-8 -*-
"""
Created on Thu Apr  6 21:06:06 2023

@author: corentin
"""

import requests
import pandas as pd

from ta.volume import OnBalanceVolumeIndicator
from ta.momentum import PercentagePriceOscillator
from ta.volume import ChaikinMoneyFlowIndicator

url = 'https://api.binance.com/api/v3/klines'
interval = '2h'
start_time = pd.Timestamp("now") - pd.Timedelta(days=3*365)
end_time = pd.Timestamp("now")
df_list = []
old_start_time=end_time

while old_start_time != start_time:

    params = {'symbol': 'ETHUSDT', 'interval': interval, 'startTime': int(start_time.timestamp() * 1000),
              'endTime': int(end_time.timestamp() * 1000)}
    
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                     'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                                     'Taker buy quote asset volume', 'Ignore'])
    df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')
    df.set_index('Open time', inplace=True)
    df_list.append(df)
    old_start_time = start_time
    start_time = df.index.max()
    print(start_time)

df = pd.concat(df_list[::-1]).drop_duplicates()

path = r"G:\Python Github\Python_proj\Binance_trading"

df.to_csv(path+"/history_base_eth.csv")

df_source = pd.read_csv(path+"/history_base_eth.csv",index_col=0)

df_source = df.copy()

df=df_source[["Close","High","Low","Volume"]].astype(float)
df = df.sort_index()

# Calculer les indicateurs de marché
df['MA_20'] = df['Close'].rolling(20).mean().shift(1)
df['MA_50'] = df['Close'].rolling(50).mean().shift(1)

delta = df['Close'].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
ema_gain = gain.ewm(alpha=1/14).mean().shift(1)
ema_loss = loss.ewm(alpha=1/14).mean().shift(1)
rs = ema_gain / ema_loss.abs()
df['RSI'] = 100 - (100 / (1 + rs))

df['MA_20'] = df['Close'].rolling(20).mean().shift(1)
df['std_20'] = df['Close'].rolling(20).std().shift(1)
df['upper_band'] = df['MA_20'] + 2 * df['std_20']
df['lower_band'] = df['MA_20'] - 2 * df['std_20']

df['Momentum_1'] = df['Close'].diff(1).shift(1)
df['Momentum_7'] = df['Close'].diff(7).shift(1)


# Calculer les indicateurs de volume
obv = OnBalanceVolumeIndicator(df['Close'].shift(1), df['Volume'].shift(1))
df['OBV'] = obv.on_balance_volume()

# Calculer les indicateurs de momentum
ppo = PercentagePriceOscillator(df['Close'].shift(1), window_slow=26, window_fast=12)
df['PPO'] = ppo.ppo().shift(1)

cmf = ChaikinMoneyFlowIndicator(df['High'].shift(1), df['Low'].shift(1), df['Close'].shift(1), df['Volume'].shift(1))
df['CMF'] = cmf.chaikin_money_flow().shift(1)

#df['OsMA'] = ppo.osma().shift(1)
