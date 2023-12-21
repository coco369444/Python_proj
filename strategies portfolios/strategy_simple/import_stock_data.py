# -*- coding: utf-8 -*-
"""
Created on Sun Nov 26 12:35:37 2023

@author: corentin
"""

import pandas as pd
import numpy as np
import yfinance as yf


# Define the tickers
snp500_ticker = "^GSPC"  # Ticker for S&P 500
msft_ticker = "MSFT"     # Ticker for Microsoft


start_date= "2020-01-01"
end_date="2023-11-01"


def get_data_yfinance(ticker,start_date,end_date):
    
    df = yf.download(ticker, start=start_date, end=end_date)
    return df


snp500_data=get_data_yfinance(snp500_ticker,start_date,end_date)
msft_data=get_data_yfinance(msft_ticker,start_date,end_date)

snp500_data.to_csv("snp500_data.csv")
msft_data.to_csv("msft_data.csv")


import ccxt
import datetime
import pandas as pd

def fetch_historical_data(exchange, symbol, timeframe, start_date, end_date):
    data = []
    while start_date < end_date:
        print(f"Fetching data from {datetime.datetime.utcfromtimestamp(start_date / 1000)}")
        new_data = exchange.fetch_ohlcv(symbol, timeframe, since=start_date)
        if not new_data or new_data[-1][0] == start_date:
            break
        data += new_data
        start_date = new_data[-1][0]
    return data

# Initialize the exchange
exchange = ccxt.binance()

# Define the symbol and the time frame
symbol = 'BTC/USDT'
timeframe = '1h'

# Calculate the start and end timestamps
end_date = exchange.milliseconds()
start_date = end_date - int(3 * 365 * 24 * 60 * 60 * 1000)  # 2 years in milliseconds

# Fetch the historical data
btc_data = fetch_historical_data(exchange, symbol, timeframe, start_date, end_date)

# Convert to a DataFrame
df = pd.DataFrame(btc_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')

df.to_csv("BTC_data.csv",index=False)

