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
from ta.momentum import RSIIndicator, StochasticOscillator

import ta
import numpy as np


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

#path = r"G:\Python Github\Python_proj\Binance_trading"
path = r"C:\Users\cbour\OneDrive\Bureau\Python proj\Python_proj\Binance_trading"

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

# Calculer les rendements
returns = np.log(df['Close'] / df['Close'].shift(1))
df["return"]=returns.shift(1)

# Calculer les indicateurs de marché
df['ret_MA_10'] = returns.rolling(10).mean().shift(1)
df['ret_MA_20'] = returns.rolling(20).mean().shift(1)
df['ret_MA_50'] = returns.rolling(50).mean().shift(1)
df['ret_std_10'] = returns.rolling(10).std().shift(1)
df['ret_std_20'] = returns.rolling(20).std().shift(1)
df['ret_std_50'] = returns.rolling(50).std().shift(1)


# Calculer les indicateurs RSI, Stochastique et MACD
rsi = RSIIndicator(close=returns, window=14)
df['RSI'] = rsi.rsi()

stoch = StochasticOscillator(high=returns, low=returns, close=returns, window=14, smooth_window=3)
df['%K'] = stoch.stoch()

# Calculer le MACD avec TA-Lib
#df['macd'], df['macdsignal'], df['macdhist'] = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span = fast, adjust = False).mean()
    exp2 = price.ewm(span = slow, adjust = False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns = {'Close':'macd'})
    signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'macd_signal'})
    
    hist = pd.DataFrame(macd['macd'] - signal['macd_signal']).rename(columns = {0:'macd_hist'})
    frames =  (macd, signal, hist)
    print(frames)
    df = pd.concat(frames, axis = 1)
    return df

macd_df = get_macd(df['Close'], slow=26, fast=12, smooth=9).shift(1)
df=pd.concat((df,macd_df),axis=1)



df['label'] = (1+returns).rolling(10).apply(np.prod, raw=True).shift(-10)-1

# Supprimer les lignes qui contiennent des valeurs NaN


df_seleced = df[[ 'RSI','Momentum_1', 'Momentum_7', 'OBV', 'PPO',
       'CMF', 'return', 'ret_MA_10', 'ret_MA_20', 'ret_MA_50', 'ret_std_10',
       'ret_std_20', 'ret_std_50', '%K', 'macd', 'macd_signal', 'macd_hist','label'
       ]]

df_seleced.dropna(inplace=True)

X = df_seleced[[ 'RSI','Momentum_1', 'Momentum_7', 'OBV', 'PPO',
       'CMF', 'return', 'ret_MA_10', 'ret_MA_20', 'ret_MA_50', 'ret_std_10',
       'ret_std_20', 'ret_std_50', '%K', 'macd', 'macd_signal', 'macd_hist'
       ]]
Y_ret = df_seleced["label"]

Y_buy = Y_ret > 0.01
Y_sell=Y_ret <0


import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score

# Diviser les données en ensembles d'entraînement et de test en tenant compte de la temporalité
split_index = int(len(X) * 0.8)  # 80% des données pour l'entraînement, 20% pour les tests
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = Y_buy[:split_index], Y_buy[split_index:]

# Créer un dataset LightGBM à partir des données d'entraînement
train_data = lgb.Dataset(X_train, label=y_train)
# Définir les paramètres du modèle LightGBM
params = {
    'objective': 'binary',
    'metric': 'binary_logloss',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': 0
}
# Entraîner le modèle LightGBM
model_buy = lgb.train(params, train_data, num_boost_round=1000)

# Faire des prédictions sur l'ensemble de test
y_pred = model_buy.predict(X_test)
y_pred = np.round(y_pred)  # Convertir les prédictions en valeurs binaires (0 ou 1)

# Évaluer la précision du modèle
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
print("Precision:", precision_score(y_test, y_pred))
print("Recall:", recall_score(y_test, y_pred))






