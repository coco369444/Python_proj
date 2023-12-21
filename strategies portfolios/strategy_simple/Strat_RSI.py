# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 18:56:13 2023

@author: corentin
"""


import pandas as pd
import numpy as np
from scipy.stats import linregress
import matplotlib.pyplot as plt


df = pd.read_csv("BTC_data.csv")

window = 14

# Function to calculate RSI
def compute_RSI(data, window=window):
    diff = data.diff(1).dropna()
    gain = (diff.where(diff > 0, 0)).sum() / window
    loss = (-diff.where(diff < 0, 0)).sum() / window
    RS = gain / loss
    return 100 - (100 / (1 + RS))

# Function to calculate MACD
def compute_MACD(data, span1=13, span2=26, span3=3):
    exp1 = data.ewm(span=span1, adjust=False).mean()
    exp2 = data.ewm(span=span2, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=span3, adjust=False).mean()
    return macd, signal


df['RSI'] = df[['Close']].rolling(window+1).apply(compute_RSI)
macd, signal = compute_MACD(df['Close'])
df['MACD'] = macd
df['Signal'] = signal
df['MACD_Crossover'] = df['MACD'] > df['Signal']

df['Buy_Signal'] = (df['RSI'] < 30) & (df['MACD_Crossover'].shift(1) == False) & (df['MACD_Crossover'] == True)
df['Sell_Signal'] = (df['RSI'] > 70) & (df['MACD_Crossover'].shift(1) == True) & (df['MACD_Crossover'] == False)


# Plotting example for MSFT
plt.figure(figsize=(12,7))
plt.subplot(2,1,1)
plt.plot(df['Close'], label='BTC Price')
plt.plot(df[df['Buy_Signal']]['Close'], 'g^', label='Buy Signal', markersize=10)
plt.plot(df[df['Sell_Signal']]['Close'], 'rv', label='Sell Signal', markersize=10)
plt.title('BTC Buy and Sell Signals')
plt.legend()

plt.subplot(2,1,2)
plt.plot(df['RSI'], label='RSI')
plt.axhline(30, color='green', linestyle='--')
plt.axhline(70, color='red', linestyle='--')
plt.title('BTC RSI')
plt.legend()
plt.tight_layout()
plt.show()

df = df.set_index("Timestamp")

trades = pd.DataFrame(columns=['Buy_Date', 'Sell_Date', 'Buy_Price', 'Sell_Price', 'Profit'])

# Tracking variables
in_position = False
buy_price = 0
stop_loss = 0
sl=0.98


# Iterate through MSFT data for trading signals
for index, row in df.iterrows():
    if row['Buy_Signal'] and not in_position:
        buy_price = row['Close']
        stop_loss = buy_price * sl
        in_position = True
        buy_date = index
    elif in_position:
        
        if row['Sell_Signal']:
            sell_price = row['Close']
            profit = sell_price - buy_price
            in_position = False
            sell_date = index
            # Record the trade
            trade = pd.DataFrame.from_dict({'Buy_Date': [buy_date], 'Sell_Date': [sell_date],
                                    'Buy_Price': [buy_price], 'Sell_Price': [sell_price], 
                                    'Profit': [profit]})
            trades = pd.concat((trades,trade),axis=0)
            
        elif row['Close'] <= stop_loss:
            sell_price = row['Close']
            profit = sell_price - buy_price
            in_position = False
            sell_date = index
            # Record the trade
            trade = pd.DataFrame.from_dict({'Buy_Date': [buy_date], 'Sell_Date': [sell_date],
                                    'Buy_Price': [buy_price], 'Sell_Price': [sell_price], 
                                    'Profit': [profit]})
            trades = pd.concat((trades,trade),axis=0)
            
    if row['Close']*sl>stop_loss and in_position:
        stop_loss=row['Close']

# Calculate total performance
total_profit = trades['Profit'].sum()
total_return_percentage = (total_profit / trades['Buy_Price'].sum()) * 100

print("Total Profit: ", total_profit)
print("Total Return Percentage: ", total_return_percentage, "%")
print(trades)
