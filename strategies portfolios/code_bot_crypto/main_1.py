# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 19:49:42 2022

@author: corentin
"""
import pandas as pd
import numpy as np

import yfinance as yf
import datetime 

from pypfopt import EfficientFrontier, risk_models, expected_returns, plotting

data = pd.read_excel((r"D:\Corentin\Bureau\bank account management\data\JB_stock_exchange.xlsx").replace("\\","/"))

today = datetime.date.today().strftime("%Y-%m-%d")
start_date = (datetime.date.today() - datetime.timedelta(days=10*365)).strftime("%Y-%m-%d")

df_EUR = yf.download("EURUSD=X", start=start_date, end=today)["Adj Close"]

df_histo_price=pd.DataFrame()
for i in range(len(data)):
    df_i = yf.download(data["Ticker"][i], start=start_date, end=today)["Adj Close"]
    if data["Currency"][i]=="EUR":
        df_i=(df_i*df_EUR).dropna()
    
    df_histo_price[data["Ticker"][i]]=df_i

df_histo_price.loc["2021-11-24":"2021-12-06","RUSG.L"]*=0.01


new_prices=df_histo_price.fillna(method="bfill").dropna().iloc[:,:5]
ret = new_prices.pct_change(1).dropna()

mu = expected_returns.mean_historical_return(new_prices,frequency=252)
S = risk_models.sample_cov(new_prices,frequency=252)


#plotting.plot_efficient_frontier(ef, show_assets=True)

#np.diag(ef.cov_matrix)**0.5
ef = EfficientFrontier(mu,S)
weights = ef.max_sharpe()
weights

ef.portfolio_performance(verbose=True)

ef = EfficientFrontier(mu,S)
weights = ef.min_volatility()
weights

ef.portfolio_performance(verbose=True)