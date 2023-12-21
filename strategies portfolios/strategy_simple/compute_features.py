# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 13:22:19 2023

@author: corentin
"""

import pandas as pd
import numpy as np
from scipy.stats import linregress

# msft_data = pd.read_csv("msft_data.csv")

msft_data =pd.read_csv("BTC_data.csv")

# Calculate returns
msft_returns = msft_data['Close'].pct_change()
# market_returns = market_data['Close'].pct_change()

# 1. Beta
# covariance = msft_returns.cov(market_returns)
# variance = market_returns.var()
# beta = covariance / variance

# 2. Moving Averages
msft_data['SMA_20'] = msft_data['Close'].rolling(window=20).mean()
msft_data['EMA_20'] = msft_data['Close'].ewm(span=20, adjust=False).mean()

# 3. MACD
msft_data['MACD'] = msft_data['Close'].ewm(span=12, adjust=False).mean() - msft_data['Close'].ewm(span=26, adjust=False).mean()
msft_data['MACD_Signal'] = msft_data['MACD'].ewm(span=9, adjust=False).mean()

# 4. RSI
delta = msft_data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
msft_data['RSI'] = 100 - (100 / (1 + rs))

# 5. Bollinger Bands
msft_data['Middle_BB'] = msft_data['Close'].rolling(window=20).mean()
msft_data['Upper_BB'] = msft_data['Middle_BB'] + 2 * msft_data['Close'].rolling(window=20).std()
msft_data['Lower_BB'] = msft_data['Middle_BB'] - 2 * msft_data['Close'].rolling(window=20).std()

# 6. Standard Deviation
msft_data['STD_20'] = msft_data['Close'].rolling(window=20).std()

# 7. Momentum
msft_data['Momentum'] = msft_data['Close'] - msft_data['Close'].shift(4)

# 8. OBV
msft_data['OBV'] = (np.sign(msft_data['Close'].diff()) * msft_data['Volume']).fillna(0).cumsum()

from compute_features_fonc import hurst_dfa,calculate_hamming_distance

# msft_data=msft_data.dropna()


hurst_exponent=msft_data['Close'].rolling(window=120).apply(lambda x : hurst_dfa(x))

msft_data['Hurst_90'] =hurst_exponent


hamming_score  = msft_data['Close'].rolling(window=120).apply(lambda x : calculate_hamming_distance(x))
msft_data['Hamming_90'] =hamming_score



df_msft_light = msft_data[["Close","Hurst_90","Hamming_90"]].dropna().reset_index(drop=True)
df_msft_light.columns = ["Close","Hurst","Hamming"]


from strategy_hurst_hamming import trading_strategy,evaluate_strategy_performance,evaluate_strategy_performance_fees

df_final = trading_strategy(df_msft_light,hurst_threshold=0.55, hamming_threshold=0.3, stop_loss=0.05)
df_check = df_final.copy()

df_start,perf = evaluate_strategy_performance_fees(df_final.copy())
perf

df_start[["Strategy","Strategy_without_fee","Strat_bench"]].iloc[:500].plot()

# perf_check = evaluate_strategy_performance(df_check)

sl_values = np.round(np.arange(0.01,0.11,0.01),3)
hamming_values = np.round(np.arange(0.2,0.65,0.05),3)

perf_df_fee = pd.DataFrame(columns=sl_values,index=hamming_values)
perf_df_vanilla = pd.DataFrame(columns=sl_values,index=hamming_values)

for sl in sl_values:
    for hamming in hamming_values:
        print(f"stop loss : {sl}")
        print(f"hamming : {hamming}")

        df_final = trading_strategy(df_msft_light,hurst_threshold=0.5, hamming_threshold=hamming, stop_loss=sl)

        _,perf_fee = evaluate_strategy_performance_fees(df_final.copy())
        print(perf_fee)
        print("\n")
        
        _,perf_vanilla = evaluate_strategy_performance(df_final.copy())
        
        perf_df_fee.loc[hamming,sl]=perf_fee["Strategy Cumulative Returns"]
        perf_df_vanilla.loc[hamming,sl]=perf_vanilla["Strategy Cumulative Returns"]

perf_df_fee=perf_df_fee.astype(float)
perf_df_vanilla=perf_df_vanilla.astype(float)


df_final = trading_strategy(df_msft_light,hurst_threshold=0.55, hamming_threshold=0.25, stop_loss=0.08)
df_strat,perf = evaluate_strategy_performance_fees(df_final.copy())
perf

df_strat.index=df_strat.index

df_strat[["Strategy","Strategy_without_fee","Strat_bench"]].plot()
