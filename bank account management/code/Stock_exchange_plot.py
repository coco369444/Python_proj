# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 09:57:28 2022

@author: corentin
"""
import pandas as pd
import numpy as np
import yfinance as yf
import datetime 


#path_source = r"C:\Users\cbour\OneDrive\Bureau\Python proj\Python_proj\bank account management\data"
path_source = r"G:\Python Github\Python_proj\bank account management\data"

data = pd.read_excel((path_source+r"\JB_stock_exchange.xlsx").replace("\\","/"))

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
change_date = np.unique(data["Date"].values)
#change_date=change_date.astype('datetime64[D]')
change_date=np.append(change_date,np.datetime64('today'))

strat_ret=pd.DataFrame()
first_date=change_date[0]
for date in change_date[1:]:
    assets = data.loc[data["Date"]<date][["Ticker","Quantity"]]
    assets = assets.groupby(by=["Ticker"]).sum()
    
    df_hist = df_histo_price.loc[(df_histo_price.index<=date) & (df_histo_price.index>=first_date)]
    if len(df_hist)>1:
        price_d =pd.DataFrame()
        for a in assets.index:
            price_a = df_hist[a]*assets.loc[a].values
            price_d[a]=price_a
        price_d.fillna(method="bfill",inplace=True)
        price_d.dropna(inplace=True)
        total = price_d.sum(axis=1)
        ret_d=total.pct_change(1)
        ret_d.dropna(inplace=True)
        w = (price_d.iloc[-1]/total[-1]).T
        strat_ret=pd.concat((strat_ret,ret_d))
    first_date=date
    
    
perf=(1+strat_ret).cumprod()


price_replace = df_histo_price.fillna(method="bfill")
ret_total = price_replace.pct_change(1)
ret_total.dropna(inplace=True)
ret_w=(ret_total*w).sum(axis=1)

perf_w=(1+ret_w).cumprod()

ret_w.mean()*250
ret_w.std()*np.sqrt(250)

ret_w.mean()*250/(ret_w.std()*np.sqrt(250))
